package com.example.animoon.ui.parents

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView

class ParentIncidentDetailActivity : BaseActivity() {

    companion object {
        const val EXTRA_ALERT_ID = "parent_alert_id"
    }

    private val handler = Handler(Looper.getMainLooper())

    private var leaving = false
    private var guidanceDialog: AlertDialog? = null

    private val expirationCheck = Runnable {
        ensureSession()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (!ensureSession()) return

        val alertId = intent.getStringExtra(EXTRA_ALERT_ID)

        val alert = ParentDemoData.alerts.firstOrNull {
            it.id == alertId
        }

        if (alert == null) {
            Toast.makeText(
                this,
                "No se encontró la alerta.",
                Toast.LENGTH_SHORT
            ).show()

            finish()
            return
        }

        setContentView(R.layout.activity_parent_incident_detail)

        findViewById<TextView>(R.id.txtIncidentTitle).text =
            alert.title

        findViewById<TextView>(R.id.txtIncidentDate).text =
            alert.dateLabel

        findViewById<TextView>(R.id.txtIncidentSummary).text =
            alert.summary

        renderMessages(alert.id)

        findViewById<MaterialButton>(R.id.btnIncidentBack)
            .setOnClickListener {
                if (ensureSession()) {
                    finish()
                }
            }

        findViewById<MaterialButton>(R.id.btnIncidentGuidance)
            .setOnClickListener {
                showGuidance(alert.id)
            }
    }

    private fun renderMessages(alertId: String) {
        val messages = ParentIncidentDemoContent.messagesFor(alertId)

        val container =
            findViewById<LinearLayout>(R.id.containerIncidentMessages)

        container.removeAllViews()

        findViewById<TextView>(R.id.txtIncidentMessageCount).text =
            if (messages.isEmpty()) {
                "El registro de mensajes no está disponible."
            } else {
                "${messages.size} mensajes de muestra · Máximo 20"
            }

        messages.forEach { message ->
            val item = layoutInflater.inflate(
                R.layout.item_parent_incident_message,
                container,
                false
            ) as MaterialCardView

            val backgroundColor =
                if (message.fromChild) "#EEF7FB" else "#F5EFFA"

            item.setCardBackgroundColor(
                Color.parseColor(backgroundColor)
            )

            val participant =
                if (message.fromChild) {
                    "${message.author} (menor)"
                } else {
                    message.author
                }

            item.findViewById<TextView>(
                R.id.txtIncidentMessageAuthor
            ).text = "$participant · ${message.time}"

            item.findViewById<TextView>(
                R.id.txtIncidentMessageBody
            ).text = message.text

            container.addView(item)
        }
    }

    private fun showGuidance(alertId: String) {
        if (!ensureSession()) return

        guidanceDialog?.dismiss()

        val dialog = ParentGuidanceDialog.create(
            activity = this,
            title = "¿Qué puedo hacer?",
            message = ParentIncidentDemoContent.guidanceFor(alertId),
            onInteraction = {
                if (ensureSession()) {
                    recordInteraction()
                    true
                } else {
                    false
                }
            }
        )

        guidanceDialog = dialog

        dialog.show()
        ajustarTamanoDialogo(dialog)
    }

    override fun onResume() {
        super.onResume()

        if (!isFinishing && !leaving) {
            ensureSession()
        }
    }

    override fun onUserInteraction() {
        super.onUserInteraction()
        recordInteraction()
    }

    private fun recordInteraction() {
        if (leaving || isFinishing) return

        if (ParentDemoSession.remainingMillis() <= 0L) {
            returnToExpiredDashboard()
            return
        }

        ParentDemoSession.registerInteraction()
        scheduleExpiration()
    }

    private fun ensureSession(): Boolean {
        if (leaving || isFinishing) return false

        if (ParentDemoSession.remainingMillis() <= 0L) {
            returnToExpiredDashboard()
            return false
        }

        scheduleExpiration()
        return true
    }

    private fun scheduleExpiration() {
        handler.removeCallbacks(expirationCheck)

        if (!leaving && !isFinishing) {
            handler.postDelayed(
                expirationCheck,
                ParentDemoSession.remainingMillis().coerceAtLeast(1L)
            )
        }
    }

    private fun returnToExpiredDashboard() {
        if (leaving) return

        leaving = true
        handler.removeCallbacks(expirationCheck)

        guidanceDialog?.dismiss()
        guidanceDialog = null

        ParentDemoSession.clear()

        // Retira el detalle de la pila. El panel detectará que
        // la sesión venció y abrirá la verificación.
        startActivity(
            Intent(this, ParentDashboardActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
                        Intent.FLAG_ACTIVITY_SINGLE_TOP
            }
        )

        finish()
    }

    override fun onPause() {
        handler.removeCallbacks(expirationCheck)
        super.onPause()
    }

    override fun onDestroy() {
        handler.removeCallbacks(expirationCheck)

        guidanceDialog?.dismiss()
        guidanceDialog = null

        super.onDestroy()
    }
}