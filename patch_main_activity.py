import re

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Instead of exact string match, we can use regex to replace the function body
def replace_func(match):
    return """    private fun renderPlayersInZone(players: List<PlayerState>) {
        val worldLayer = findViewById<androidx.constraintlayout.widget.ConstraintLayout>(R.id.worldLayer)
        if (worldLayer == null) return
        worldLayer.removeAllViews()

        for (player in players) {
            val playerView = android.widget.LinearLayout(this)
            playerView.orientation = android.widget.LinearLayout.VERTICAL
            playerView.gravity = android.view.Gravity.CENTER
            
            // Set position based on backend data
            playerView.x = player.x
            playerView.y = player.y
            
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
            
            playerView.addView(avatarImage)
            playerView.addView(nicknameText)
            
            playerView.setOnClickListener {
                startActivity(com.example.animoon.ui.profile.ProfileActivity.playerProfileIntent(this, player.usuarioId))
            }
            
            // Fix absolute positioning by overriding top/start constraints to parent
            val params = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams(
                androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.WRAP_CONTENT,
                androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.WRAP_CONTENT
            )
            params.topToTop = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.PARENT_ID
            params.startToStart = androidx.constraintlayout.widget.ConstraintLayout.LayoutParams.PARENT_ID
            playerView.layoutParams = params
            
            worldLayer.addView(playerView)
        }
    }"""

content = re.sub(r'    private fun renderPlayersInZone\(players: List<PlayerState>\) \{.*?\n    \}', replace_func, content, flags=re.DOTALL)

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
