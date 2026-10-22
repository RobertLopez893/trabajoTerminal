package com.example.animoon.ui.admin

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AlertDialog
import androidx.core.view.isVisible
import androidx.lifecycle.lifecycleScope
import com.example.animoon.BuildConfig
import com.example.animoon.R
import com.example.animoon.ui.auth.LoginActivity
import com.example.animoon.ui.base.BaseActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.DateFormat
import java.util.Date

class AdminAppealsActivity : BaseActivity() {

    // La sesión administrativa de prueba es independiente
    // de la sesión del jugador observada en BaseActivity.
    override val observarSesionExpirada: Boolean = false

    private lateinit var repository: AdminDemoRepository
    private lateinit var reasonEdit: EditText
    private lateinit var errorText: TextView

    private var selectedId: String? = null
    private var busy = false
    private var activeDialog: AlertDialog? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (!BuildConfig.DEBUG || !AdminDemoSession.isActive) {
            returnToLogin()
            return
        }

        setContentView(R.layout.activity_admin_appeals)

        repository = AdminDemoRepository(this)
        reasonEdit = findViewById(R.id.edtAdminReason)
        errorText = findViewById(R.id.txtAdminError)

        findViewById<MaterialButton>(R.id.btnAdminLogout)
            .setOnClickListener {
                confirmLogout()
            }

        findViewById<MaterialButton>(R.id.btnAdminBack)
            .setOnClickListener {
                leaveDetail()
            }

        findViewById<MaterialButton>(R.id.btnAdminReview)
            .setOnClickListener {
                val id = selectedId ?: return@setOnClickListener

                runOperation(
                    operation = { repository.markInReview(id) },
                    onSuccess = { renderDetail(id) }
                )
            }

        findViewById<MaterialButton>(R.id.btnAdminApprove)
            .setOnClickListener {
                confirmResolution(approved = true)
            }

        findViewById<MaterialButton>(R.id.btnAdminReject)
            .setOnClickListener {
                confirmResolution(approved = false)
            }

        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    if (busy) return

                    if (selectedId != null) {
                        leaveDetail()
                    } else {
                        confirmLogout()
                    }
                }
            }
        )

        val restoredId = savedInstanceState?.getString("selected_id")

        if (
            restoredId != null &&
            repository.find(restoredId) != null
        ) {
            openDetail(restoredId)

            if (repository.find(restoredId)?.status?.isResolved == false) {
                reasonEdit.setText(
                    savedInstanceState?.getString("reason_draft").orEmpty()
                )
            }
        } else {
            showList()
        }
    }

    override fun onResume() {
        super.onResume()

        if (!isFinishing && !AdminDemoSession.isActive) {
            returnToLogin()
        }
    }

    private fun showList() {
        selectedId = null

        findViewById<View>(R.id.panelAdminList).isVisible = true
        findViewById<View>(R.id.panelAdminDetail).isVisible = false

        errorText.isVisible = false

        val appeals = repository.getAll()

        val pending = appeals.count {
            it.status == AdminAppealStatus.PENDING
        }

        val reviewing = appeals.count {
            it.status == AdminAppealStatus.IN_REVIEW
        }

        val resolved = appeals.count {
            it.status.isResolved
        }

        findViewById<TextView>(R.id.txtAdminCounts).text =
            "Pendientes: $pending   ·   En revisión: $reviewing   ·   Resueltas: $resolved"

        val container =
            findViewById<LinearLayout>(R.id.containerAdminAppeals)

        container.removeAllViews()

        appeals.forEach { appeal ->
            val item = layoutInflater.inflate(
                R.layout.item_admin_appeal,
                container,
                false
            )

            item.findViewById<TextView>(R.id.txtAdminItemTitle).text =
                appeal.nickname

            item.findViewById<TextView>(R.id.txtAdminItemMeta).text =
                "${appeal.id} · ${appeal.date}"

            item.findViewById<TextView>(R.id.txtAdminItemStatus).text =
                appeal.status.label

            item.findViewById<MaterialButton>(R.id.btnAdminItemOpen)
                .setOnClickListener {
                    if (!busy) {
                        openDetail(appeal.id)
                    }
                }

            container.addView(item)
        }
    }

    private fun openDetail(id: String) {
        selectedId = id

        reasonEdit.text.clear()
        reasonEdit.error = null
        errorText.isVisible = false

        findViewById<View>(R.id.panelAdminList).isVisible = false
        findViewById<View>(R.id.panelAdminDetail).isVisible = true

        renderDetail(id)
    }

    private fun renderDetail(id: String) {
        val appeal = repository.find(id)

        if (appeal == null) {
            showList()
            errorText.text = "No se encontró la apelación."
            errorText.isVisible = true
            return
        }

        findViewById<TextView>(R.id.txtAdminDetailTitle).text =
            "${appeal.id} · ${appeal.nickname}"

        findViewById<TextView>(R.id.txtAdminDetailMeta).text =
            "${appeal.date}\nEstado: ${appeal.status.label}"

        findViewById<TextView>(R.id.txtAdminIncident).text =
            "Incidencia: ${appeal.incident}"

        findViewById<TextView>(R.id.txtAdminExplanation).text =
            appeal.explanation

        findViewById<TextView>(R.id.txtAdminEvidence).text =
            appeal.evidence

        findViewById<View>(R.id.panelAdminActions).isVisible =
            !appeal.status.isResolved

        findViewById<View>(R.id.btnAdminReview).isVisible =
            appeal.status == AdminAppealStatus.PENDING

        val resolutionText =
            findViewById<TextView>(R.id.txtAdminResolution)

        resolutionText.isVisible = appeal.status.isResolved

        if (appeal.status.isResolved) {
            val date = DateFormat.getDateTimeInstance(
                DateFormat.MEDIUM,
                DateFormat.SHORT
            ).format(Date(appeal.resolvedAt))

            resolutionText.text =
                "${appeal.status.label}\n\n" +
                        "${appeal.resolution}\n\n" +
                        "Registrada por: ${appeal.resolvedBy}\n" +
                        "$date\n\n" +
                        "Decisión de demostración. No modifica cuentas reales."
        }
    }

    private fun confirmResolution(approved: Boolean) {
        if (busy || activeDialog?.isShowing == true) return

        val id = selectedId ?: return
        val appeal = repository.find(id) ?: return

        if (appeal.status.isResolved) {
            renderDetail(id)
            return
        }

        val reason = reasonEdit.text.toString().trim()

        if (reason.isBlank()) {
            reasonEdit.error = "Escribe el motivo de la decisión."
            reasonEdit.requestFocus()
            return
        }

        if (reason.length > 500) {
            reasonEdit.error = "Usa un máximo de 500 caracteres."
            return
        }

        val action = if (approved) "aprobar" else "rechazar"

        showDialog(
            dialogBuilder()
                .setTitle("¿Confirmar decisión?")
                .setMessage(
                    "Vas a $action la apelación ${appeal.id}.\n\n" +
                            "La decisión quedará guardada localmente y no " +
                            "podrá modificarse desde este panel.\n\n" +
                            "No se cambiará el acceso de ninguna cuenta real."
                )
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Confirmar") { _, _ ->
                    runOperation(
                        operation = {
                            repository.resolve(id, approved, reason)
                        },
                        onSuccess = {
                            reasonEdit.text.clear()
                            renderDetail(id)
                        }
                    )
                }
                .create()
        )
    }

    private fun runOperation(
        operation: () -> Boolean,
        onSuccess: () -> Unit
    ) {
        if (busy || !AdminDemoSession.isActive) return

        setBusy(true)
        errorText.isVisible = false

        lifecycleScope.launch {
            try {
                val saved = withContext(Dispatchers.IO) {
                    operation()
                }

                if (saved) {
                    onSuccess()
                } else {
                    selectedId?.let { renderDetail(it) }

                    errorText.text =
                        "No se pudo guardar el cambio. " +
                                "La solicitud puede haber sido resuelta."
                    errorText.isVisible = true
                }
            } catch (exception: CancellationException) {
                throw exception
            } catch (_: Exception) {
                errorText.text =
                    "No se pudo guardar el cambio. Intenta nuevamente."
                errorText.isVisible = true
            } finally {
                setBusy(false)
            }
        }
    }

    private fun setBusy(value: Boolean) {
        busy = value

        findViewById<View>(R.id.progressAdmin).isVisible = value
        reasonEdit.isEnabled = !value

        listOf(
            R.id.btnAdminLogout,
            R.id.btnAdminBack,
            R.id.btnAdminReview,
            R.id.btnAdminApprove,
            R.id.btnAdminReject
        ).forEach { id ->
            findViewById<View>(id).isEnabled = !value
        }
    }

    private fun hasDraft(): Boolean {
        val id = selectedId ?: return false
        val appeal = repository.find(id) ?: return false

        return !appeal.status.isResolved &&
                reasonEdit.text.toString().isNotBlank()
    }

    private fun leaveDetail() {
        if (busy || activeDialog?.isShowing == true) return

        if (!hasDraft()) {
            showList()
            return
        }

        showDialog(
            dialogBuilder()
                .setTitle("¿Descartar el motivo escrito?")
                .setMessage(
                    "Todavía no has registrado una decisión. " +
                            "El texto se perderá al volver a la lista."
                )
                .setNegativeButton("Seguir revisando", null)
                .setPositiveButton("Descartar") { _, _ ->
                    reasonEdit.text.clear()
                    showList()
                }
                .create()
        )
    }

    private fun confirmLogout() {
        if (busy || activeDialog?.isShowing == true) return

        val message = if (hasDraft()) {
            "Volverás al inicio de sesión y se descartará " +
                    "el motivo que todavía no has guardado."
        } else {
            "Volverás al inicio de sesión. " +
                    "Las decisiones guardadas se conservarán."
        }

        showDialog(
            dialogBuilder()
                .setTitle("¿Cerrar sesión administrativa?")
                .setMessage(message)
                .setNegativeButton("Permanecer", null)
                .setPositiveButton("Cerrar sesión") { _, _ ->
                    AdminDemoSession.logout()
                    returnToLogin()
                }
                .create()
        )
    }

    private fun dialogBuilder(): MaterialAlertDialogBuilder =
        MaterialAlertDialogBuilder(
            this,
            R.style.ThemeOverlay_Animoon_Admin_Dialog
        )

    private fun showDialog(dialog: AlertDialog) {
        activeDialog?.dismiss()
        activeDialog = dialog

        dialog.show()
        ajustarTamanoDialogo(dialog)
    }

    private fun returnToLogin() {
        AdminDemoSession.logout()

        startActivity(
            Intent(this, LoginActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TASK
            }
        )

        finish()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString("selected_id", selectedId)

        if (::reasonEdit.isInitialized) {
            outState.putString(
                "reason_draft",
                reasonEdit.text.toString()
            )
        }

        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        activeDialog?.dismiss()
        activeDialog = null
        super.onDestroy()
    }
}