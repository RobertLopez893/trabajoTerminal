package com.example.animoon.notifications

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.example.animoon.R
import com.example.animoon.ui.splash.SplashActivity

object LocalNotificationManager {

    private const val PREFS_NAME = "animoon_notification_preferences"
    private const val KEY_ENABLED = "local_notifications_enabled"

    private const val CHANNEL_ID = "animoon_local_notifications"
    private const val NOTIFICATION_TAG = "animoon_local"

    private fun preferences(context: Context) =
        context.applicationContext.getSharedPreferences(
            PREFS_NAME,
            Context.MODE_PRIVATE
        )

    fun isEnabled(context: Context): Boolean =
        preferences(context).getBoolean(KEY_ENABLED, false)

    fun setEnabled(context: Context, enabled: Boolean) {
        preferences(context)
            .edit()
            .putBoolean(KEY_ENABLED, enabled)
            .apply()

        if (!enabled) {
            cancelLocalNotifications(context)
        }
    }

    fun createChannel(context: Context) {
        // El proyecto tiene minSdk 26.
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Avisos de ANIMOON",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "Notificaciones locales de ANIMOON"
        }

        context.getSystemService(NotificationManager::class.java)
            .createNotificationChannel(channel)
    }

    fun hasPermission(context: Context): Boolean {
        return Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
                ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.POST_NOTIFICATIONS
                ) == PackageManager.PERMISSION_GRANTED
    }

    fun canShow(context: Context): Boolean {
        if (!hasPermission(context)) return false

        if (!NotificationManagerCompat.from(context)
                .areNotificationsEnabled()
        ) {
            return false
        }

        val manager =
            context.getSystemService(NotificationManager::class.java)

        val channel = manager.getNotificationChannel(CHANNEL_ID)

        return channel == null ||
                channel.importance != NotificationManager.IMPORTANCE_NONE
    }

    /**
     * Devuelve true si el aviso se entregó al sistema.
     * Android decide cómo presentarlo según sus ajustes.
     */
    fun show(
        context: Context,
        notificationId: Int,
        title: String,
        message: String
    ): Boolean {
        createChannel(context)

        if (!isEnabled(context) || !canShow(context)) {
            return false
        }

        val intent = Intent(context, SplashActivity::class.java)

        val pendingIntent = PendingIntent.getActivity(
            context,
            notificationId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or
                    PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification_animoon)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setVisibility(NotificationCompat.VISIBILITY_PRIVATE)
            .build()

        return try {
            NotificationManagerCompat.from(context).notify(
                NOTIFICATION_TAG,
                notificationId,
                notification
            )
            true
        } catch (_: SecurityException) {
            // El permiso pudo cambiar entre la comprobación y el envío.
            false
        }
    }

    fun cancelLocalNotifications(context: Context) {
        val manager =
            context.getSystemService(NotificationManager::class.java)

        manager.activeNotifications
            .filter { it.tag == NOTIFICATION_TAG }
            .forEach { notification ->
                manager.cancel(notification.tag, notification.id)
            }
    }
}