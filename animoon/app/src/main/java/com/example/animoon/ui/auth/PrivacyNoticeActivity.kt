package com.example.animoon.ui.auth

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.core.view.ViewCompat
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton

class PrivacyNoticeActivity : BaseActivity() {

    override val observarSesionExpirada: Boolean = false

    private data class PrivacySection(
        val key: String,
        val title: String,
        val content: String
    )

    private val expandedSections = mutableSetOf<String>()

    companion object {
        private const val STATE_EXPANDED = "privacy_expanded_sections"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_privacy_notice)

        val sections = privacySections()

        if (savedInstanceState != null) {
            savedInstanceState
                .getStringArrayList(STATE_EXPANDED)
                ?.let { expandedSections.addAll(it) }
        } else {
            // Mostramos todas las secciones desplegadas inicialmente para lectura directa,
            // conservando el comportamiento interactivo de contraer/expandir como en Ayuda.
            sections.forEach { expandedSections.add(it.key) }
        }

        val backButton =
            findViewById<MaterialButton>(R.id.btnPrivacyBack)

        val sectionsContainer =
            findViewById<LinearLayout>(R.id.containerPrivacySections)

        backButton.setOnClickListener {
            finish()
            overridePendingTransition(0, 0)
        }

        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    finish()
                    overridePendingTransition(0, 0)
                }
            }
        )

        addSections(
            container = sectionsContainer,
            sections = sections
        )
    }

    private fun addSections(
        container: LinearLayout,
        sections: List<PrivacySection>
    ) {
        sections.forEach { item ->

            val card = layoutInflater.inflate(
                R.layout.item_help_question,
                container,
                false
            )

            val questionButton =
                card.findViewById<MaterialButton>(
                    R.id.btnHelpQuestion
                )

            val answerText =
                card.findViewById<TextView>(
                    R.id.txtHelpAnswer
                )

            answerText.text = item.content

            fun updateCard() {
                val expanded =
                    expandedSections.contains(item.key)

                questionButton.text =
                    if (expanded) {
                        "−  ${item.title}"
                    } else {
                        "+  ${item.title}"
                    }

                questionButton.contentDescription =
                    item.title

                ViewCompat.setStateDescription(
                    questionButton,
                    if (expanded) "Expandida" else "Contraída"
                )

                answerText.visibility =
                    if (expanded) View.VISIBLE else View.GONE
            }

            questionButton.setOnClickListener {
                if (!expandedSections.add(item.key)) {
                    expandedSections.remove(item.key)
                }

                updateCard()
            }

            updateCard()
            container.addView(card)
        }
    }

    private fun privacySections(): List<PrivacySection> {
        return listOf(
            PrivacySection(
                key = "responsables",
                title = "1. ¿Quiénes somos y quién cuida estos datos?",
                content =
                    "ANIMOON es un proyecto tecnológico desarrollado en la Escuela Superior de Cómputo " +
                            "del Instituto Politécnico Nacional (ESCOM - IPN, Trabajo Terminal 2026-B109). " +
                            "Los responsables directos del cuidado y protección de los datos de esta plataforma " +
                            "somos el equipo desarrollador:\n\n" +
                            "• González Martínez Silvia — sgonzalezm1902@alumno.ipn.mx\n" +
                            "• López Chávez Moisés — mlopezc2105@alumno.ipn.mx\n" +
                            "• López Reyes José Roberto — jlopezr1911@alumno.ipn.mx\n" +
                            "• Serrano Gayosso José Eduardo — jserranog1900@alumno.ipn.mx"
            ),
            PrivacySection(
                key = "minimizacion",
                title = "2. Privacidad desde el primer momento (Cero datos reales del menor)",
                content =
                    "En ANIMOON los niños juegan de forma anónima:\n\n" +
                            "• NUNCA pedimos ni guardamos el nombre real de tu hijo, su edad exacta, " +
                            "fotografías, dirección, escuela ni ubicación GPS.\n" +
                            "• Dentro del mundo virtual, tu hijo solo será conocido por un Apelativo " +
                            "(un apodo divertido que no debe incluir su nombre real) y su Avatar " +
                            "(su personaje animal)."
            ),
            PrivacySection(
                key = "datos_recabados",
                title = "3. ¿Qué datos pedimos y para qué los usamos?",
                content =
                    "• Tu número de teléfono celular (10 dígitos): Es el único dato personal que solicitamos. " +
                            "Lo usamos exclusivamente para:\n" +
                            "  1) Enviarte un código por SMS y confirmar que tú autorizas la creación de la cuenta.\n" +
                            "  2) Ayudarte a recuperar la contraseña o entrar a la \"Sección para Padres\".\n" +
                            "  3) Enviarte una alerta inmediata por SMS si nuestro sistema detecta alguna situación de riesgo en el chat.\n\n" +
                            "• Contraseña de la cuenta: Se guarda transformada mediante un candado criptográfico " +
                            "irreversible; ni siquiera nuestro equipo puede verla.\n\n" +
                            "• Progreso en el juego: Guardamos sus puntajes en los minijuegos educativos y " +
                            "preferencias de sonido o notificaciones para que su aventura continúe donde la dejó."
            ),
            PrivacySection(
                key = "guardian_ia",
                title = "4. ¿Cómo funciona nuestro Guardián Inteligente en el chat?",
                content =
                    "Para mantener a la comunidad segura frente a conductas inapropiadas o de acoso infantil (grooming):\n\n" +
                            "• Todos los mensajes viajan protegidos con cifrado de alta seguridad.\n" +
                            "• Nuestro sistema de Inteligencia Artificial analiza automáticamente bloques de " +
                            "conversación en busca de señales de riesgo, sin exponer la identidad de tu hijo.\n" +
                            "• Si el guardián detecta un comportamiento peligroso: cierra el chat de inmediato " +
                            "para poner a salvo a tu hijo, bloquea la cuenta del agresor, te envía un aviso por SMS " +
                            "y guarda únicamente ese fragmento de conversación bajo llave como evidencia en la \"Sección para Padres\".\n" +
                            "• En caso de que un bloqueo sea revisado por un moderador, este solo podrá ver el " +
                            "fragmento de mensajes que activó la alerta y jamás el historial completo de tu hijo."
            ),
            PrivacySection(
                key = "cero_publicidad",
                title = "5. Cero publicidad y cero ventas de información",
                content =
                    "En ANIMOON no existen anuncios comerciales. Nunca venderemos, rentaremos ni " +
                            "compartiremos tu número telefónico ni la actividad de la cuenta con terceros " +
                            "con fines publicitarios o comerciales."
            ),
            PrivacySection(
                key = "derechos_arco",
                title = "6. Tú tienes el control (Derechos ARCO)",
                content =
                    "Como madre, padre o tutor, en cualquier momento puedes revisar las alertas desde la " +
                            "\"Sección para Padres\" dentro de la app, o bien solicitar el Acceso, Rectificación, " +
                            "Cancelación de la cuenta u Oposición al uso de tus datos enviando un correo a " +
                            "cualquiera de nuestras direcciones de contacto:\n\n" +
                            "• sgonzalezm1902@alumno.ipn.mx\n" +
                            "• mlopezc2105@alumno.ipn.mx\n" +
                            "• jlopezr1911@alumno.ipn.mx\n" +
                            "• jserranog1900@alumno.ipn.mx"
            )
        )
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putStringArrayList(
            STATE_EXPANDED,
            ArrayList(expandedSections)
        )

        super.onSaveInstanceState(outState)
    }
}
