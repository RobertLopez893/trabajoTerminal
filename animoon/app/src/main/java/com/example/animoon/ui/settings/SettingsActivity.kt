package com.example.animoon.ui.settings

import android.Manifest
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import com.example.animoon.R
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager
import com.example.animoon.notifications.LocalNotificationManager
import com.example.animoon.ui.base.BaseActivity
import com.example.animoon.ui.splash.SplashActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.materialswitch.MaterialSwitch
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import com.example.animoon.ui.help.HelpActivity

class SettingsActivity : BaseActivity() {

    private lateinit var notificationSwitch: MaterialSwitch
    private lateinit var notificationStatus: TextView
    private lateinit var systemNotificationsButton: MaterialButton
    private lateinit var backButton: MaterialButton
    private lateinit var helpButton: MaterialButton
    private lateinit var parentsButton: MaterialButton
    private lateinit var logoutButton: MaterialButton

    private var updatingSwitch = false
    private var loggingOut = false
    private var requestingPermission = false

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        requestingPermission = false

        LocalNotificationManager.setEnabled(this, granted)
        refreshNotificationControls()

        if (!granted) {
            MaterialAlertDialogBuilder(this)
                .setTitle("Notificaciones desactivadas")
                .setMessage(
                    "Puedes seguir usando ANIMOON. " +
                            "Si quieres recibir avisos, puedes permitirlos " +
                            "desde los ajustes de Android."
                )
                .setNegativeButton("Ahora no", null)
                .setPositiveButton("Abrir ajustes") { _, _ ->
                    LocalNotificationManager.setEnabled(this, true)
                    openSystemNotificationSettings()
                }
                .show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Es seguro inicializarlo nuevamente con el contexto de la app.
        TokenManager.init(applicationContext)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        notificationSwitch = findViewById(R.id.switchLocalNotifications)
        notificationStatus = findViewById(R.id.txtNotificationStatus)
        systemNotificationsButton =
            findViewById(R.id.btnSystemNotifications)

        backButton = findViewById(R.id.btnSettingsBack)
        helpButton = findViewById(R.id.btnSettingsHelp)
        parentsButton = findViewById(R.id.btnSettingsParents)
        logoutButton = findViewById(R.id.btnSettingsLogout)

        LocalNotificationManager.createChannel(this)

        notificationSwitch.setOnCheckedChangeListener { _, checked ->
            if (!updatingSwitch) {
                changeNotificationPreference(checked)
            }
        }

        systemNotificationsButton.setOnClickListener {
            openSystemNotificationSettings()
        }

        backButton.setOnClickListener {
            finish()
        }

        helpButton.setOnClickListener {
            startActivity(
                Intent(
                    this,
                    HelpActivity::class.java
                )
            )
        }

        parentsButton.setOnClickListener {
            showPendingSection("Para padres")
        }

        logoutButton.setOnClickListener {
            confirmLogout()
        }

        // Mientras termina el cierre, evitamos volver al lobby.
        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    if (!loggingOut) {
                        finish()
                    }
                }
            }
        )

        refreshNotificationControls()
    }

    override fun onResume() {
        super.onResume()

        if (::notificationSwitch.isInitialized) {
            // Refleja también cambios hechos en los ajustes de Android.
            refreshNotificationControls()
        }
    }

    private fun changeNotificationPreference(enabled: Boolean) {
        LocalNotificationManager.setEnabled(this, enabled)

        if (!enabled) {
            refreshNotificationControls()
            return
        }

        if (
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            !LocalNotificationManager.hasPermission(this)
        ) {
            requestingPermission = true
            refreshNotificationControls()

            permissionLauncher.launch(
                Manifest.permission.POST_NOTIFICATIONS
            )
            return
        }

        refreshNotificationControls()

        if (!LocalNotificationManager.canShow(this)) {
            MaterialAlertDialogBuilder(this)
                .setTitle("Permitir notificaciones")
                .setMessage(
                    "Android tiene bloqueadas las notificaciones de ANIMOON. " +
                            "Puedes habilitarlas en los ajustes del dispositivo."
                )
                .setNegativeButton("Ahora no", null)
                .setPositiveButton("Abrir ajustes") { _, _ ->
                    openSystemNotificationSettings()
                }
                .show()
        }
    }

    private fun refreshNotificationControls() {
        val enabled = LocalNotificationManager.isEnabled(this)
        val allowed = LocalNotificationManager.canShow(this)

        updatingSwitch = true
        notificationSwitch.isChecked = enabled
        updatingSwitch = false

        notificationSwitch.isEnabled =
            !loggingOut && !requestingPermission

        notificationStatus.text = when {
            requestingPermission ->
                "Confirma si deseas recibir notificaciones."

            !enabled ->
                "Notificaciones desactivadas."

            !allowed ->
                "Activadas en ANIMOON, pero bloqueadas por Android. " +
                        "Revisa los permisos para recibir avisos."

            else ->
                "Notificaciones activadas."
        }

        systemNotificationsButton.visibility =
            if (enabled && !allowed && !requestingPermission) {
                View.VISIBLE
            } else {
                View.GONE
            }

        systemNotificationsButton.isEnabled = !loggingOut
    }

    private fun openSystemNotificationSettings() {
        // Desde aquí se puede revisar tanto el permiso general
        // como el canal “Avisos de ANIMOON”.
        val intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
            .putExtra(Settings.EXTRA_APP_PACKAGE, packageName)

        startActivity(intent)
    }

    private fun showPendingSection(title: String) {
        MaterialAlertDialogBuilder(this)
            .setTitle(title)
            .setMessage("Esta sección estará disponible próximamente.")
            .setPositiveButton("Entendido", null)
            .show()
    }

    private fun confirmLogout() {
        if (loggingOut) return

        MaterialAlertDialogBuilder(this)
            .setTitle("¿Cerrar sesión?")
            .setMessage(
                "Volverás a la pantalla de inicio de ANIMOON."
            )
            .setNegativeButton("Quedarme", null)
            .setPositiveButton("Cerrar sesión") { _, _ ->
                logout()
            }
            .show()
    }

    private fun logout() {
        if (loggingOut) return

        loggingOut = true
        setControlsEnabled(false)
        logoutButton.text = "Cerrando sesión…"

        lifecycleScope.launch {
            // Conservamos el token mientras se avisa al backend.
            // La falta de conexión no impide el cierre local.
            withTimeoutOrNull(5_000L) {
                try {
                    ApiClient.authService.logout()
                } catch (exception: CancellationException) {
                    throw exception
                } catch (_: Exception) {
                    // Continuamos con el cierre local.
                }
            }

            TokenManager.clearToken()
            LocalNotificationManager.cancelLocalNotifications(
                this@SettingsActivity
            )

            val intent = Intent(
                this@SettingsActivity,
                SplashActivity::class.java
            ).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TASK
            }

            startActivity(intent)
            finish()
        }
    }

    private fun setControlsEnabled(enabled: Boolean) {
        backButton.isEnabled = enabled
        helpButton.isEnabled = enabled
        parentsButton.isEnabled = enabled
        logoutButton.isEnabled = enabled
        systemNotificationsButton.isEnabled = enabled
        notificationSwitch.isEnabled = enabled
    }
}