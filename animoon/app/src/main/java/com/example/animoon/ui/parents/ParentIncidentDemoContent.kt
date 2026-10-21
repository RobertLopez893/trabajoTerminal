package com.example.animoon.ui.parents

data class ParentIncidentMessage(
    val author: String,
    val time: String,
    val text: String,
    val fromChild: Boolean
)

object ParentIncidentDemoContent {

    // Los mensajes están ordenados del más antiguo al más reciente.
    val generalGuidance: String = """
        1. Conversen sobre su experiencia
    
        Pregunta qué le gusta jugar y cómo se siente al conversar con otras personas. Hazle saber que puede pedirte ayuda sin miedo a ser regañado.
    
        2. Cuiden la información personal
    
        Repasen qué datos deben mantenerse privados: domicilio, escuela, teléfono, contraseñas y ubicación.
    
        3. Revisen los nuevos contactos
    
        Acompaña al menor cuando alguien le proponga conversar en otra aplicación o compartir datos de contacto.
    
        4. Hablen sobre las conversaciones incómodas
    
        Recuérdale que puede dejar de responder y acudir a una persona adulta de confianza. Si alguien le pide guardar una conversación que le preocupa en secreto, puede contártelo.
    
        5. Consulten las alertas con calma
    
        Una alerta requiere revisar el contexto. La ausencia de alertas no garantiza que todas las interacciones sean seguras.
    """.trimIndent()
    private val conversations = mapOf(
        "DEMO-003" to listOf(
            ParentIncidentMessage(
                "ExploradorLunar", "17:38",
                "¿Vamos al centro de comando?", true
            ),
            ParentIncidentMessage(
                "Jugador de muestra", "17:38",
                "Sí, nos vemos ahí.", false
            ),
            ParentIncidentMessage(
                "Jugador de muestra", "17:39",
                "¿Cómo se llama tu escuela y dónde está?", false
            ),
            ParentIncidentMessage(
                "ExploradorLunar", "17:39",
                "Prefiero no compartir esos datos.", true
            )
        ),
        "DEMO-002" to listOf(
            ParentIncidentMessage(
                "ExploradorLunar", "16:13",
                "Ya terminé el minijuego.", true
            ),
            ParentIncidentMessage(
                "Jugador de muestra", "16:13",
                "Podemos seguir platicando.", false
            ),
            ParentIncidentMessage(
                "Jugador de muestra", "16:14",
                "Pásame tu número para hablar en otra aplicación.", false
            ),
            ParentIncidentMessage(
                "ExploradorLunar", "16:14",
                "Mejor seguimos jugando aquí.", true
            )
        ),
        "DEMO-001" to listOf(
            ParentIncidentMessage(
                "ExploradorLunar", "18:03",
                "Voy a contarle a mi mamá lo que jugamos.", true
            ),
            ParentIncidentMessage(
                "Jugador de muestra", "18:03",
                "No le cuentes sobre nuestra conversación.", false
            ),
            ParentIncidentMessage(
                "ExploradorLunar", "18:04",
                "¿Por qué?", true
            ),
            ParentIncidentMessage(
                "Jugador de muestra", "18:04",
                "Mejor que quede entre nosotros.", false
            )
        )
    )

    fun messagesFor(alertId: String): List<ParentIncidentMessage> =
        conversations[alertId].orEmpty().takeLast(20)

    fun guidanceFor(alertId: String): String {
        val specificAdvice = when (alertId) {
            "DEMO-003" ->
                "Recuerden qué información debe mantenerse privada: " +
                        "domicilio, escuela, teléfono, contraseñas y ubicación."

            "DEMO-002" ->
                "Conversen sobre las invitaciones a otras aplicaciones. " +
                        "Antes de aceptar nuevos contactos o compartir su número, " +
                        "el menor puede pedir ayuda a una persona adulta de confianza."

            "DEMO-001" ->
                "Explícale que puede hablar contigo sobre cualquier " +
                        "conversación que le preocupe, incluso si alguien " +
                        "le pidió mantenerla en secreto."

            else ->
                "Repasen juntos cómo pedir ayuda cuando una conversación " +
                        "resulte incómoda o solicite información privada."
        }

        return """
            1. Escucha con calma

            Pregunta qué ocurrió, sin culpar ni regañar al menor. Hazle saber que puede pedir ayuda.

            2. Revisa el contexto

            Lee la conversación disponible y pregunta si hubo otras interacciones. Una alerta señala una situación que necesita revisión; no confirma por sí sola la intención de otra persona.

            3. Refuerza la prevención

            $specificAdvice

            4. Acompaña los siguientes pasos

            Si el contacto le incomoda, ayúdale a interrumpir la conversación y a buscar apoyo de una persona adulta de confianza.
        """.trimIndent()
    }
}