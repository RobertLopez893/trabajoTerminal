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
                "Usuario externo", "17:38",
                "Sí, nos vemos ahí.", false
            ),
            ParentIncidentMessage(
                "Usuario externo", "17:39",
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
                "Usuario externo", "16:13",
                "Podemos seguir platicando.", false
            ),
            ParentIncidentMessage(
                "Usuario externo", "16:14",
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
                "Usuario externo", "18:03",
                "No le cuentes sobre nuestra conversación.", false
            ),
            ParentIncidentMessage(
                "ExploradorLunar", "18:04",
                "¿Por qué?", true
            ),
            ParentIncidentMessage(
                "Usuario externo", "18:04",
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
                "Acompañen la interacción y mantengan las conversaciones " +
                        "dentro de ANIMOON, donde aplican los filtros de seguridad."

            "DEMO-001" ->
                "Refuercen la confianza para hablar sobre situaciones que " +
                        "generen incomodidad y recuerden que no debe guardar secretos que le preocupen."

            else ->
                "Escucha con calma, revisa el contexto y refuerza la confianza del menor."
        }

        return """
            1. Escucha con calma
        
            Pregunta qué ocurrió, sin culpar ni regañar al menor. Hazle saber que puede pedirte apoyo siempre.
        
            2. Revisa el contexto
        
            Lee la conversación disponible y pregunta si hubo otras interacciones. Una alerta señala una situación que necesita revisión y contención preventiva.
        
            3. Refuerza la prevención
        
            $specificAdvice
        
            4. Acompaña los siguientes pasos
        
            Si la situación te preocupa, puedes reportar al usuario desde la plataforma o consultar a una persona especialista en orientación infantil.
        """.trimIndent()
    }
}
