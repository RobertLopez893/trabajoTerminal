package com.example.animoon.ui.parents

import android.content.Intent
import android.os.Bundle
import android.os.CountDownTimer
import android.os.SystemClock
import android.view.inputmethod.EditorInfo
import android.widget.TextView
import androidx.core.widget.doAfterTextChanged
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.ParentVerifyCodeRequest
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

class ParentVerificationActivity : BaseActivity() {

    companion object {
        private const val CODE_VALIDITY_MS = 120_000L
        private const val STATE_EXPIRES_AT = "parent_code_expires_at"
        private const val STATE_CODE_USED = "parent_code_used"
    }

    private lateinit var codeInput: TextInputLayout
    private lateinit var codeEditText: TextInputEditText
    private lateinit var timerText: TextView
    private lateinit var verifyButton: MaterialButton
    private lateinit var resendButton: MaterialButton

    private var countDownTimer: CountDownTimer? = null
    private var expiresAt = 0L
    private var codeUsed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_parent_verification)

        codeInput = findViewById(R.id.inputParentCode)
        codeEditText = findViewById(R.id.edtParentCode)
        timerText = findViewById(R.id.txtParentCodeTimer)
        verifyButton = findViewById(R.id.btnParentVerify)
        resendButton = findViewById(R.id.btnParentResend)

        expiresAt = savedInstanceState?.getLong(STATE_EXPIRES_AT)
            ?: (SystemClock.elapsedRealtime() + CODE_VALIDITY_MS)

        codeUsed = savedInstanceState?.getBoolean(STATE_CODE_USED)
            ?: false

        codeEditText.doAfterTextChanged {
            codeInput.error = null
        }

        codeEditText.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                verificarCodigo()
                true
            } else {
                false
            }
        }

        verifyButton.setOnClickListener {
            verificarCodigo()
        }

        resendButton.setOnClickListener {
            solicitarCodigoSms()
        }

        findViewById<MaterialButton>(R.id.btnParentBack)
            .setOnClickListener {
                finish()
            }

        // Solicitar código inicial al cargar la pantalla
        solicitarCodigoSms()
    }

    override fun onResume() {
        super.onResume()
        startTimer()
    }

    override fun onPause() {
        countDownTimer?.cancel()
        countDownTimer = null
        super.onPause()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putLong(STATE_EXPIRES_AT, expiresAt)
        outState.putBoolean(STATE_CODE_USED, codeUsed)
        super.onSaveInstanceState(outState)
    }

    private fun solicitarCodigoSms() {
        verifyButton.isEnabled = false
        resendButton.isEnabled = false
        codeEditText.isEnabled = false
        timerText.text = "Enviando código SMS al tutor..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = ApiClient.parentService.requestCode()
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val body = response.body()!!
                        expiresAt = SystemClock.elapsedRealtime() + (body.expiresInSeconds * 1000L)
                        codeUsed = false
                        codeEditText.text?.clear()
                        codeInput.error = null
                        codeInput.helperText = "Enviado al ${body.maskedPhone}"
                        startTimer()
                        codeEditText.requestFocus()
                    } else {
                        // Fallback con timer si hay error transitorio
                        expiresAt = SystemClock.elapsedRealtime() + CODE_VALIDITY_MS
                        codeUsed = false
                        codeInput.helperText = "Usa tu código SMS o el código 123456"
                        startTimer()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    expiresAt = SystemClock.elapsedRealtime() + CODE_VALIDITY_MS
                    codeUsed = false
                    codeInput.helperText = "Modo local: Usa el código 123456"
                    startTimer()
                }
            }
        }
    }

    private fun startTimer() {
        countDownTimer?.cancel()

        if (codeUsed) {
            showUsedCodeState()
            return
        }

        val remaining = expiresAt - SystemClock.elapsedRealtime()

        if (remaining <= 0L) {
            showExpiredCodeState()
            return
        }

        verifyButton.isEnabled = true
        resendButton.isEnabled = false
        codeEditText.isEnabled = true

        updateTimerText(remaining)

        countDownTimer = object : CountDownTimer(remaining, 1_000L) {
            override fun onTick(millisUntilFinished: Long) {
                val timeLeft = expiresAt - SystemClock.elapsedRealtime()

                if (timeLeft > 0L) {
                    updateTimerText(timeLeft)
                } else {
                    showExpiredCodeState()
                }
            }

            override fun onFinish() {
                showExpiredCodeState()
            }
        }.start()
    }

    private fun updateTimerText(remaining: Long) {
        val seconds = (remaining + 999L) / 1_000L

        val formattedTime = String.format(
            Locale.getDefault(),
            "%02d:%02d",
            seconds / 60,
            seconds % 60
        )

        timerText.text = "El código vence en $formattedTime"
    }

    private fun showExpiredCodeState() {
        countDownTimer?.cancel()
        countDownTimer = null

        timerText.text = "El código venció. Solicita uno nuevo."
        verifyButton.isEnabled = false
        resendButton.isEnabled = true
        codeEditText.isEnabled = false
    }

    private fun showUsedCodeState() {
        timerText.text = "Código de verificación utilizado."
        verifyButton.isEnabled = false
        resendButton.isEnabled = true
        codeEditText.isEnabled = false
    }

    private fun verificarCodigo() {
        if (codeUsed) return

        if (SystemClock.elapsedRealtime() >= expiresAt) {
            showExpiredCodeState()
            return
        }

        val enteredCode = codeEditText.text?.toString().orEmpty().trim()

        if (enteredCode.length != 6) {
            codeInput.error = "Ingresa los 6 dígitos del código."
            return
        }

        verifyButton.isEnabled = false
        codeEditText.isEnabled = false
        timerText.text = "Validando código de seguridad..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = ApiClient.parentService.verifyCode(
                    ParentVerifyCodeRequest(codigo = enteredCode)
                )

                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val body = response.body()!!
                        codeUsed = true
                        countDownTimer?.cancel()
                        countDownTimer = null

                        ParentDemoSession.start(body.parentToken)
                        abrirDashboard()
                    } else {
                        // Si el backend devuelve error de validación
                        verifyButton.isEnabled = true
                        codeEditText.isEnabled = true
                        startTimer()
                        codeInput.error = "Código incorrecto. Intenta nuevamente."
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    // Fallback para pruebas sin conexión
                    if (enteredCode == "123456" || enteredCode == "000000") {
                        codeUsed = true
                        countDownTimer?.cancel()
                        countDownTimer = null
                        ParentDemoSession.start("OFFLINE_DEMO_PARENT_TOKEN")
                        abrirDashboard()
                    } else {
                        verifyButton.isEnabled = true
                        codeEditText.isEnabled = true
                        startTimer()
                        codeInput.error = "Código incorrecto o sin conexión."
                    }
                }
            }
        }
    }

    private fun abrirDashboard() {
        startActivity(
            Intent(this, ParentDashboardActivity::class.java)
        )
        finish()
    }

    override fun onDestroy() {
        countDownTimer?.cancel()
        countDownTimer = null
        super.onDestroy()
    }
}
