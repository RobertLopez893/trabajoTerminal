package com.example.animoon.ui.help

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.view.ViewCompat
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton

class HelpActivity : BaseActivity() {

    private data class HelpQuestion(
        val key: String,
        val question: String,
        val answer: String
    )

    private val expandedQuestions = mutableSetOf<String>()

    companion object {
        private const val STATE_EXPANDED = "help_expanded_questions"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_help)

        savedInstanceState
            ?.getStringArrayList(STATE_EXPANDED)
            ?.let { expandedQuestions.addAll(it) }

        val backButton =
            findViewById<MaterialButton>(R.id.btnHelpBack)

        val instructionsContainer =
            findViewById<LinearLayout>(
                R.id.containerHelpInstructions
            )

        val safetyContainer =
            findViewById<LinearLayout>(
                R.id.containerHelpSafety
            )

        backButton.setOnClickListener {
            finish()
        }

        addQuestions(
            container = instructionsContainer,
            questions = instructionQuestions()
        )

        addQuestions(
            container = safetyContainer,
            questions = safetyQuestions()
        )
    }

    private fun addQuestions(
        container: LinearLayout,
        questions: List<HelpQuestion>
    ) {
        questions.forEach { item ->

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

            answerText.text = item.answer

            fun updateCard() {
                val expanded =
                    expandedQuestions.contains(item.key)

                questionButton.text =
                    if (expanded) {
                        "−  ${item.question}"
                    } else {
                        "+  ${item.question}"
                    }

                // El lector de pantalla recibe la pregunta
                // sin tener que leer los símbolos + y −.
                questionButton.contentDescription =
                    item.question

                ViewCompat.setStateDescription(
                    questionButton,
                    if (expanded) "Expandida" else "Contraída"
                )

                answerText.visibility =
                    if (expanded) View.VISIBLE else View.GONE
            }

            questionButton.setOnClickListener {
                if (!expandedQuestions.add(item.key)) {
                    expandedQuestions.remove(item.key)
                }

                updateCard()
            }

            updateCard()
            container.addView(card)
        }
    }

    private fun instructionQuestions(): List<HelpQuestion> {
        return listOf(
            HelpQuestion(
                key = "start",
                question = "¿Dónde empiezo?",
                answer =
                    "La Base Principal es tu punto de partida. " +
                            "Desde allí puedes abrir Minijuegos o entrar " +
                            "a Ajustes usando sus botones."
            ),
            HelpQuestion(
                key = "minigames",
                question = "¿Cómo entro a los minijuegos?",
                answer =
                    "En la Base Principal, toca Minijuegos para abrir " +
                            "el menú y elegir una actividad disponible. " +
                            "También puedes tocar el portal del Centro de " +
                            "Entrenamiento y confirmar que quieres entrar."
            ),
            HelpQuestion(
                key = "instructions",
                question = "¿Cómo sé qué hacer en cada juego?",
                answer =
                    "Observa la historia y lee las instrucciones " +
                            "que aparecen en la pantalla. En el entrenamiento " +
                            "de preguntas, lee la situación y toca la respuesta " +
                            "que consideres más segura. Después, revisa la " +
                            "explicación antes de continuar."
            ),
            HelpQuestion(
                key = "mistakes",
                question = "¿Qué pasa si me equivoco?",
                answer =
                    "¡Equivocarse también ayuda a aprender! " +
                            "Lee con calma la explicación de Moonie para " +
                            "entender cómo cuidarte y sigue las indicaciones " +
                            "de la pantalla."
            ),
            HelpQuestion(
                key = "notifications",
                question = "¿Cómo cambio las notificaciones?",
                answer =
                    "Abre Ajustes desde la Base Principal y usa el " +
                            "interruptor de Notificaciones locales. " +
                            "Si Android solicita permiso, puedes aceptarlo " +
                            "o continuar jugando sin notificaciones."
            ),
            HelpQuestion(
                key = "logout",
                question = "¿Cómo cierro mi sesión?",
                answer =
                    "Abre Ajustes, toca Cerrar sesión y confirma. " +
                            "Si quieres seguir jugando, elige Quedarme."
            )
        )
    }

    private fun safetyQuestions(): List<HelpQuestion> {
        return listOf(
            HelpQuestion(
                key = "personal_data",
                question = "¿Qué información debo cuidar?",
                answer =
                    "No compartas tu contraseña, dirección, teléfono, " +
                            "ubicación ni el nombre de tu escuela con personas " +
                            "que conoces por Internet. Antes de enviar fotos " +
                            "o información personal, pide ayuda a una persona " +
                            "adulta de confianza."
            ),
            HelpQuestion(
                key = "uncomfortable",
                question = "¿Qué hago si alguien me incomoda?",
                answer =
                    "Puedes dejar de responder y alejarte de la " +
                            "conversación. Cuéntaselo a una persona adulta de " +
                            "confianza, como tu mamá, papá, alguien que te cuida " +
                            "o un docente. No tienes que seguir hablando " +
                            "con alguien que te hace sentir mal."
            ),
            HelpQuestion(
                key = "secrets",
                question = "¿Y si me piden guardar un secreto?",
                answer =
                    "Si un secreto te hace sentir miedo, preocupación " +
                            "o incomodidad, puedes contarlo a una persona adulta " +
                            "de confianza, aunque hayas prometido no hacerlo. " +
                            "Pedir ayuda está bien."
            ),
            HelpQuestion(
                key = "gifts",
                question = "¿Y si me ofrecen regalos a cambio de algo?",
                answer =
                    "Si alguien te ofrece premios, monedas o regalos " +
                            "a cambio de fotos, datos personales o cosas que " +
                            "te incomodan, no tienes que aceptar. Deja de " +
                            "responder y pide ayuda a una persona adulta " +
                            "de confianza."
            ),
            HelpQuestion(
                key = "already_shared",
                question = "¿Qué hago si ya compartí algo?",
                answer =
                    "No es tu culpa si alguien te engañó o te presionó. " +
                            "No envíes más información y busca a una persona " +
                            "adulta de confianza para que te ayude. " +
                            "Si la primera persona no te escucha, busca a otra."
            ),
            HelpQuestion(
                key = "identity",
                question = "¿Todos son quienes dicen ser en Internet?",
                answer =
                    "Una foto, un nombre o un avatar no demuestra " +
                            "quién está detrás de una cuenta. Aunque alguien " +
                            "diga tener tu edad, cuida tus datos y no acuerdes " +
                            "encuentros por tu cuenta. Habla con una persona " +
                            "adulta de confianza."
            )
        )
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putStringArrayList(
            STATE_EXPANDED,
            ArrayList(expandedQuestions)
        )

        super.onSaveInstanceState(outState)
    }
}