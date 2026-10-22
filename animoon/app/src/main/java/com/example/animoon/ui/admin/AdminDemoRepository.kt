package com.example.animoon.ui.admin

import android.content.Context
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
 * Acceso simulado para probar la interfaz.
 * No representa autenticación ni autorización del servidor.
 */
object AdminDemoSession {

    const val USERNAME = "admin.animoon"

    private const val PASSWORD = "AdminDemo#2026"

    var isActive = false
        private set

    fun login(username: String, password: String): Boolean {
        isActive = username == USERNAME && password == PASSWORD
        return isActive
    }

    fun logout() {
        isActive = false
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
                Conversación ficticia

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
                Conversación ficticia

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
                Conversación ficticia

                15:05 · LunaVioleta:
                No cuentes lo que estamos hablando.

                15:06 · Jugador de muestra:
                Si algo me preocupa, puedo hablar con mi tutor.

                15:06 · LunaVioleta:
                Entiendo.
            """.trimIndent()
        )
    )

    fun getAll(): List<AdminAppeal> = samples.map { sample ->
        val stored = preferences.getString(sample.id, null)
            ?: return@map sample

        val json = JSONObject(stored)

        val status = AdminAppealStatus.valueOf(
            json.getString("status")
        )

        sample.copy(
            status = status,
            resolution = json.optString("resolution"),
            resolvedAt = json.optLong("resolvedAt"),
            resolvedBy = json.optString("resolvedBy")
        )
    }

    fun find(id: String): AdminAppeal? =
        getAll().firstOrNull { it.id == id }

    /**
     * Llamar fuera del hilo principal.
     */
    @Synchronized
    fun markInReview(id: String): Boolean {
        val appeal = find(id) ?: return false

        if (appeal.status != AdminAppealStatus.PENDING) {
            return false
        }

        return save(
            appeal.copy(status = AdminAppealStatus.IN_REVIEW)
        )
    }

    /**
     * Una decisión ya registrada no puede sobrescribirse.
     * Esta restricción es local y de demostración.
     */
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

        return save(
            appeal.copy(
                status = if (approved) {
                    AdminAppealStatus.APPROVED
                } else {
                    AdminAppealStatus.REJECTED
                },
                resolution = cleanReason,
                resolvedAt = System.currentTimeMillis(),
                resolvedBy = AdminDemoSession.USERNAME
            )
        )
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