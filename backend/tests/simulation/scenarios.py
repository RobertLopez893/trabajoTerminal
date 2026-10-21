"""
Escenarios de conversación para pruebas de simulación y validación de BETO en Animoon.
Incluye:
- Conversación normal/inocua (NIVEL_0_SEGURO)
- Ataque simulado de Grooming (NIVEL_2_GROOMING) con fases de confianza, aislamiento y petición de secretos.
"""

# Escenario 1: Conversación inocua entre dos amigos de la escuela (20 mensajes)
CONVERSACION_INOCUA = [
    {"emisor": "alice", "texto": "Hola Bob, ¿hiciste la tarea de matemáticas de ayer?"},
    {"emisor": "bob", "texto": "Hola Alice. Sí, terminé los primeros cinco ejercicios pero el seis se me complicó."},
    {"emisor": "alice", "texto": "El seis es sobre fracciones algebraicas, ¿verdad? Yo lo resolví simplificando los denominadores."},
    {"emisor": "bob", "texto": "Ah, tiene sentido. ¿Te dio 3/4 o 1/2 al final?"},
    {"emisor": "alice", "texto": "Me dio 3/4. Solo hay que factorizar el trinomio cuadrado perfecto."},
    {"emisor": "bob", "texto": "Genial, muchas gracias. ¿Vas a entrar al torneo de ajedrez de la escuela?"},
    {"emisor": "alice", "texto": "Sí, ya me inscribí con el profesor Martínez. ¿Tú también vas a jugar?"},
    {"emisor": "bob", "texto": "Estoy pensando en entrar pero juego con las blancas un poco lento."},
    {"emisor": "alice", "texto": "El ajedrez ayuda mucho a la concentración para los exámenes de física."},
    {"emisor": "bob", "texto": "Buena recomendación. Oye, ¿viste la película de animación que recomendaron en clase de arte?"},
    {"emisor": "alice", "texto": "Sí, la animación en stop-motion estuvo increíble, los colores eran muy vivos."},
    {"emisor": "bob", "texto": "A mí me encantó la música de la banda sonora, era con orquesta sinfónica."},
    {"emisor": "alice", "texto": "El profesor de música nos dejó escuchar la quinta sinfonía de Beethoven."},
    {"emisor": "bob", "texto": "Perfecto. ¿Cuáles páginas del libro de texto entran para el examen?"},
    {"emisor": "alice", "texto": "De la página 45 a la 60 del capítulo de álgebra y funciones."},
    {"emisor": "bob", "texto": "Excelente, voy a repasar los teoremas hoy por la tarde en mi casa."},
    {"emisor": "alice", "texto": "Sale, no se te olvide repasar la regla de tres y potencias."},
    {"emisor": "bob", "texto": "Ya guardé el libro en la mochila. Descansa Alice."},
    {"emisor": "alice", "texto": "Igualmente Bob, hasta mañana."},
    {"emisor": "bob", "texto": "Hasta mañana, que descanses."}
]

# Escenario 2: Ataque simulado de Grooming (20 mensajes)
# Diseñado con las pautas semánticas de grooming: halagos excesivos, solicitud de edad,
# aislamiento ("no le digas a tus papás"), secreto y propuesta de fotos o encuentro privado.
ATAQUE_GROOMING = [
    {"emisor": "agresor", "texto": "Hola bonita, te vi en el grupo y me llamaste mucho la atención."},
    {"emisor": "victima", "texto": "Hola, ¿quién eres? No te conozco."},
    {"emisor": "agresor", "texto": "Solo alguien que quiere ser tu amigo, eres muy linda e inteligente."},
    {"emisor": "victima", "texto": "Gracias, pero mis papás dicen que no hable con extraños."},
    {"emisor": "agresor", "texto": "Tus papás no tienen por qué enterarse de todo, eres muy madura para tu edad."},
    {"emisor": "victima", "texto": "Tengo 12 años, voy en primero de secundaria."},
    {"emisor": "agresor", "texto": "Te ves mucho más grande, tienes una madurez que no tienen las demás niñas."},
    {"emisor": "victima", "texto": "¿En serio? Casi todos en mi salón me dicen que soy tímida."},
    {"emisor": "agresor", "texto": "Es que ellos son unos tontos, tú eres especial. Yo te entiendo mejor que tu familia."},
    {"emisor": "victima", "texto": "A veces siento que mis papás no me prestan atención por su trabajo."},
    {"emisor": "agresor", "texto": "Por eso estoy aquí para cuidarte. Pero esto debe ser nuestro secreto especial entre tú y yo."},
    {"emisor": "victima", "texto": "¿Por qué un secreto? No me gusta mentirle a mi mamá."},
    {"emisor": "agresor", "texto": "No es mentir, es cuidar nuestra amistad para que no nos separen."},
    {"emisor": "victima", "texto": "Bueno... si tú lo dices."},
    {"emisor": "agresor", "texto": "Mándame una foto de ti en tu cuarto a solas para ver cómo estás vestida hoy."},
    {"emisor": "victima", "texto": "No quiero mandar fotos mías privadas, me da pena y no te conozco."},
    {"emisor": "agresor", "texto": "Si confías en mí mándame una foto íntima, borra nuestros mensajes para que nadie los vea."},
    {"emisor": "victima", "texto": "Ya no me hables de eso, me estás dando miedo."},
    {"emisor": "agresor", "texto": "No tengas miedo preciosa, apaga la luz y tómate la foto, prométeme que no le dirás a tus papás."},
    {"emisor": "agresor", "texto": "Mándame la foto ahora mismo y mañana nos vemos a solas en el parque sin que nadie sepa."}
]
