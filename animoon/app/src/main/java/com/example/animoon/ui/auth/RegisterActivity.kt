package com.example.animoon.ui.auth

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.text.SpannableString
import android.text.Spanned
import android.text.TextPaint
import android.text.style.ClickableSpan
import android.view.MotionEvent
import android.view.View
import android.widget.CheckBox
import android.widget.TextView
import android.widget.Toast
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import androidx.core.widget.doAfterTextChanged
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class RegisterActivity : BaseActivity() {
    override val observarSesionExpirada: Boolean = false

    companion object {
        private const val SPECIAL_CHARACTERS = "!@#$%^&*(),.?\":{}|<>_-+=[]\\;'/`~"
    }

    private lateinit var tilRegisterApelativo: TextInputLayout
    private lateinit var tilTutorPhone: TextInputLayout
    private lateinit var tilRegisterPassword: TextInputLayout
    private lateinit var tilConfirmPassword: TextInputLayout

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
        configurePrivacyLinks()
        configureListeners()
    }

    /**
     * Relaciona las variables Kotlin con los elementos
     * definidos en activity_register.xml.
     */
    private fun initViews() {

        tilRegisterApelativo =
            findViewById(R.id.tilRegisterApelativo)

        tilTutorPhone =
            findViewById(R.id.tilTutorPhone)

        tilRegisterPassword =
            findViewById(R.id.tilRegisterPassword)

        tilConfirmPassword =
            findViewById(R.id.tilConfirmPassword)

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
     * Configura el enlace dentro del texto del CheckBox para abrir
     * el Aviso de Privacidad con cambio rápido de pantalla, sin marcar
     * o desmarcar por error la casilla.
     */
    private fun configurePrivacyLinks() {
        val fullText = "El tutor acepta los lineamientos de privacidad y uso de datos."
        val linkText = "lineamientos de privacidad y uso de datos"
        val startIndex = fullText.indexOf(linkText)

        if (startIndex >= 0) {
            val spannable = SpannableString(fullText)
            val clickableSpan = object : ClickableSpan() {
                override fun onClick(widget: View) {
                    openPrivacyNotice()
                }

                override fun updateDrawState(ds: TextPaint) {
                    super.updateDrawState(ds)
                    ds.color = Color.parseColor("#7951B0")
                    ds.isUnderlineText = true
                    ds.isFakeBoldText = true
                }
            }

            spannable.setSpan(
                clickableSpan,
                startIndex,
                startIndex + linkText.length,
                Spanned.SPAN_EXCLUSIVE_EXCLUSIVE
            )

            checkTerms.text = spannable

            checkTerms.setOnTouchListener { view, event ->
                val textView = view as TextView
                val layout = textView.layout ?: return@setOnTouchListener false

                val x = event.x.toInt() - textView.totalPaddingLeft + textView.scrollX
                val y = event.y.toInt() - textView.totalPaddingTop + textView.scrollY

                if (x >= 0 && y >= 0 && y <= layout.height) {
                    val line = layout.getLineForVertical(y)
                    if (x <= layout.getLineRight(line)) {
                        val offset = layout.getOffsetForHorizontal(line, x.toFloat())
                        val spans = spannable.getSpans(offset, offset, ClickableSpan::class.java)
                        if (spans.isNotEmpty()) {
                            if (event.action == MotionEvent.ACTION_UP) {
                                spans[0].onClick(textView)
                            }
                            return@setOnTouchListener true
                        }
                    }
                }
                false
            }
        }
    }

    private fun openPrivacyNotice() {
        val intent = Intent(this, PrivacyNoticeActivity::class.java)
        startActivity(intent)
        overridePendingTransition(0, 0)
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

        etRegisterApelativo.doAfterTextChanged {
            tilRegisterApelativo.error = null
        }

        etTutorPhone.doAfterTextChanged {
            tilTutorPhone.error = null
        }

        etRegisterPassword.doAfterTextChanged {
            tilRegisterPassword.error = null
        }

        etConfirmPassword.doAfterTextChanged {
            tilConfirmPassword.error = null
        }
    }

    private fun validatePasswordSecurity(password: String): String? {
        if (password.isEmpty()) {
            return "Ingresa una contraseña"
        }
        if (password.length < 8) {
            return "La contraseña debe tener al menos 8 caracteres"
        }
        if (!password.any { it.isUpperCase() }) {
            return "Debe incluir al menos una letra mayúscula (A-Z)"
        }
        if (!password.any { it.isLowerCase() }) {
            return "Debe incluir al menos una letra minúscula (a-z)"
        }
        if (!password.any { it.isDigit() }) {
            return "Debe incluir al menos un número (0-9)"
        }
        if (!password.any { it in SPECIAL_CHARACTERS }) {
            return "Debe incluir al menos un símbolo especial (ej. !@#$%*)"
        }
        return null
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

        // Limpiar errores previos
        tilRegisterApelativo.error = null
        tilTutorPhone.error = null
        tilRegisterPassword.error = null
        tilConfirmPassword.error = null

        // -----------------------------------------
        // APelativo
        // -----------------------------------------

        if (apelativo.isEmpty()) {

            tilRegisterApelativo.error =
                "Ingresa un apelativo"

            etRegisterApelativo.requestFocus()

            return
        }

        // -----------------------------------------
        // TELÉFONO
        // -----------------------------------------

        if (phone.isEmpty()) {

            tilTutorPhone.error =
                "Ingresa el número del tutor"

            etTutorPhone.requestFocus()

            return
        }

        if (phone.length != 10 ||
            !phone.all { it.isDigit() }
        ) {

            tilTutorPhone.error =
                "Ingresa un número de 10 dígitos"

            etTutorPhone.requestFocus()

            return
        }

        // -----------------------------------------
        // CONTRASEÑA Y FILTROS DE SEGURIDAD
        // -----------------------------------------

        val passwordError = validatePasswordSecurity(password)
        if (passwordError != null) {

            tilRegisterPassword.error = passwordError

            etRegisterPassword.requestFocus()

            return
        }

        // -----------------------------------------
        // CONFIRMAR CONTRASEÑA
        // -----------------------------------------

        if (confirmPassword.isEmpty()) {

            tilConfirmPassword.error =
                "Confirma la contraseña"

            etConfirmPassword.requestFocus()

            return
        }

        if (password != confirmPassword) {

            tilConfirmPassword.error =
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

        // Llamadas al API (Corrutina)
        btnSendSms.isEnabled = false
        showLoading("Comprobando apelativo...")
        lifecycleScope.launch {
            try {
                // 1. Verificar apelativo
                val nicknameReq = com.example.animoon.data.model.NicknameCheckRequest(apelativo)
                val nicknameRes = com.example.animoon.data.network.ApiClient.authService.verifyNickname(nicknameReq)
                
                if (!nicknameRes.isSuccessful) {
                    hideLoading()
                    Toast.makeText(this@RegisterActivity, "El apelativo ya está en uso", Toast.LENGTH_SHORT).show()
                    btnSendSms.isEnabled = true
                    return@launch
                }

                // 2. Enviar SMS
                val smsReq = com.example.animoon.data.model.SmsSendRequest(apelativo, phone)
                val smsRes = com.example.animoon.data.network.ApiClient.authService.sendSmsCode(smsReq)
                
                if (!smsRes.isSuccessful) {
                    hideLoading()
                    Toast.makeText(this@RegisterActivity, "Error al enviar SMS", Toast.LENGTH_SHORT).show()
                    btnSendSms.isEnabled = true
                    return@launch
                }

                // 3. Continuar a la verificación SMS
                hideLoading()
                goToVerification(apelativo, phone, password)
            } catch (e: Exception) {
                hideLoading()
                Toast.makeText(this@RegisterActivity, "Error de red: ${e.message}", Toast.LENGTH_SHORT).show()
                btnSendSms.isEnabled = true
            }
        }
    }

    /**
     * Abre la pantalla de verificación SMS.
     */
    private fun goToVerification(
        apelativo: String,
        phone: String,
        password: String
    ) {

        val intent =
            Intent(
                this,
                VerificationActivity::class.java
            )

        intent.putExtra("APELATIVO", apelativo)
        intent.putExtra("PHONE_NUMBER", phone)
        intent.putExtra("PASSWORD", password)

        startActivity(intent)
    }
}
