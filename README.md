# Prototipo de Entorno Virtual Anti-Grooming con NLP (Android)

> **Trabajo Terminal No. 2026 - B109**
> *Escuela Superior de Cómputo (ESCOM) - IPN*

## 📖 Descripción del Proyecto

Este proyecto consiste en el diseño, implementación y validación de un **Producto Mínimo Viable (MVP)** de un entorno virtual para dispositivos móviles Android, dirigido a niños de 6 a 13 años en la República Mexicana.

El objetivo principal es proporcionar un espacio digital seguro que combina minijuegos y un chat moderado. La innovación central reside en la integración de un modelo de **Procesamiento de Lenguaje Natural (PLN/NLP)** capaz de detectar patrones de *grooming* (acoso sexual a menores) en etapas tempranas.

### 🎯 Objetivos Principales
* **Entorno Seguro:** Crear un mundo virtual con minijuegos educativos e interfaces interactivas adecuadas para la edad.
* **Detección Inteligente:** Entrenar e implementar un modelo de PLN (basado en BERT) para analizar conversaciones.
* **Protección Activa:** Generar alertas y acciones de moderación automáticas (bloqueo temporal, aviso a tutores) al detectar comportamientos sospechosos.

---

## 🚀 Características Clave

* **Autenticación Supervisada:** Registro de usuarios con verificación mediante el correo electrónico de los padres/tutores.
* **Chat con Auditoría NLP:** El sistema procesa lotes de mensajes (cada 10 interacciones) para analizar el contexto en busca de riesgos de grooming.
* **Acciones de Moderación:**
    * Identificación del agresor.
    * Banear al agresor automáticamente.
    * Envío de correo de advertencia a los padres.
* **Seguridad de Datos:** Implementación de cifrado con **Argon2** para credenciales y **AES** para mensajes.

---

## 🛠️ Tecnologías y Herramientas

El desarrollo del prototipo utiliza el siguiente stack tecnológico:

| Área | Tecnología / Herramienta | Uso Principal |
| :--- | :--- | :--- |
| **Móvil (Frontend)** | **Kotlin** (Android Studio) | Desarrollo de la aplicación Android e interfaces. |
| **IA / NLP** | **Python** (Jupyter Notebook) | Entrenamiento y lógica del modelo de lenguaje. |
| **Frameworks ML** | PyTorch, TensorFlow, Hugging Face | Implementación del modelo **BERT**. |
| **Backend / BD** | **MySQL** / SQL | Gestión de base de datos de usuarios y registros. |
| **Seguridad** | Argon2, AES | Hashing de contraseñas y cifrado de datos. |
| **Diseño** | Adobe Photoshop | Creación de recursos gráficos y sprites. |
| **Metodología** | **Scrumban** | Gestión ágil del proyecto (Scrum + Kanban). |

---

## ⚙️ Arquitectura del Sistema

El flujo general del sistema sigue el siguiente esquema de operación:

1.  **Registro/Login:** Validación de credenciales y verificación parental.
2.  **Mundo Virtual:** El usuario accede a minijuegos y chat.
3.  **Monitorización:**
    * El sistema acumula mensajes en el Backend.
    * Al llegar a un umbral (ej. 10 mensajes), se envían al **Modelo de Detección**.
4.  **Decisión:**
    * Si `Grooming = True` ➔ Se detona el protocolo de seguridad (Ban + Alerta).
    * Si `Grooming = False` ➔ Continúa la interacción normal.

---

## 👥 Autores y Contacto

Este proyecto es desarrollado como parte de la titulación en Ingeniería en Sistemas Computacionales.

**Alumnos:**
* **González Martínez Silvia** (`sgonzalezm1902@alumno.ipn.mx`)
* **López Chávez Moisés** (`mlopezc2105@alumno.ipn.mx`)
* **López Reyes José Roberto** (`jlopezr1911@alumno.ipn.mx`)
* **Serrano Gayosso José Eduardo** (`jserranog1900@alumno.ipn.mx`)

**Directores:**
* **M. en C. López Rojas Ariel** (`arilopez@ipn.mx`)

---

## 📄 Estado del Proyecto

Actualmente, el proyecto se encuentra en desarrollo bajo la normativa **ISO/IEC 12207**, dividido en fases (TT1 y TT2):
- [x] **Iteración 0:** Formulación y Análisis (Actual).
- [x] **Iteración 1:** Entrenamiento del modelo NLP y diseño.
- [ ] **Iteración 2:** Módulos de Registro y Login.
- [ ] **Iteración 3:** Chat y Minijuegos.
- [ ] **Iteración 4:** Integración y Pruebas.

---
*Escuela Superior de Cómputo - Instituto Politécnico Nacional*
