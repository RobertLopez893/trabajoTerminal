package com.example.animoon.ui.minigame.game2.view

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.PointF
import android.util.AttributeSet
import android.view.View
import com.example.animoon.ui.minigame.game2.model.Conexion
import com.example.animoon.ui.minigame.game2.model.DestinoConexion


class CableBoardView @JvmOverloads constructor(

    context: Context,

    attrs: AttributeSet? = null,

    defStyleAttr: Int = 0

) : View(
    context,
    attrs,
    defStyleAttr
) {


    private var salidas:
            Map<Int, View> =
        emptyMap()


    private var destinos:
            Map<DestinoConexion, View> =
        emptyMap()


    private var conexiones:
            Set<Conexion> =
        emptySet()


    private var colores:
            Map<Int, Int> =
        emptyMap()


    private val paintCable =
        Paint(Paint.ANTI_ALIAS_FLAG).apply {

            style =
                Paint.Style.STROKE

            strokeWidth =
                dpToPx(7f)

            strokeCap =
                Paint.Cap.ROUND

            strokeJoin =
                Paint.Join.ROUND
        }


    private val paintConnector =
        Paint(Paint.ANTI_ALIAS_FLAG).apply {

            style =
                Paint.Style.FILL
        }


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


    fun configurarColores(
        colores: Map<Int, Int>
    ) {

        this.colores =
            colores


        invalidate()
    }


    fun actualizarConexiones(
        conexiones: Set<Conexion>
    ) {

        this.conexiones =
            conexiones.toSet()


        invalidate()
    }


    override fun onDraw(
        canvas: Canvas
    ) {

        super.onDraw(
            canvas
        )


        conexiones.forEach { conexion ->


            val salida =
                salidas[
                    conexion.mensajeId
                ]


            val destino =
                destinos[
                    conexion.destino
                ]


            if (
                salida == null ||
                destino == null
            ) {

                return@forEach
            }


            val inicio =
                obtenerCentroInferior(
                    salida
                )


            val fin =
                obtenerCentroSuperior(
                    destino
                )


            val color =
                colores[
                    conexion.mensajeId
                ] ?: Color.WHITE


            paintCable.color =
                color


            paintConnector.color =
                color


            dibujarCable(

                canvas,

                inicio,

                fin
            )
        }
    }


    private fun dibujarCable(

        canvas: Canvas,

        inicio: PointF,

        fin: PointF
    ) {


        val distancia =
            fin.y -
                    inicio.y


        val control1 =
            inicio.y +
                    distancia * 0.38f


        val control2 =
            fin.y -
                    distancia * 0.38f


        val path =
            Path().apply {

                moveTo(
                    inicio.x,
                    inicio.y
                )


                cubicTo(

                    inicio.x,
                    control1,

                    fin.x,
                    control2,

                    fin.x,
                    fin.y
                )
            }


        canvas.drawPath(
            path,
            paintCable
        )


        canvas.drawCircle(

            inicio.x,

            inicio.y,

            dpToPx(6f),

            paintConnector
        )


        canvas.drawCircle(

            fin.x,

            fin.y,

            dpToPx(6f),

            paintConnector
        )
    }


    private fun obtenerCentroInferior(
        view: View
    ): PointF {


        val ubicacionView =
            IntArray(2)


        val ubicacionBoard =
            IntArray(2)


        view.getLocationInWindow(
            ubicacionView
        )


        getLocationInWindow(
            ubicacionBoard
        )


        return PointF(

            ubicacionView[0] -
                    ubicacionBoard[0] +
                    view.width / 2f,

            ubicacionView[1] -
                    ubicacionBoard[1] +
                    view.height.toFloat()
        )
    }


    private fun obtenerCentroSuperior(
        view: View
    ): PointF {


        val ubicacionView =
            IntArray(2)


        val ubicacionBoard =
            IntArray(2)


        view.getLocationInWindow(
            ubicacionView
        )


        getLocationInWindow(
            ubicacionBoard
        )


        return PointF(
            ubicacionView[0] - ubicacionBoard[0] + view.width / 2f,
            (ubicacionView[1] - ubicacionBoard[1]).toFloat()
        )
    }


    private fun dpToPx(
        dp: Float
    ): Float {

        return dp *
                resources
                    .displayMetrics
                    .density
    }
}