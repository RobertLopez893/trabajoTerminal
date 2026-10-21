package com.example.animoon.ui.parents

data class ParentAlert(
    val id: String,
    val dateLabel: String,
    val title: String,
    val summary: String
)

object ParentDemoData {

    const val childNickname = "ExploradorLunar"
    const val childDescription = "Cuenta de muestra"

    // Ordenadas de la más reciente a la más antigua.
    val alerts: List<ParentAlert> = listOf(
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
 * Sesión simulada exclusivamente para navegar por el frontend.
 * No sustituye la autenticación ni la autorización del servidor.
 */
object ParentDemoSession {

    private const val INACTIVITY_LIMIT_MS = 15 * 60 * 1_000L

    private var active = false
    private var lastInteraction = 0L

    fun start() {
        active = true
        lastInteraction = android.os.SystemClock.elapsedRealtime()
    }

    fun remainingMillis(): Long {
        if (!active) return 0L

        val elapsed =
            android.os.SystemClock.elapsedRealtime() - lastInteraction

        return (INACTIVITY_LIMIT_MS - elapsed).coerceAtLeast(0L)
    }

    fun registerInteraction() {
        // Una interacción posterior al vencimiento no reactiva la sesión.
        if (remainingMillis() > 0L) {
            lastInteraction = android.os.SystemClock.elapsedRealtime()
        }
    }

    fun clear() {
        active = false
        lastInteraction = 0L
    }
}