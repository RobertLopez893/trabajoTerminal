package com.example.animoon.ui.parents

import android.os.Bundle
import android.os.CountDownTimer
import android.os.SystemClock
import android.view.inputmethod.EditorInfo
import android.widget.TextView
import androidx.core.widget.doAfterTextChanged
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import java.util.Locale
import android.content.Intent

class ParentVerificationActivity : BaseActivity() {

    companion object {
        // Solo para esta demostración del frontend.
        private const val DEMO_CODE = "123456"
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
                verifyDemoCode()
                true
            } else {
                false
            }
        }

        verifyButton.setOnClickListener {
            verifyDemoCode()
        }

        resendButton.setOnClickListener {
            restartDemoCode()
        }

        findViewById<MaterialButton>(R.id.btnParentBack)
            .setOnClickListener {
                finish()
            }
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
                // La fecha de vencimiento es la referencia principal.
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
        timerText.text = "Código de prueba utilizado."
        verifyButton.isEnabled = false
        resendButton.isEnabled = true
        codeEditText.isEnabled = false
    }

    private fun restartDemoCode() {
        // Simula un nuevo código, sin llamadas de red.
        codeUsed = false
        expiresAt = SystemClock.elapsedRealtime() + CODE_VALIDITY_MS

        codeEditText.text?.clear()
        codeInput.error = null

        startTimer()
        codeEditText.requestFocus()
    }

    private fun verifyDemoCode() {
        if (codeUsed) return

        if (SystemClock.elapsedRealtime() >= expiresAt) {
            showExpiredCodeState()
            return
        }

        val enteredCode = codeEditText.text?.toString().orEmpty()

        if (enteredCode.length != 6) {
            codeInput.error = "Ingresa los 6 dígitos del código."
            return
        }

        if (enteredCode != DEMO_CODE) {
            codeInput.error = "Código incorrecto. Intenta nuevamente."
            return
        }

        codeUsed = true
        countDownTimer?.cancel()
        countDownTimer = null

        codeEditText.text?.clear()
        showUsedCodeState()

        showDemoSuccess()
    }

    private fun showDemoSuccess() {
        ParentDemoSession.start()

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