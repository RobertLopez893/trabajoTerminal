package com.example.animoon.ui.world

import com.example.animoon.MainActivity
import com.example.animoon.R

class VillageActivity : MainActivity() {
    override val screenZone: WorldZone = WorldZone.VILLAGE
    override val screenLayout: Int = R.layout.activity_village
}