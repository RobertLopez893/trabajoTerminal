package com.example.animoon.ui.parents

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AlertDialog
import androidx.core.view.isVisible
import com.example.animoon.R
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class ParentDashboardActivity : BaseActivity() {

    private val handler = Handler(Looper.getMainLooper())

    private var leaving = false
    private var activeDialog: AlertDialog? = null

    private val expirationCheck = Runnable {
        checkSession()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (ParentDemoSession.remainingMillis() <= 0L) {
            openVerification()
            return
        }

        setContentView(R.layout.activity_parent_dashboard)

        findViewById<TextView>(R.id.txtParentChildName).text =
            ParentDemoData.childNickname

        findViewById<TextView>(R.id.txtParentChildDescription).text =
            ParentDemoData.childDescription

        renderAlerts()

        findViewById<MaterialButton>(R.id.btnParentGeneralGuidance)
            .setOnClickListener {
                showGeneralGuidance()
            }

        findViewById<MaterialButton>(R.id.btnParentExit)
            .setOnClickListener {
                confirmExit()
            }

        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    confirmExit()
                }
            }
        )
    }

    private fun renderAlerts() {
        val alerts = ParentDemoData.alerts

        val container =
            findViewById<LinearLayout>(R.id.containerParentAlerts)

        container.removeAllViews()

        findViewById<TextView>(R.id.txtParentAlertCount).text =
            when (alerts.size) {
                0 -> "Sin alertas"
                1 -> "1 alerta de muestra"
                else -> "${alerts.size} alertas de muestra · Más recientes primero"
            }

        findViewById<TextView>(R.id.txtParentEmpty).isVisible =
            alerts.isEmpty()

        alerts.forEach { alert ->
            val item = layoutInflater.inflate(
                R.layout.item_parent_alert,
                container,
                false
            )

            item.findViewById<TextView>(R.id.txtAlertDate).text =
                alert.dateLabel

            item.findViewById<TextView>(R.id.txtAlertTitle).text =
                alert.title

            item.findViewById<TextView>(R.id.txtAlertSummary).text =
                alert.summary

            item.findViewById<MaterialButton>(R.id.btnAlertSummary)
                .apply {
                    contentDescription = "Consultar alerta: ${alert.title}"

                    setOnClickListener {
                        showAlertSummary(alert)
                    }
                }

            container.addView(item)
        }
    }

    private fun showAlertSummary(alert: ParentAlert) {
        if (!checkSession()) return

        ParentDemoSession.registerInteraction()
        scheduleExpiration()

        startActivity(
            Intent(this, ParentIncidentDetailActivity::class.java)
                .putExtra(
                    ParentIncidentDetailActivity.EXTRA_ALERT_ID,
                    alert.id
                )
        )
    }

    private fun confirmExit() {
        if (!checkSession()) return

        activeDialog?.dismiss()

        activeDialog = MaterialAlertDialogBuilder(this)
            .setTitle("¿Salir del panel?")
            .setMessage(
                "Volverás a Ajustes. Para entrar nuevamente " +
                        "se solicitará otro código de verificación."
            )
            .setNegativeButton("Permanecer") { _, _ ->
                if (checkSession()) {
                    ParentDemoSession.registerInteraction()
                    scheduleExpiration()
                }
            }
            .setPositiveButton("Salir") { _, _ ->
                leaving = true
                handler.removeCallbacks(expirationCheck)
                ParentDemoSession.clear()
                finish()
            }
            .create()

        activeDialog?.show()
    }

    override fun onResume() {
        super.onResume()

        if (!leaving) {
            checkSession()
        }
    }

    override fun onUserInteraction() {
        super.onUserInteraction()

        if (leaving) return

        if (ParentDemoSession.remainingMillis() <= 0L) {
            openVerification()
            return
        }

        ParentDemoSession.registerInteraction()
        scheduleExpiration()
    }

    private fun checkSession(): Boolean {
        if (leaving) return false

        if (ParentDemoSession.remainingMillis() <= 0L) {
            openVerification()
            return false
        }

        scheduleExpiration()
        return true
    }

    private fun scheduleExpiration() {
        handler.removeCallbacks(expirationCheck)

        if (!leaving) {
            handler.postDelayed(
                expirationCheck,
                ParentDemoSession.remainingMillis().coerceAtLeast(1L)
            )
        }
    }

    private fun openVerification() {
        if (leaving) return

        leaving = true
        handler.removeCallbacks(expirationCheck)
        activeDialog?.dismiss()
        activeDialog = null

        ParentDemoSession.clear()

        startActivity(
            Intent(this, ParentVerificationActivity::class.java)
        )

        finish()
    }

    private fun showGeneralGuidance() {
        if (!checkSession()) return

        activeDialog?.dismiss()

        val dialog = ParentGuidanceDialog.create(
            activity = this,
            title = "Consejos para padres y tutores",
            message = ParentIncidentDemoContent.generalGuidance,
            onInteraction = {
                if (checkSession()) {
                    ParentDemoSession.registerInteraction()
                    scheduleExpiration()
                    true
                } else {
                    false
                }
            }
        )

        activeDialog = dialog

        dialog.show()
        ajustarTamanoDialogo(dialog)
    }

    override fun onPause() {
        handler.removeCallbacks(expirationCheck)
        super.onPause()
    }

    override fun onDestroy() {
        handler.removeCallbacks(expirationCheck)
        activeDialog?.dismiss()
        activeDialog = null
        super.onDestroy()
    }
}