package com.example.animoon.ui.world

import android.graphics.PointF

/**
 * Validador de colisiones y límites transitables para los escenarios del mundo Animoon.
 * Define los polígonos del suelo caminable en coordenadas normalizadas (0.0 a 1.0)
 * para adaptarse a cualquier resolución de pantalla y relación de aspecto (centerCrop).
 */
object WorldBoundsValidator {

    data class Polygon(val points: List<PointF>) {
        /**
         * Determina si el punto (x, y) en coordenadas normalizadas [0.0..1.0] está dentro del polígono.
         * Utiliza el algoritmo estándar de Ray Casting (cruce de rayos).
         */
        fun contains(x: Float, y: Float): Boolean {
            if (points.isEmpty()) return true
            var inside = false
            var j = points.size - 1
            for (i in points.indices) {
                val pi = points[i]
                val pj = points[j]
                if ((pi.y > y) != (pj.y > y) &&
                    (x < (pj.x - pi.x) * (y - pi.y) / (pj.y - pi.y) + pi.x)
                ) {
                    inside = !inside
                }
                j = i
            }
            return inside
        }

        /**
         * Sujeta (clamp) un punto que cae fuera del polígono hacia el punto más cercano
         * sobre el borde transitable. Esto permite que si un usuario toca el cielo o una pared,
         * el avatar camine hasta el límite más próximo en lugar de ignorar la pulsación.
         */
        fun clamp(x: Float, y: Float): PointF {
            if (points.isEmpty()) return PointF(x, y)
            if (contains(x, y)) return PointF(x, y)

            var closestPoint = points[0]
            var minDistanceSq = Float.MAX_VALUE

            for (i in points.indices) {
                val p1 = points[i]
                val p2 = points[(i + 1) % points.size]
                val proj = closestPointOnSegment(x, y, p1.x, p1.y, p2.x, p2.y)
                val distSq = (x - proj.x) * (x - proj.x) + (y - proj.y) * (y - proj.y)
                if (distSq < minDistanceSq) {
                    minDistanceSq = distSq
                    closestPoint = proj
                }
            }
            return closestPoint
        }

        private fun closestPointOnSegment(
            px: Float, py: Float,
            x1: Float, y1: Float,
            x2: Float, y2: Float
        ): PointF {
            val dx = x2 - x1
            val dy = y2 - y1
            val lengthSq = dx * dx + dy * dy
            if (lengthSq <= 0.00001f) return PointF(x1, y1)

            val t = (((px - x1) * dx + (py - y1) * dy) / lengthSq).coerceIn(0f, 1f)
            return PointF(x1 + t * dx, y1 + t * dy)
        }
    }

    // 1. BASE PRINCIPAL (Lobby con explanada central y jardineras circulares en esquinas)
    private val polygonBase = Polygon(
        listOf(
            PointF(0.12f, 0.50f),
            PointF(0.88f, 0.50f),
            PointF(0.92f, 0.72f),
            PointF(0.80f, 0.84f),
            PointF(0.76f, 0.93f),
            PointF(0.24f, 0.93f),
            PointF(0.20f, 0.84f),
            PointF(0.08f, 0.72f)
        )
    )

    // 2. ALDEA LUNÁTICA (Plaza exterior con cúpulas y jardineras)
    private val polygonVillage = Polygon(
        listOf(
            PointF(0.14f, 0.48f),
            PointF(0.86f, 0.48f),
            PointF(0.90f, 0.70f),
            PointF(0.82f, 0.85f),
            PointF(0.78f, 0.93f),
            PointF(0.22f, 0.93f),
            PointF(0.18f, 0.85f),
            PointF(0.10f, 0.70f)
        )
    )

    // 3. CRÁTERES GIGANTES (Plataforma frontal con barandal frente al abismo lunar)
    private val polygonCraters = Polygon(
        listOf(
            PointF(0.08f, 0.47f),
            PointF(0.92f, 0.47f),
            PointF(0.92f, 0.93f),
            PointF(0.08f, 0.93f)
        )
    )

    // 4. LADO OSCURO DE LA LUNA (Suelo rocoso con observatorio y cristales)
    private val polygonDarkSide = Polygon(
        listOf(
            PointF(0.16f, 0.51f),
            PointF(0.38f, 0.46f),
            PointF(0.86f, 0.46f),
            PointF(0.90f, 0.72f),
            PointF(0.82f, 0.85f),
            PointF(0.76f, 0.93f),
            PointF(0.24f, 0.93f),
            PointF(0.18f, 0.85f),
            PointF(0.12f, 0.72f)
        )
    )

    /**
     * Obtiene el polígono de colisión correspondiente a una zona del mundo.
     */
    fun getPolygonForZone(zone: WorldZone): Polygon {
        return when (zone) {
            WorldZone.BASE -> polygonBase
            WorldZone.VILLAGE -> polygonVillage
            WorldZone.CRATERS -> polygonCraters
            WorldZone.DARK_SIDE -> polygonDarkSide
        }
    }

    /**
     * Valida y sujeta un punto en coordenadas normalizadas [0.0..1.0] para que siempre
     * se encuentre dentro de los límites transitables de la zona actual.
     */
    fun clampPoint(zone: WorldZone, normX: Float, normY: Float): PointF {
        val poly = getPolygonForZone(zone)
        return poly.clamp(normX.coerceIn(0f, 1f), normY.coerceIn(0f, 1f))
    }

    /**
     * Retorna verdadero si el punto en coordenadas normalizadas está dentro de la zona caminable.
     */
    fun isPointWalkable(zone: WorldZone, normX: Float, normY: Float): Boolean {
        val poly = getPolygonForZone(zone)
        return poly.contains(normX, normY)
    }
}
