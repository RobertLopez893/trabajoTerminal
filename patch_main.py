import re

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
imports = """import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import com.example.animoon.data.model.PlayerState
import com.example.animoon.ui.profile.AvatarDrawableResolver
import androidx.constraintlayout.widget.ConstraintLayout
"""

if "import kotlinx.coroutines.flow.collectLatest" not in content:
    content = content.replace('import android.os.Bundle', 'import android.os.Bundle\n' + imports)

# Insert the collector in onCreate
collector_code = """
        lifecycleScope.launch {
            com.example.animoon.data.network.WebSocketManager.playersInZone.collectLatest { players ->
                renderPlayersInZone(players)
            }
        }
"""
content = content.replace('com.example.animoon.data.network.WebSocketManager.connect("base_principal")', 'com.example.animoon.data.network.WebSocketManager.connect("base_principal")\n' + collector_code)

# Add the render function
render_code = """
    private fun renderPlayersInZone(players: List<PlayerState>) {
        val worldLayer = findViewById<ConstraintLayout>(R.id.worldLayer)
        if (worldLayer == null) return
        worldLayer.removeAllViews()

        for (player in players) {
            val playerView = android.widget.LinearLayout(this)
            playerView.orientation = android.widget.LinearLayout.VERTICAL
            playerView.gravity = android.view.Gravity.CENTER
            
            val avatarImage = ImageView(this)
            avatarImage.layoutParams = android.widget.LinearLayout.LayoutParams(160, 160)
            
            val species = player.avatar?.get("especie") ?: "gato"
            val color = player.avatar?.get("color") ?: "azul"
            val avatarRes = AvatarDrawableResolver.resolve(species, color) ?: R.drawable.avatar_cat_blue
            avatarImage.setImageResource(avatarRes)
            
            val nicknameText = android.widget.TextView(this)
            nicknameText.text = player.nickname
            nicknameText.setTextColor(Color.WHITE)
            nicknameText.setShadowLayer(4f, 0f, 0f, Color.BLACK)
            nicknameText.textSize = 14f
            
            playerView.addView(avatarImage)
            playerView.addView(nicknameText)
            
            playerView.setOnClickListener {
                startActivity(ProfileActivity.playerProfileIntent(this, player.usuarioId))
            }
            
            val params = ConstraintLayout.LayoutParams(
                ConstraintLayout.LayoutParams.WRAP_CONTENT,
                ConstraintLayout.LayoutParams.WRAP_CONTENT
            )
            params.leftToLeft = ConstraintLayout.LayoutParams.PARENT_ID
            params.topToTop = ConstraintLayout.LayoutParams.PARENT_ID
            
            // Basic screen positioning based on x, y (0 to 1 range usually, or raw floats)
            // We multiply by an arbitrary scale to spread them out on the screen
            params.leftMargin = ((player.x % 100) * 10).toInt().coerceIn(50, 800)
            params.topMargin = ((player.y % 100) * 10).toInt().coerceIn(200, 1500)
            
            worldLayer.addView(playerView, params)
        }
    }
"""
if "fun renderPlayersInZone" not in content:
    content = content.replace('private fun showMinigameDialog()', render_code + '\n    private fun showMinigameDialog()')

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
