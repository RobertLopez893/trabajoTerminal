import re

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace renderPlayersInZone entirely
def replace_func(match):
    return """    private val playerViews = mutableMapOf<String, android.view.View>()

    private fun renderPlayersInZone(players: List<com.example.animoon.data.model.PlayerState>) {
        val worldLayer = findViewById<androidx.constraintlayout.widget.ConstraintLayout>(R.id.worldLayer)
        if (worldLayer == null) return

        val currentIds = players.map { it.usuarioId }.toSet()
        val toRemove = playerViews.keys.filter { it !in currentIds }
        for (id in toRemove) {
            worldLayer.removeView(playerViews[id])
            playerViews.remove(id)
        }

        for (player in players) {
            val playerView = playerViews[player.usuarioId] ?: run {
                val newView = android.widget.LinearLayout(this)
                newView.orientation = android.widget.LinearLayout.VERTICAL
                newView.gravity = android.view.Gravity.CENTER
                
                val avatarImage = android.widget.ImageView(this)
                avatarImage.layoutParams = android.widget.LinearLayout.LayoutParams(160, 160)
                
                val species = player.avatar?.get("especie") ?: "gato"
                val color = player.avatar?.get("color") ?: "azul"
                val avatarRes = com.example.animoon.ui.profile.AvatarDrawableResolver.resolve(species, color) ?: R.drawable.avatar_cat_blue
                avatarImage.setImageResource(avatarRes)
                
                val nicknameText = android.widget.TextView(this)
                nicknameText.text = player.nickname
                nicknameText.setTextColor(android.graphics.Color.WHITE)
                nicknameText.setShadowLayer(4f, 0f, 0f, android.graphics.Color.BLACK)
                nicknameText.textSize = 14f
                
                newView.addView(avatarImage)
                newView.addView(nicknameText)
                
                newView.setOnClickListener {
                    startActivity(com.example.animoon.ui.profile.ProfileActivity.playerProfileIntent(this, player.usuarioId))
                }
                
                val params = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams(
                    androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.WRAP_CONTENT,
                    androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.WRAP_CONTENT
                )
                params.topToTop = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.PARENT_ID
                params.startToStart = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.PARENT_ID
                newView.layoutParams = params
                
                worldLayer.addView(newView)
                playerViews[player.usuarioId] = newView
                
                // Posicion inicial sin animacion
                newView.translationX = player.x - 80f // centrar
                newView.translationY = player.y - 100f // centrar
                
                newView
            }
            
            // Actualizar posicion con animacion suave
            playerView.animate()
                .translationX(player.x - 80f)
                .translationY(player.y - 100f)
                .setDuration(150)
                .start()
        }
    }"""

# regex to replace renderPlayersInZone (handling the old version which had a for loop and removed all views)
# we can just match from 'private fun renderPlayersInZone' up to the last closing brace of that function
# To be safe we match until 'fun renderZone' which follows it, or something else.
content = re.sub(r'    private fun renderPlayersInZone\(players: List<PlayerState>\).*?(?=\n\n    // =========================================================)', replace_func, content, flags=re.DOTALL)

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
