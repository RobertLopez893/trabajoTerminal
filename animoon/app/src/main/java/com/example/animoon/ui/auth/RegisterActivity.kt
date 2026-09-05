package com.example.animoon.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.CheckBox
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class RegisterActivity : AppCompatActivity() {

    private lateinit var etRegisterApelativo: TextInputEditText
    private lateinit var etTutorPhone: TextInputEditText
    private lateinit var etRegisterPassword: TextInputEditText
    private lateinit var etConfirmPassword: TextInputEditText

    private lateinit var checkTerms: CheckBox

    private lateinit var btnSendSms: MaterialButton
    private lateinit var btnCancel: MaterialButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        initViews()
        configureListeners()
    }

    /**
     * Relaciona las variables Kotlin con los elementos
     * definidos en activity_register.xml.
     */
    private fun initViews() {

        etRegisterApelativo =
            findViewById(R.id.etRegisterApelativo)

        etTutorPhone =
            findViewById(R.id.etTutorPhone)

        etRegisterPassword =
            findViewById(R.id.etRegisterPassword)

        etConfirmPassword =
            findViewById(R.id.etConfirmPassword)

        checkTerms =
            findViewById(R.id.checkTerms)

        btnSendSms =
            findViewById(R.id.btnSendSms)

        btnCancel =
            findViewById(R.id.btnCancel)

        // Al iniciar, no se puede continuar
        // hasta aceptar los términos.
        btnSendSms.isEnabled = false
        btnSendSms.alpha = 0.5f
    }

    /**
     * Configura las acciones de los botones
     * y otros elementos interactivos.
     */
    private fun configureListeners() {

        checkTerms.setOnCheckedChangeListener { _, isChecked ->

            btnSendSms.isEnabled = isChecked

            btnSendSms.alpha =
                if (isChecked) {
                    1f
                } else {
                    0.5f
                }
        }

        btnCancel.setOnClickListener {

            // Regresa a la pantalla anterior.
            finish()
        }

        btnSendSms.setOnClickListener {

            validateRegisterData()
        }
    }

    /**
     * Valida la información capturada
     * antes de continuar a la verificación SMS.
     */
    private fun validateRegisterData() {

        val apelativo =
            etRegisterApelativo.text
                ?.toString()
                ?.trim()
                .orEmpty()

        val phone =
            etTutorPhone.text
                ?.toString()
                ?.trim()
                .orEmpty()

        val password =
            etRegisterPassword.text
                ?.toString()
                .orEmpty()

        val confirmPassword =
            etConfirmPassword.text
                ?.toString()
                .orEmpty()

        // -----------------------------------------
        // APelativo
        // -----------------------------------------

        if (apelativo.isEmpty()) {

            etRegisterApelativo.error =
                "Ingresa un apelativo"

            etRegisterApelativo.requestFocus()

            return
        }

        // -----------------------------------------
        // TELÉFONO
        // -----------------------------------------

        if (phone.isEmpty()) {

            etTutorPhone.error =
                "Ingresa el número del tutor"

            etTutorPhone.requestFocus()

            return
        }

        if (phone.length != 10 ||
            !phone.all { it.isDigit() }
        ) {

            etTutorPhone.error =
                "Ingresa un número de 10 dígitos"

            etTutorPhone.requestFocus()

            return
        }

        // -----------------------------------------
        // CONTRASEÑA
        // -----------------------------------------

        if (password.isEmpty()) {

            etRegisterPassword.error =
                "Ingresa una contraseña"

            etRegisterPassword.requestFocus()

            return
        }

        if (password.length < 8) {

            etRegisterPassword.error =
                "La contraseña debe tener al menos 8 caracteres"

            etRegisterPassword.requestFocus()

            return
        }

        // -----------------------------------------
        // CONFIRMAR CONTRASEÑA
        // -----------------------------------------

        if (confirmPassword.isEmpty()) {

            etConfirmPassword.error =
                "Confirma la contraseña"

            etConfirmPassword.requestFocus()

            return
        }

        if (password != confirmPassword) {

            etConfirmPassword.error =
                "Las contraseñas no coinciden"

            etConfirmPassword.requestFocus()

            return
        }

        // -----------------------------------------
        // TÉRMINOS
        // -----------------------------------------

        if (!checkTerms.isChecked) {

            Toast.makeText(
                this,
                "Debes aceptar los lineamientos de privacidad",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        /*
         * =========================================
         * BACKEND - SE IMPLEMENTARÁ DESPUÉS
         * =========================================
         *
         * Aquí posteriormente se realizará algo como:
         *
         * 1. Comprobar que el apelativo esté disponible.
         *
         * 2. Mandar los datos del registro al backend.
         *
         * 3. Solicitar el envío del SMS.
         *
         * Ejemplo futuro:
         *
         * api.sendVerificationCode(
         *     apelativo,
         *     phone,
         *     password
         * )
         *
         * Por ahora solamente navegamos
         * a la pantalla de verificación.
         */

        goToVerification(
            apelativo = apelativo,
            phone = phone
        )
    }

    /**
     * Abre la pantalla de verificación SMS.
     */
    private fun goToVerification(
        apelativo: String,
        phone: String
    ) {

        val intent =
            Intent(
                this,
                VerificationActivity::class.java
            )

        /*
         * Mandamos los datos que posiblemente
         * necesitaremos durante el resto
         * del proceso de registro.
         */

        intent.putExtra(
            "APELATIVO",
            apelativo
        )

        intent.putExtra(
            "PHONE_NUMBER",
            phone
        )

        startActivity(intent)
    }
}