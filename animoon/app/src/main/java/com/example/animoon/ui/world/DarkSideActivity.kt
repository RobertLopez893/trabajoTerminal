package com.example.animoon.ui.world

import com.example.animoon.MainActivity
import com.example.animoon.R

class DarkSideActivity : MainActivity() {
    override val screenZone: WorldZone = WorldZone.DARK_SIDE
    override val screenLayout: Int = R.layout.activity_dark_side
}