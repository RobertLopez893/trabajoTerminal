package com.example.animoon.ui.admin

import android.content.Context
import com.example.animoon.data.network.AdminAppealResolveRequest
import com.example.animoon.data.network.ApiClient
import org.json.JSONObject

enum class AdminAppealStatus {
    PENDING,
    IN_REVIEW,
    APPROVED,
    REJECTED;

    val label: String
        get() = when (this) {
            PENDING -> "Pendiente"
            IN_REVIEW -> "En revisión"
            APPROVED -> "Aprobada"
            REJECTED -> "Rechazada"
        }

    val isResolved: Boolean
        get() = this == APPROVED || this == REJECTED
}

data class AdminAppeal(
    val id: String,
    val nickname: String,
    val date: String,
    val incident: String,
    val explanation: String,
    val evidence: String,
    val status: AdminAppealStatus = AdminAppealStatus.PENDING,
    val resolution: String = "",
    val resolvedAt: Long = 0L,
    val resolvedBy: String = ""
)

/**
 * Sesión administrativa de Animoon.
 * Almacena el token JWT expedido por el backend.
 */
object AdminDemoSession {

    const val USERNAME = "admin.animoon"
    private const val PASSWORD = "AdminDemo#2026"

    var isActive = false
        private set

    var adminToken: String? = null
        private set

    fun login(username: String, password: String, token: String = ""): Boolean {
        isActive = username == USERNAME && (password == PASSWORD || token.isNotBlank())
        adminToken = if (token.isNotBlank()) token else "LOCAL_ADMIN_TOKEN"
        return isActive
    }

    fun logout() {
        isActive = false
        adminToken = null
    }
}

class AdminDemoRepository(context: Context) {

    private val preferences = context.applicationContext
        .getSharedPreferences(
            "animoon_admin_appeals_demo",
            Context.MODE_PRIVATE
        )

    private val samples = listOf(
        AdminAppeal(
            id = "AP-DEMO-003",
            nickname = "CometaAzul",
            date = "20 de octubre de 2026 · 16:40",
            incident = "Solicitud de información personal",
            explanation =
                "Creo que se interpretó mal mi pregunta. " +
                        "Quisiera que revisaran el contexto de la conversación.",
            evidence = """
                Conversación registrada

                16:35 · CometaAzul:
                ¿En qué escuela estás?

                16:36 · Jugador de muestra:
                Prefiero no compartir esa información.

                16:36 · CometaAzul:
                Está bien, podemos seguir con el juego.
            """.trimIndent()
        ),
        AdminAppeal(
            id = "AP-DEMO-002",
            nickname = "ZorroEstelar",
            date = "19 de octubre de 2026 · 18:20",
            incident = "Invitación a una conversación externa",
            explanation =
                "Quiero explicar lo que ocurrió antes de que se " +
                        "suspendiera mi cuenta y solicitar una revisión.",
            evidence = """
                Conversación registrada

                18:15 · ZorroEstelar:
                ¿Podemos hablar en otra aplicación?

                18:16 · Jugador de muestra:
                Prefiero quedarme en ANIMOON.

                18:16 · ZorroEstelar:
                De acuerdo.
            """.trimIndent()
        ),
        AdminAppeal(
            id = "AP-DEMO-001",
            nickname = "LunaVioleta",
            date = "18 de octubre de 2026 · 15:10",
            incident = "Solicitud de mantener una conversación en secreto",
            explanation =
                "Solicito que revisen los mensajes completos " +
                        "para aclarar lo que intentaba decir.",
            evidence = """
                Conversación registrada

                15:05 · LunaVioleta:
                No cuentes lo que estamos hablando.

                15:06 · Jugador de muestra:
                Si algo me preocupa, puedo hablar con mi tutor.

                15:06 · LunaVioleta:
                Entiendo.
            """.trimIndent()
        )
    )

    // Cache en memoria para respuestas remotas
    private var remoteCache: MutableMap<String, AdminAppeal> = mutableMapOf()

    suspend fun fetchAllRemote(): List<AdminAppeal> {
        val token = AdminDemoSession.adminToken.orEmpty()
        try {
            val response = ApiClient.adminService.getAppeals(token)
            if (response.isSuccessful && response.body() != null) {
                val list = response.body()!!.map { dto ->
                    val statusParsed = try {
                        AdminAppealStatus.valueOf(dto.status)
                    } catch (e: Exception) {
                        AdminAppealStatus.PENDING
                    }

                    AdminAppeal(
                        id = dto.id,
                        nickname = dto.nickname,
                        date = dto.date,
                        incident = dto.incident,
                        explanation = dto.explanation,
                        evidence = dto.evidence,
                        status = statusParsed,
                        resolution = dto.resolution,
                        resolvedAt = dto.resolvedAt,
                        resolvedBy = dto.resolvedBy
                    )
                }

                synchronized(this) {
                    remoteCache.clear()
                    list.forEach { appeal ->
                        remoteCache[appeal.id] = appeal
                        save(appeal)
                    }
                }
                return list
            }
        } catch (_: Exception) {
            // Fallback a almacenamiento local si el backend no responde
        }
        return getAll()
    }

    fun getAll(): List<AdminAppeal> {
        synchronized(this) {
            if (remoteCache.isNotEmpty()) {
                return remoteCache.values.toList()
            }
        }

        return samples.map { sample ->
            val stored = preferences.getString(sample.id, null)
                ?: return@map sample

            val json = JSONObject(stored)

            val status = try {
                AdminAppealStatus.valueOf(json.getString("status"))
            } catch (e: Exception) {
                AdminAppealStatus.PENDING
            }

            sample.copy(
                status = status,
                resolution = json.optString("resolution"),
                resolvedAt = json.optLong("resolvedAt"),
                resolvedBy = json.optString("resolvedBy")
            )
        }
    }

    fun find(id: String): AdminAppeal? =
        getAll().firstOrNull { it.id == id }

    suspend fun markInReviewRemote(id: String): Boolean {
        val token = AdminDemoSession.adminToken.orEmpty()
        try {
            val response = ApiClient.adminService.markInReview(token, id)
            if (response.isSuccessful) {
                markInReview(id)
                return true
            }
        } catch (_: Exception) {
        }
        return markInReview(id)
    }

    @Synchronized
    fun markInReview(id: String): Boolean {
        val appeal = find(id) ?: return false

        if (appeal.status != AdminAppealStatus.PENDING) {
            return false
        }

        val updated = appeal.copy(status = AdminAppealStatus.IN_REVIEW)
        remoteCache[id] = updated
        return save(updated)
    }

    suspend fun resolveRemote(
        id: String,
        approved: Boolean,
        reason: String
    ): Boolean {
        val token = AdminDemoSession.adminToken.orEmpty()
        val cleanReason = reason.trim()

        try {
            val response = ApiClient.adminService.resolve(
                token = token,
                id = id,
                req = AdminAppealResolveRequest(approved = approved, reason = cleanReason)
            )

            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val st = if (approved) AdminAppealStatus.APPROVED else AdminAppealStatus.REJECTED
                val updated = AdminAppeal(
                    id = dto.id,
                    nickname = dto.nickname,
                    date = dto.date,
                    incident = dto.incident,
                    explanation = dto.explanation,
                    evidence = dto.evidence,
                    status = st,
                    resolution = dto.resolution,
                    resolvedAt = dto.resolvedAt,
                    resolvedBy = dto.resolvedBy
                )
                synchronized(this) {
                    remoteCache[id] = updated
                    save(updated)
                }
                return true
            }
        } catch (_: Exception) {
        }

        return resolve(id, approved, cleanReason)
    }

    @Synchronized
    fun resolve(
        id: String,
        approved: Boolean,
        reason: String
    ): Boolean {
        val appeal = find(id) ?: return false
        val cleanReason = reason.trim()

        if (appeal.status.isResolved) return false
        if (cleanReason.isBlank() || cleanReason.length > 500) {
            return false
        }

        val updated = appeal.copy(
            status = if (approved) {
                AdminAppealStatus.APPROVED
            } else {
                AdminAppealStatus.REJECTED
            },
            resolution = cleanReason,
            resolvedAt = System.currentTimeMillis(),
            resolvedBy = AdminDemoSession.USERNAME
        )

        remoteCache[id] = updated
        return save(updated)
    }

    private fun save(appeal: AdminAppeal): Boolean {
        val json = JSONObject()
            .put("status", appeal.status.name)
            .put("resolution", appeal.resolution)
            .put("resolvedAt", appeal.resolvedAt)
            .put("resolvedBy", appeal.resolvedBy)

        return preferences.edit()
            .putString(appeal.id, json.toString())
            .commit()
    }
}
