package com.example.animoon.ui.parents

data class ParentAlert(
    val id: String,
    val dateLabel: String,
    val title: String,
    val summary: String,
    val isRead: Boolean = false
)

object ParentDemoData {

    var childNickname: String = "ExploradorLunar"
    var childDescription: String = "Cuenta protegida por Animoon"

    // Ordenadas de la más reciente a la más antigua.
    var alerts: List<ParentAlert> = listOf(
        ParentAlert(
            id = "DEMO-003",
            dateLabel = "18 de octubre de 2026 · 17:40",
            title = "Solicitud de información personal",
            summary = "En una conversación de ejemplo, otro jugador " +
                    "solicitó datos personales del menor."
        ),
        ParentAlert(
            id = "DEMO-002",
            dateLabel = "17 de octubre de 2026 · 16:15",
            title = "Invitación a conversar fuera de ANIMOON",
            summary = "En una conversación de ejemplo, otro jugador " +
                    "propuso continuar el contacto en una aplicación externa."
        ),
        ParentAlert(
            id = "DEMO-001",
            dateLabel = "16 de octubre de 2026 · 18:05",
            title = "Solicitud de mantener una conversación en secreto",
            summary = "En una conversación de ejemplo, otro jugador " +
                    "pidió al menor no comentar la interacción con su tutor."
        )
    )
}

/**
 * Sesión parental protegida (15 minutos de inactividad).
 * Almacena el token de autorización expedido por el backend tras validar el SMS.
 */
object ParentDemoSession {

    private const val INACTIVITY_LIMIT_MS = 15 * 60 * 1_000L

    var parentToken: String? = null
        private set

    private var active = false
    private var lastInteraction = 0L

    val isActive: Boolean
        get() = active && remainingMillis() > 0L

    fun start(token: String = "") {
        active = true
        parentToken = token.ifBlank { "PARENT_SESSION_ACTIVE" }
        lastInteraction = android.os.SystemClock.elapsedRealtime()
    }

    fun remainingMillis(): Long {
        if (!active) return 0L

        val elapsed =
            android.os.SystemClock.elapsedRealtime() - lastInteraction

        return (INACTIVITY_LIMIT_MS - elapsed).coerceAtLeast(0L)
    }

    fun registerInteraction() {
        if (remainingMillis() > 0L) {
            lastInteraction = android.os.SystemClock.elapsedRealtime()
        }
    }

    fun clear() {
        active = false
        parentToken = null
        lastInteraction = 0L
    }
}
