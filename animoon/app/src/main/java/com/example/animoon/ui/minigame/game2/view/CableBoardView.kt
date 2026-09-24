package com.example.animoon.ui.minigame.game2.view

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.PointF
import android.util.AttributeSet
import android.view.View
import com.example.animoon.ui.minigame.game2.model.Conexion
import com.example.animoon.ui.minigame.game2.model.DestinoConexion


/**
 * Vista encargada exclusivamente
 * de dibujar los cables.
 *
 * No decide:
 *
 * - si una conexión es correcta
 * - cuántos puntos obtiene el jugador
 * - cuándo cambia la ronda
 *
 * Únicamente representa las conexiones.
 */
class CableBoardView @JvmOverloads constructor(

    context: Context,

    attrs: AttributeSet? = null,

    defStyleAttr: Int = 0

) : View(
    context,
    attrs,
    defStyleAttr
) {


    // =========================================================
    // PUERTOS
    // =========================================================

    /**
     * ID lógico del mensaje
     * →
     * View donde se encuentra actualmente.
     */
    private var salidas:
            Map<Int, View> =
        emptyMap()


    /**
     * Destino lógico
     * →
     * View correspondiente.
     */
    private var destinos:
            Map<DestinoConexion, View> =
        emptyMap()


    // =========================================================
    // CONEXIONES
    // =========================================================

    private var conexiones:
            Set<Conexion> =
        emptySet()


    // =========================================================
    // COLORES
    // =========================================================

    /**
     * ID del mensaje
     * →
     * color asignado durante esta ronda.
     *
     * Este color depende de la posición visual
     * y no del ID permanente del mensaje.
     */
    private var coloresPorMensaje:
            Map<Int, Int> =
        emptyMap()


    // =========================================================
    // PINCEL
    // =========================================================

    private val cablePaint =
        Paint(
            Paint.ANTI_ALIAS_FLAG
        ).apply {


            style =
                Paint.Style.STROKE


            strokeWidth =
                dpToPx(7f)


            strokeCap =
                Paint.Cap.ROUND
        }


    // =========================================================
    // CONFIGURAR PUERTOS
    // =========================================================

    fun configurarPuertos(

        salidas: Map<Int, View>,

        destinos: Map<DestinoConexion, View>
    ) {


        this.salidas =
            salidas


        this.destinos =
            destinos


        invalidate()
    }


    // =========================================================
    // CONFIGURAR COLORES
    // =========================================================

    fun configurarColores(
        nuevosColores: Map<Int, Int>
    ) {


        coloresPorMensaje =
            nuevosColores.toMap()


        invalidate()
    }


    // =========================================================
    // ACTUALIZAR CONEXIONES
    // =========================================================

    fun actualizarConexiones(
        nuevasConexiones: Set<Conexion>
    ) {


        /*
         * Creamos una copia para que
         * CableBoardView no dependa del
         * MutableSet original.
         */
        conexiones =
            nuevasConexiones.toSet()


        invalidate()
    }


    // =========================================================
    // DIBUJAR
    // =========================================================

    override fun onDraw(
        canvas: Canvas
    ) {


        super.onDraw(
            canvas
        )


        conexiones.forEach { conexion ->


            // -------------------------------------------------
            // LOCALIZAR PUERTOS
            // -------------------------------------------------

            val salida =
                salidas[
                    conexion.mensajeId
                ]


            val destino =
                destinos[
                    conexion.destino
                ]


            /*
             * Si alguna referencia todavía
             * no está disponible, ignoramos
             * únicamente esa conexión.
             */
            if (
                salida == null ||
                destino == null
            ) {

                return@forEach
            }


            // -------------------------------------------------
            // COORDENADAS
            // -------------------------------------------------

            val inicio =
                obtenerCentroInferior(
                    salida
                )


            val fin =
                obtenerCentroSuperior(
                    destino
                )


            // -------------------------------------------------
            // COLOR
            // -------------------------------------------------

            cablePaint.color =

                coloresPorMensaje[
                    conexion.mensajeId
                ]
                    ?: Color.parseColor(
                        "#6674D9"
                    )


            // -------------------------------------------------
            // DIBUJAR
            // -------------------------------------------------

            /*
             * Por ahora utilizamos líneas rectas.
             *
             * Posteriormente podremos convertirlas
             * en cables curvos, luminosos o animados.
             */
            canvas.drawLine(

                inicio.x,
                inicio.y,

                fin.x,
                fin.y,

                cablePaint
            )
        }
    }


    // =========================================================
    // CENTRO INFERIOR DE SALIDA
    // =========================================================

    /**
     * Calcula el centro inferior
     * del botón superior.
     */
    private fun obtenerCentroInferior(
        view: View
    ): PointF {


        val viewLocation =
            IntArray(2)


        val boardLocation =
            IntArray(2)


        /*
         * Coordenadas absolutas
         * de la View.
         */
        view.getLocationOnScreen(
            viewLocation
        )


        /*
         * Coordenadas absolutas
         * del CableBoardView.
         */
        getLocationOnScreen(
            boardLocation
        )


        /*
         * Convertimos las coordenadas
         * absolutas en coordenadas relativas
         * al CableBoardView.
         */
        val x =

            (
                    viewLocation[0] -
                            boardLocation[0]
                    ).toFloat() +

                    view.width / 2f


        val y =

            (
                    viewLocation[1] -
                            boardLocation[1] +
                            view.height
                    ).toFloat()


        return PointF(

            x,

            y
        )
    }


    // =========================================================
    // CENTRO SUPERIOR DE DESTINO
    // =========================================================

    /**
     * Calcula el centro superior
     * del botón inferior.
     */
    private fun obtenerCentroSuperior(
        view: View
    ): PointF {


        val viewLocation =
            IntArray(2)


        val boardLocation =
            IntArray(2)


        view.getLocationOnScreen(
            viewLocation
        )


        getLocationOnScreen(
            boardLocation
        )


        val x =

            (
                    viewLocation[0] -
                            boardLocation[0]
                    ).toFloat() +

                    view.width / 2f


        val y =

            (
                    viewLocation[1] -
                            boardLocation[1]
                    ).toFloat()


        return PointF(

            x,

            y
        )
    }


    // =========================================================
    // UTILIDADES
    // =========================================================

    private fun dpToPx(
        dp: Float
    ): Float {


        return dp *
                resources
                    .displayMetrics
                    .density
    }
}