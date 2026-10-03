package com.example.animoon.ui.world

import android.app.Dialog
import android.os.Bundle
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.fragment.app.DialogFragment
import com.example.animoon.R
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class WorldMapDialogFragment : DialogFragment() {

    companion object {
        const val TAG = "world_map"
        const val REQUEST_KEY = "world_map_selection"
        const val RESULT_ZONE_ID = "selected_zone_id"

        private const val ARG_CURRENT_ZONE = "current_zone"

        fun newInstance(zone: WorldZone): WorldMapDialogFragment {
            return WorldMapDialogFragment().apply {
                arguments = Bundle().apply {
                    putString(ARG_CURRENT_ZONE, zone.id)
                }
            }
        }
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val currentZone = WorldZone.fromId(
            requireArguments().getString(ARG_CURRENT_ZONE)
        )

        val content = layoutInflater.inflate(
            R.layout.dialog_world_map,
            null
        )

        content.findViewById<TextView>(
            R.id.txtMapCurrentZone
        ).text = "Estás en: ${currentZone.title}"

        val destinations = listOf(
            R.id.btnMapBase to WorldZone.BASE,
            R.id.btnMapCraters to WorldZone.CRATERS,
            R.id.btnMapVillage to WorldZone.VILLAGE,
            R.id.btnMapDarkSide to WorldZone.DARK_SIDE
        )

        destinations.forEach { (buttonId, zone) ->
            val button = content.findViewById<MaterialButton>(buttonId)
            val isCurrentZone = zone == currentZone

            button.text = if (isCurrentZone) {
                "${zone.title}\nEstás aquí"
            } else {
                zone.title
            }

            // Mantiene legible el nombre de la ubicación actual.
            button.isEnabled = true

            button.strokeWidth = (
                    (if (isCurrentZone) 3 else 1) *
                            resources.displayMetrics.density
                    ).toInt()

            button.setOnClickListener {
                if (!isCurrentZone) {
                    parentFragmentManager.setFragmentResult(
                        REQUEST_KEY,
                        Bundle().apply {
                            putString(RESULT_ZONE_ID, zone.id)
                        }
                    )
                }

                // Tocar la ubicación actual simplemente cierra el mapa.
                dismiss()
            }
        }

        return MaterialAlertDialogBuilder(requireContext())
            .setView(content)
            .setNegativeButton("Cerrar", null)
            .create()
    }

    override fun onStart() {
        super.onStart()

        val window = dialog?.window ?: return
        val metrics = resources.displayMetrics

        val margin = (24 * metrics.density).toInt()
        val maxWidth = (840 * metrics.density).toInt()

        val availableWidth = (metrics.widthPixels - margin * 2)
            .coerceAtLeast(1)

        val availableHeight = (metrics.heightPixels - margin * 2)
            .coerceAtLeast(1)

        window.setLayout(
            minOf(maxWidth, availableWidth),
            ViewGroup.LayoutParams.WRAP_CONTENT
        )

        window.decorView.post {
            if (window.decorView.height > availableHeight) {
                window.setLayout(
                    minOf(maxWidth, availableWidth),
                    availableHeight
                )
            }
        }

        WindowInsetsControllerCompat(
            window,
            window.decorView
        ).apply {
            systemBarsBehavior =
                WindowInsetsControllerCompat
                    .BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE

            hide(WindowInsetsCompat.Type.systemBars())
        }
    }
}