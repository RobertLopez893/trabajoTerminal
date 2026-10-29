package com.example.animoon.ui.common

import android.app.Activity
import android.app.Dialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.text.InputFilter
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import com.example.animoon.R
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager
import com.example.animoon.data.network.UserAppealSubmitRequest
import com.example.animoon.network.ChatWebSocketManager
import com.example.animoon.ui.splash.SplashActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject

object BannedAccountDialog {

    /**
     * Muestra el pop-up de cuenta suspendida con el estilo visual de Animoon.
     * Cumple con los requerimientos del Módulo 10 (RN-AP-01 a RN-AP-04 y RF-AP-01 a RF-AP-07).
     *
     * @param activity Actividad que invoca el diálogo (ChatActivity o LoginActivity)
     * @param motivo Detalle o razón de la suspensión (sin exponer datos del modelo PLN)
     * @param isChatBan true si la expulsión ocurre en tiempo real durante una sesión de chat,
     *                  false si ocurre al intentar iniciar sesión en LoginActivity.
     * @param nickname Apelativo del usuario suspendido (opcional, para prellenar formulario de apelación)
     * @param onDismissAction Callback ejecutado al presionar el botón de acción principal.
     */
    fun show(
        activity: Activity,
        motivo: String? = null,
        isChatBan: Boolean = false,
        nickname: String? = null,
        onDismissAction: (() -> Unit)? = null
    ) {
        if (activity.isFinishing || activity.isDestroyed) return

        val dialog = Dialog(activity)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        dialog.setContentView(R.layout.dialog_account_banned)
        dialog.setCancelable(false)
        dialog.setCanceledOnTouchOutside(false)

        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        val width = (activity.resources.displayMetrics.widthPixels * 0.90).toInt()
        dialog.window?.setLayout(width, ViewGroup.LayoutParams.WRAP_CONTENT)

        val tvTitle = dialog.findViewById<TextView>(R.id.tvBannedTitle)
        val tvMessage = dialog.findViewById<TextView>(R.id.tvBannedMessage)
        val tvDetail = dialog.findViewById<TextView>(R.id.tvBannedDetail)
        val btnAppeal = dialog.findViewById<MaterialButton>(R.id.btnBannedAppeal)
        val btnAction = dialog.findViewById<MaterialButton>(R.id.btnBannedAction)

        tvTitle.text = "⚠️ Cuenta Suspendida"

        if (isChatBan) {
            tvMessage.text = "Tu cuenta ha sido suspendida permanentemente por violar las normas de seguridad y convivencia de Animoon.\n\nTu sesión activa ha sido cerrada."
            btnAction.text = "Volver al inicio"
        } else {
            tvMessage.text = "Tu cuenta ha sido suspendida permanentemente por violar las normas de seguridad y convivencia de Animoon.\n\nNo es posible iniciar sesión."
            btnAction.text = "Entendido"
        }

        // RN-AP-01: No mostrar frases específicas ni pesos del modelo de PLN
        if (!motivo.isNullOrBlank()) {
            tvDetail.visibility = View.VISIBLE
            val cleanMotivo = motivo
                .replace("CUENTA_BANEADA:", "")
                .replace("GROOMING_ALERT:", "")
                .trim()
            val mensajeProtegido = if (cleanMotivo.length > 80 || cleanMotivo.contains("{")) {
                "Conductas inapropiadas detectadas por el sistema de seguridad."
            } else {
                cleanMotivo
            }
            tvDetail.text = "Motivo: $mensajeProtegido"
        } else {
            tvDetail.visibility = View.GONE
        }

        // RF-AP-03: Botón '¿Crees que se trata de un error? Toca aquí'
        btnAppeal.text = "¿Crees que se trata de un error? Toca aquí"
        btnAppeal.setOnClickListener {
            val apelativoEfectivo = nickname ?: TokenManager.getNickname()
            showAppealFormDialog(activity, apelativoEfectivo, dialog)
        }

        // Botón de Acción Principal (Volver al inicio o Entendido)
        btnAction.setOnClickListener {
            dialog.dismiss()

            if (isChatBan) {
                // Matar tokens locales y cerrar WebSockets
                TokenManager.clearToken()
                ChatWebSocketManager.disconnect()
                com.example.animoon.data.network.WebSocketManager.disconnect()

                // Redirigir a la pantalla principal / Splash limpiando toda la pila de Activities
                val intent = Intent(activity, SplashActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                }
                activity.startActivity(intent)
                activity.finish()
            } else {
                onDismissAction?.invoke()
            }
        }

        try {
            dialog.show()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    /**
     * RF-AP-04: Presenta un formulario simple donde el usuario puede redactar una justificación breve
     * con límite máximo de 250 caracteres para la revisión manual de su caso.
     */
    private fun showAppealFormDialog(
        activity: Activity,
        prefilledNickname: String?,
        parentBannedDialog: Dialog
    ) {
        if (activity.isFinishing || activity.isDestroyed) return

        val formDialog = Dialog(activity)
        formDialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        formDialog.setContentView(R.layout.dialog_appeal_form)
        formDialog.setCancelable(true)
        formDialog.setCanceledOnTouchOutside(false)

        formDialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        val width = (activity.resources.displayMetrics.widthPixels * 0.92).toInt()
        formDialog.window?.setLayout(width, ViewGroup.LayoutParams.WRAP_CONTENT)

        val tvAccountBadge = formDialog.findViewById<TextView>(R.id.tvAppealAccountBadge)
        val tilNickname = formDialog.findViewById<TextInputLayout>(R.id.tilAppealNickname)
        val etNickname = formDialog.findViewById<TextInputEditText>(R.id.etAppealNickname)
        val tilJustification = formDialog.findViewById<TextInputLayout>(R.id.tilAppealJustification)
        val etJustification = formDialog.findViewById<TextInputEditText>(R.id.etAppealJustification)
        val pbLoading = formDialog.findViewById<ProgressBar>(R.id.pbAppealLoading)
        val btnSubmit = formDialog.findViewById<MaterialButton>(R.id.btnSubmitAppeal)
        val btnCancel = formDialog.findViewById<MaterialButton>(R.id.btnCancelAppeal)

        // Limitar campo a exactamente 250 caracteres (RF-AP-04)
        etJustification.filters = arrayOf(InputFilter.LengthFilter(250))

        if (!prefilledNickname.isNullOrBlank()) {
            tvAccountBadge.visibility = View.VISIBLE
            tvAccountBadge.text = "Cuenta: @$prefilledNickname"
            tilNickname.visibility = View.GONE
            etNickname.setText(prefilledNickname)
        } else {
            tvAccountBadge.visibility = View.GONE
            tilNickname.visibility = View.VISIBLE
        }

        btnCancel.setOnClickListener {
            formDialog.dismiss()
        }

        btnSubmit.setOnClickListener {
            val nick = if (!prefilledNickname.isNullOrBlank()) {
                prefilledNickname.trim()
            } else {
                etNickname.text?.toString()?.trim().orEmpty()
            }

            val justificacion = etJustification.text?.toString()?.trim().orEmpty()

            if (nick.isBlank()) {
                tilNickname.error = "Ingresa el apelativo de tu cuenta"
                return@setOnClickListener
            } else {
                tilNickname.error = null
            }

            if (justificacion.length < 5) {
                tilJustification.error = "Escribe al menos una justificación breve (mín. 5 caracteres)"
                return@setOnClickListener
            } else if (justificacion.length > 250) {
                tilJustification.error = "La justificación no puede superar los 250 caracteres"
                return@setOnClickListener
            } else {
                tilJustification.error = null
            }

            // Enviar apelación al backend
            btnSubmit.isEnabled = false
            btnCancel.isEnabled = false
            pbLoading.visibility = View.VISIBLE

            CoroutineScope(Dispatchers.Main).launch {
                try {
                    val response = withContext(Dispatchers.IO) {
                        ApiClient.adminService.submitAppeal(
                            UserAppealSubmitRequest(
                                nickname = nick,
                                justificacion = justificacion
                            )
                        )
                    }

                    pbLoading.visibility = View.GONE
                    btnSubmit.isEnabled = true
                    btnCancel.isEnabled = true

                    if (response.isSuccessful) {
                        // RF-AP-07: Mensaje de confirmación de envío y redirección al inicio
                        formDialog.dismiss()
                        parentBannedDialog.dismiss()

                        MaterialAlertDialogBuilder(activity)
                            .setTitle("Apelación enviada")
                            .setMessage("Tu solicitud ha sido registrada exitosamente. El equipo de administración revisará manualmente tu caso y notificará la resolución a tu tutor vía SMS.")
                            .setPositiveButton("Volver al inicio") { _, _ ->
                                TokenManager.clearToken()
                                ChatWebSocketManager.disconnect()
                                com.example.animoon.data.network.WebSocketManager.disconnect()

                                val intent = Intent(activity, SplashActivity::class.java).apply {
                                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                                }
                                activity.startActivity(intent)
                                activity.finish()
                            }
                            .setCancelable(false)
                            .show()

                    } else {
                        val errorBody = response.errorBody()?.string().orEmpty()
                        var errorMsg = "No fue posible procesar la apelación."

                        try {
                            val json = JSONObject(errorBody)
                            if (json.has("detail")) {
                                errorMsg = json.getString("detail")
                            }
                        } catch (_: Exception) {}

                        // RF-AP-05: Si ya existe una apelación registrada y pendiente, o fue rechazada
                        if (response.code() == 409) {
                            formDialog.dismiss()
                            MaterialAlertDialogBuilder(activity)
                                .setTitle("Apelación en proceso")
                                .setMessage(errorMsg)
                                .setPositiveButton("Entendido", null)
                                .show()
                        } else {
                            MaterialAlertDialogBuilder(activity)
                                .setTitle("Aviso")
                                .setMessage(errorMsg)
                                .setPositiveButton("Entendido", null)
                                .show()
                        }
                    }

                } catch (e: Exception) {
                    pbLoading.visibility = View.GONE
                    btnSubmit.isEnabled = true
                    btnCancel.isEnabled = true

                    Toast.makeText(
                        activity,
                        "Error de conexión. Verifica tu acceso a internet e intenta de nuevo.",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }

        try {
            formDialog.show()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}

