package com.example.animoon.ui.minigame.game2

import com.example.animoon.ui.minigame.game2.model.CategoriaMensaje
import com.example.animoon.ui.minigame.game2.model.MensajeJuego


object Game2MessageBank {


    // =========================================================
    // DATOS PERSONALES
    // =========================================================

    val personales = listOf(

        MensajeJuego(
            id = 101,
            texto = "Me llamo Juan Pérez",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Tu nombre completo solo lo pueden conocer personas que ya saben quién eres de verdad, como tus padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 102,
            texto = "Tengo 6 años",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Tu edad es un dato personal: solo va a padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 103,
            texto = "El nombre de mi mamá es Alondra",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Datos de tu familia solo deben viajar a padres, tutores o profesores, nunca a Animoon."
        ),

        MensajeJuego(
            id = 104,
            texto = "Vivo en Tlanepantla",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Saber dónde vives es delicado. Solo tus padres o profesores pueden saberlo."
        ),

        MensajeJuego(
            id = 105,
            texto = "Mi número de teléfono es 55-1234",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Un teléfono es un dato personal, solo para padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 106,
            texto = "Mi contraseña es: hola123",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "¡Una contraseña nunca debe compartirse por Animoon! Solo confía eso a tus padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 107,
            texto = "Mi escuela se llama Benito Juárez y está cerca de mi casa",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Ese dato ayuda a saber dónde encontrarte, así que solo va a padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 108,
            texto = "Estoy solo en mi casa ahorita",
            categoria = CategoriaMensaje.PERSONAL,
            explicacion = "Contar que estás solo es peligroso compartirlo por Animoon. Eso solo se dice a padres, tutores o profesores."
        )
    )


    // =========================================================
    // DATOS DEL JUEGO
    // =========================================================

    val juego = listOf(

        MensajeJuego(
            id = 201,
            texto = "Mi nombre de usuario es Zorrito99",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Un nombre de usuario de juego es inofensivo, puede viajar a padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 202,
            texto = "¡Mi récord en Súper Carrera es 700!",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Presumir tu puntaje está bien con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 203,
            texto = "Mi avatar favorito es el zorro",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Hablar de tu avatar es seguro con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 204,
            texto = "Ya llegué al nivel 12",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Contar tu progreso en el juego puede ir a padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 205,
            texto = "Mi equipo se llama Los Rayos",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "El nombre de tu equipo de juego no revela nada personal, así que puede ir a cualquiera de los tres."
        ),

        MensajeJuego(
            id = 206,
            texto = "Elegí el traje azul para mi personaje",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Eso es solo del juego, puede compartirse con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 207,
            texto = "Mi mascota virtual se llama Copito",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Una mascota virtual es un dato de juego, seguro para los tres puertos."
        ),

        MensajeJuego(
            id = 208,
            texto = "Tengo 3 estrellas en este nivel",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Tu avance en el juego es seguro de compartir con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 209,
            texto = "Mi clan se llama Los Ninjas",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "El nombre de tu clan es un dato de juego, puede ir a cualquiera de los tres."
        ),

        MensajeJuego(
            id = 210,
            texto = "Desbloqueé una espada nueva",
            categoria = CategoriaMensaje.JUEGO,
            explicacion = "Eso es parte del juego, no hay problema en compartirlo con padres, tutores, profesores o Animoon."
        )
    )


    // =========================================================
    // INFORMACIÓN ESCOLAR
    // =========================================================

    val escolares = listOf(

        MensajeJuego(
            id = 301,
            texto = "¿Cuál era la tarea de mate?",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Preguntas de tarea son para padres, tutores o profesores, no para Animoon."
        ),

        MensajeJuego(
            id = 302,
            texto = "La escuela estuvo aburrida hoy",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Hablar de tu día escolar solo debe ser con padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 303,
            texto = "Me gustan mucho las matemáticas",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Aunque parezca inofensivo, hablar de la escuela solo va a padres, tutores o profesores, no por Animoon."
        ),

        MensajeJuego(
            id = 304,
            texto = "Mañana tenemos examen de ciencias",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Información sobre tu escuela solo es para padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 305,
            texto = "La maestra dejó leer un cuento",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Contar detalles de la escuela es solo para padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 306,
            texto = "No entendí la clase de hoy, ¿me explicas?",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Esa duda es mejor resolverla con padres, tutores o profesores, no por Animoon."
        ),

        MensajeJuego(
            id = 307,
            texto = "Hoy tuvimos educación física",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Detalles del horario escolar solo se comparten con padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 308,
            texto = "Mi materia favorita es historia",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Hablar de la escuela, aunque sea algo lindo, solo va con padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 309,
            texto = "¿A qué hora salen de la escuela?",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Ese dato podría usarse para saber dónde encontrarte, solo para padres, tutores o profesores."
        ),

        MensajeJuego(
            id = 310,
            texto = "Mi salón es el 3B",
            categoria = CategoriaMensaje.ESCOLAR,
            explicacion = "Saber tu salón es un dato escolar delicado, solo para padres, tutores o profesores."
        )
    )


    // =========================================================
    // AMIGOS / HOBBIES
    // =========================================================

    val entretenimiento = listOf(

        MensajeJuego(
            id = 401,
            texto = "¡Me gusta el Hombre Araña!",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Hablar de tus gustos es seguro con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 402,
            texto = "¿Qué cartas de Pokémon tienes?",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Eso es un tema de amigos, puede ir a cualquiera de los tres puertos."
        ),

        MensajeJuego(
            id = 403,
            texto = "¿Ya viste el nuevo capítulo de Paw Patrol?",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Hablar de caricaturas es inofensivo, va bien con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 404,
            texto = "Mi dibujo favorito es el de los dinosaurios",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Compartir tus gustos artísticos es seguro con los tres puertos."
        ),

        MensajeJuego(
            id = 405,
            texto = "¿Jugamos en línea el sábado?",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Invitar a jugar es un tema de amigos, puede ir a padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 406,
            texto = "Mi color favorito es el verde",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Ese gusto personal, al no ser un dato sensible, puede compartirse con cualquiera de los tres."
        ),

        MensajeJuego(
            id = 407,
            texto = "¿Cuál es tu superhéroe favorito?",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Una pregunta de gustos es segura con padres, tutores, profesores o Animoon."
        ),

        MensajeJuego(
            id = 408,
            texto = "Me encanta armar Legos",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Hablar de tus pasatiempos es seguro con los tres puertos."
        ),

        MensajeJuego(
            id = 409,
            texto = "¿Viste la película nueva de animales?",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Comentar películas es un tema de amigos, va bien con cualquiera de los tres."
        ),

        MensajeJuego(
            id = 410,
            texto = "Me gusta dibujar monstruitos",
            categoria = CategoriaMensaje.ENTRETENIMIENTO,
            explicacion = "Compartir un hobby así es seguro con padres, tutores, profesores o Animoon."
        )
    )
}