<div align="center">
  <img src="animoon/app/src/main/res/drawable/logo_animoon.png" alt="Animoon Logo" width="200" />
  
  # Animoon 🌙
  **Protegiendo sonrisas en cada conexión virtual**
  
  *Un Prototipo de Entorno Virtual Anti-Grooming con Inteligencia Artificial*
</div>

<br>

> **Trabajo Terminal No. 2026 - B109**  
> *Escuela Superior de Cómputo (ESCOM) - Instituto Politécnico Nacional*

---

## ✨ Descubre Animoon

**Animoon** es más que un simple juego; es un espacio digital seguro diseñado especialmente para niños de 6 a 13 años. Nuestro Producto Mínimo Viable (MVP) para dispositivos móviles Android ofrece una experiencia única que combina divertidos minijuegos y un chat interactivo, todo respaldado por tecnología de vanguardia.

Nuestra innovación central es un **guardián inteligente**: un modelo de **Procesamiento de Lenguaje Natural (PLN/NLP)** que trabaja de forma invisible para detectar y prevenir patrones de *grooming* en etapas tempranas. ¡Para que la diversión nunca esté en riesgo!

---

## 🎯 Nuestros Objetivos

- 🛡️ **Entorno 100% Seguro:** Un mundo virtual vibrante con minijuegos educativos e interfaces adaptadas y seguras.
- 🧠 **Detección Inteligente:** Análisis semántico profundo de las conversaciones mediante inteligencia artificial (modelo basado en la arquitectura **BERT**).
- 🚨 **Protección Proactiva:** Respuesta inmediata ante riesgos. El sistema actúa como un escudo: detecta, bloquea y alerta a los tutores de forma automática.

---

## 🚀 Características Estrella

* 🔒 **Autenticación Familiar:** Registro seguro con supervisión y verificación parental obligatoria.
* 💬 **Chat con Auditoría NLP:** Monitoreo en tiempo real. Analizamos el contexto cada ciclo de interacciones para neutralizar amenazas al instante.
* ⚡ **Moderación Automática Inmediata:**
  * Identificación rápida de comportamientos anómalos.
  * Bloqueo y suspensión automática de perfiles de riesgo.
  * Alertas inmediatas enviadas por correo electrónico a los padres.
* 🔐 **Privacidad de Hierro:** Tus datos están seguros. Utilizamos **Argon2** para el cifrado de credenciales y **AES** para proteger cada mensaje.

---

## 🛠️ Nuestro Arsenal Tecnológico

<div align="center">

| Área | Tecnología | Propósito |
| :--- | :--- | :--- |
| **📱 Frontend (Móvil)** | **Kotlin** (Android Studio) | Magia visual e interfaces interactivas. |
| **🧠 Cerebro (IA / NLP)** | **Python** (Jupyter) | Entrenamiento y lógica del modelo de lenguaje. |
| **🤖 Frameworks ML** | **PyTorch, TensorFlow, Hugging Face** | El corazón de nuestro detector inteligente. |
| **🗄️ Backend / BD** | **MySQL** / SQL | Gestión robusta y ágil de la base de datos de usuarios. |
| **🛡️ Seguridad** | **Argon2, AES** | Cifrado militar para la máxima privacidad y protección. |
| **🎨 Diseño** | **Adobe Photoshop / Godot** | Creación de mundos, assets y recursos gráficos. |
| **📈 Metodología** | **Scrumban** | Desarrollo ágil, ordenado y eficiente. |

</div>

---

## ⚙️ ¿Cómo funciona la magia?

1. 🔑 **Registro y Verificación:** Acceso controlado desde el primer momento con el visto bueno de los padres o tutores.
2. 🎮 **A Jugar:** El niño explora, juega y chatea en el entorno virtual de Animoon.
3. 👁️‍🗨️ **El Guardián en Acción:** 
   * Los mensajes fluyen al backend de forma cifrada.
   * Al alcanzar el umbral de mensajes, el **Modelo de IA** analiza el contexto de la conversación.
4. ⚖️ **Veredicto Inmediato:**
   * 🔴 **Riesgo Detectado:** Protocolo de emergencia activado (Suspensión de cuenta + Alerta a Padres).
   * 🟢 **Todo Seguro:** ¡Que siga la diversión con total tranquilidad!

---

## 🚀 Guía de Ejecución (Frontend y Backend)

Para probar la comunicación entre la aplicación móvil (Frontend) y nuestro servidor de autenticación/IA (Backend), sigue estos pasos:

### 1. Levantar el Backend (Servidor)
El backend está "dockerizado" para evitar problemas de instalación. 
1. Asegúrate de tener Docker instalado y abierto.
2. Abre una terminal en la raíz del proyecto y ejecuta:
   ```bash
   docker-compose up -d --build
   ```
3. Esto levantará la API de FastAPI (puerto `8000`) y la base de datos PostgreSQL de forma automática.

### 2. Configurar la App de Android (Frontend)
¡Buenas noticias! **Por defecto, la app ya está apuntando al servidor de pruebas en AWS** (`http://18.217.21.239:8000/`).
Solo dale "Play" en Android Studio y estarás probando en la nube con el resto del equipo.

Si algún día AWS se apaga y quieres **probar en tu computadora local**, la IP se configura de forma local para evitar conflictos en Git:

1. Abre el archivo `animoon/local.properties`.
2. Agrega la variable `API_BASE_URL` dependiendo de dónde vayas a probar:

**Opción A: Probar en el Emulador de Android Studio (Local)**
```properties
API_BASE_URL=http://10.0.2.2:8000/
```

**Opción B: Probar en Celular Físico conectado a tu PC (Local)**
```properties
API_BASE_URL=http://T.U.I.P:8000/
```
*(Y presiona el botón del elefante 🐘 en Gradle para aplicar).*

### 3. Sincronizar y Correr
1. En Android Studio, da clic en **Sync Project with Gradle Files** (el ícono del elefante 🐘).
2. Selecciona tu emulador o tu celular físico y dale clic a Play (▶️) para instalar la app.

---

## 📈 Ruta de Desarrollo

Construyendo el futuro paso a paso bajo la normativa **ISO/IEC 12207**:

- [x] **Iteración 0:** Formulación, Análisis y Diseño conceptual.
- [x] **Iteración 1:** Entrenamiento del modelo NLP y arquitectura base.
- [ ] **Iteración 2:** Módulos de Registro, Login y Seguridad de datos (En progreso).
- [ ] **Iteración 3:** Creación del Mundo Virtual: Chat y Minijuegos.
- [ ] **Iteración 4:** Integración total, Pruebas y Pulido final.

---

## 👨‍💻 Equipo de Desarrollo

Este proyecto se desarrolla como parte de la titulación en **Ingeniería en Sistemas Computacionales**.

**Creadores:**
* 🌟 **González Martínez Silvia** - *sgonzalezm1902@alumno.ipn.mx*
* 🌟 **López Chávez Moisés** - *mlopezc2105@alumno.ipn.mx*
* 🌟 **López Reyes José Roberto** - *jlopezr1911@alumno.ipn.mx*
* 🌟 **Serrano Gayosso José Eduardo** - *jserranog1900@alumno.ipn.mx*

**Directores:**
* 🎓 **M. en C. López Rojas Ariel** - *arilopez@ipn.mx*

<br>

<div align="center">
  <i>"La tecnología al servicio de los que más queremos."</i> <br>
  <b>Escuela Superior de Cómputo - Instituto Politécnico Nacional</b>
</div>
