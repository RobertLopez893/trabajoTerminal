package com.example.animoon.ui.auth

import android.content.Intent
import android.os.Bundle
import android.os.CountDownTimer
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.R
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import androidx.core.widget.doAfterTextChanged

class VerificationActivity : BaseActivity() {
    override val observarSesionExpirada: Boolean = false


    private lateinit var edtCode1: EditText
    private lateinit var edtCode2: EditText
    private lateinit var edtCode3: EditText
    private lateinit var edtCode4: EditText
    private lateinit var edtCode5: EditText
    private lateinit var edtCode6: EditText

    private lateinit var btnVerify: Button
    private lateinit var btnBack: Button
    private lateinit var txtResend: TextView
    private lateinit var txtPhone: TextView

    private var canResend = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_verification)

        initViews()

        val phoneNumber = intent.getStringExtra("PHONE_NUMBER")

        if (!phoneNumber.isNullOrEmpty()) {
            txtPhone.text = maskPhone(phoneNumber)
        }

        configureCodeInputs()

        btnVerify.setOnClickListener {
            verifyCode()
        }

        btnBack.setOnClickListener {
            finish()
        }

        txtResend.setOnClickListener {
            if (canResend) {
                resendCode()
            }
        }

        startResendTimer()
    }

    private fun initViews() {
        edtCode1 = findViewById(R.id.edtCode1)
        edtCode2 = findViewById(R.id.edtCode2)
        edtCode3 = findViewById(R.id.edtCode3)
        edtCode4 = findViewById(R.id.edtCode4)
        edtCode5 = findViewById(R.id.edtCode5)
        edtCode6 = findViewById(R.id.edtCode6)

        btnVerify = findViewById(R.id.btnVerify)
        btnBack = findViewById(R.id.btnBack)
        txtResend = findViewById(R.id.txtResend)
        txtPhone = findViewById(R.id.txtPhone)
    }

    private fun configureCodeInputs() {
        val inputs = listOf(
            edtCode1,
            edtCode2,
            edtCode3,
            edtCode4,
            edtCode5,
            edtCode6
        )

        inputs.forEachIndexed { index, editText ->
            editText.doAfterTextChanged { text ->
                if (
                    editText.hasFocus() &&
                    text?.length == 1 &&
                    index < inputs.lastIndex
                ) {
                    inputs[index + 1].requestFocus()
                }
            }
        }
    }

    private fun verifyCode() {

        val code =
            edtCode1.text.toString() +
                    edtCode2.text.toString() +
                    edtCode3.text.toString() +
                    edtCode4.text.toString() +
                    edtCode5.text.toString() +
                    edtCode6.text.toString()

        if (code.length != 6) {

            Toast.makeText(
                this,
                "Ingresa los 6 números del código",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        // Recuperar datos
        val phoneNumber = intent.getStringExtra("PHONE_NUMBER") ?: ""
        val apelativo = intent.getStringExtra("APELATIVO") ?: ""
        val password = intent.getStringExtra("PASSWORD") ?: ""

        btnVerify.isEnabled = false
        showLoading("Verificando código de seguridad...")

        lifecycleScope.launch {
            try {
                val req = com.example.animoon.data.model.SmsVerifyRequest(
                    telefono = phoneNumber,
                    codigo_verificacion = code,
                    nickname = apelativo
                )
                val response = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                    com.example.animoon.data.network.ApiClient.authService.verifySmsCode(req)
                }

                hideLoading()
                btnVerify.isEnabled = true

                if (response.isSuccessful) {
                    val intent = Intent(
                        this@VerificationActivity,
                        AvatarSelectionActivity::class.java
                    )
                    intent.putExtra("PHONE_NUMBER", phoneNumber)
                    intent.putExtra("APELATIVO", apelativo)
                    intent.putExtra("PASSWORD", password)
                    intent.putExtra("VERIFICATION_CODE", code)

                    startActivity(intent)
                } else {
                    var errorDetail = "El código ingresado es incorrecto o ha expirado."
                    try {
                        val errorJson = response.errorBody()?.string()
                        if (!errorJson.isNullOrBlank()) {
                            val json = org.json.JSONObject(errorJson)
                            if (json.has("detail")) {
                                errorDetail = json.getString("detail")
                            }
                        }
                    } catch (_: Exception) {}

                    Toast.makeText(
                        this@VerificationActivity,
                        errorDetail,
                        Toast.LENGTH_LONG
                    ).show()

                    edtCode1.text?.clear()
                    edtCode2.text?.clear()
                    edtCode3.text?.clear()
                    edtCode4.text?.clear()
                    edtCode5.text?.clear()
                    edtCode6.text?.clear()
                    edtCode1.requestFocus()
                }
            } catch (e: Exception) {
                hideLoading()
                btnVerify.isEnabled = true
                Toast.makeText(
                    this@VerificationActivity,
                    "Error de conexión al verificar el código",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun resendCode() {
        val phoneNumber = intent.getStringExtra("PHONE_NUMBER") ?: ""
        val apelativo = intent.getStringExtra("APELATIVO") ?: ""

        lifecycleScope.launch {
            try {
                val req = com.example.animoon.data.model.SmsSendRequest(apelativo, phoneNumber)
                val res = com.example.animoon.data.network.ApiClient.authService.sendSmsCode(req)
                if (res.isSuccessful) {
                    Toast.makeText(this@VerificationActivity, "Código reenviado", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@VerificationActivity, "Error al reenviar SMS", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@VerificationActivity, "Error de red", Toast.LENGTH_SHORT).show()
            }
        }
        startResendTimer()
    }

    private fun startResendTimer() {

        canResend = false

        object : CountDownTimer(120000, 1000) {

            override fun onTick(millisUntilFinished: Long) {

                val seconds = millisUntilFinished / 1000
                val minutes = seconds / 60
                val remainingSeconds = seconds % 60

                txtResend.text =
                    "Reenviar código en %02d:%02d".format(
                        minutes,
                        remainingSeconds
                    )
            }

            override fun onFinish() {

                canResend = true
                txtResend.text = "Reenviar código"
            }

        }.start()
    }

    private fun maskPhone(phone: String): String {

        if (phone.length < 4) {
            return phone
        }

        return "+52 •••••• ${phone.takeLast(4)}"
    }
}