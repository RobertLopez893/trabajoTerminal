import re

with open('animoon/app/src/main/java/com/example/animoon/ui/profile/ProfileActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports
imports = """import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.example.animoon.data.network.ApiClient
import com.example.animoon.data.network.TokenManager
"""

if "import androidx.lifecycle.lifecycleScope" not in content:
    content = content.replace("import android.os.Bundle", "import android.os.Bundle\n" + imports)

# Replace the onCreate loading logic
old_logic = """
        val userId =
            intent.getStringExtra(EXTRA_USER_ID)

        val profile =
            userId?.let { DemoProfileSource.findProfile(it) }

        if (profile == null) {
            profileCard.visibility = View.GONE
            errorText.visibility = View.VISIBLE
            return
        }

        val isOwnProfile =
            DemoProfileSource.isMyProfile(profile.id)

        titleText.text =
            if (isOwnProfile) {
                "Mi perfil"
            } else {
                "Perfil de jugador"
            }

        nicknameText.text = profile.nickname

        val avatarDrawable =
            AvatarDrawableResolver.resolve(
                species = profile.species,
                color = profile.color
            )

        if (avatarDrawable != null) {
            avatarImage.setImageResource(avatarDrawable)
            avatarImage.contentDescription =
                "Avatar de ${profile.nickname}"

            avatarImage.visibility = View.VISIBLE
            avatarUnavailable.visibility = View.GONE
        } else {
            avatarImage.visibility = View.GONE
            avatarUnavailable.visibility = View.VISIBLE
        }

        chatButton.visibility =
            if (isOwnProfile) View.GONE else View.VISIBLE

        chatButton.setOnClickListener {
            val intent = Intent(this, com.example.animoon.ui.chat.ChatActivity::class.java)
            startActivity(intent)
        }

        errorText.visibility = View.GONE
        profileCard.visibility = View.VISIBLE
"""

new_logic = """
        val userId = intent.getStringExtra(EXTRA_USER_ID) ?: return

        // Hide initially
        profileCard.visibility = View.GONE
        errorText.visibility = View.GONE
        
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val response = ApiClient.authService.getProfile(userId)
                
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val profile = response.body()!!
                        // Asumimos que si userId es "me", es propio, 
                        // de lo contrario deberiamos tener el ID real guardado en TokenManager.
                        // Para esto usaremos si el EXTRA_USER_ID era "me" (o puedes ajustar luego)
                        val isOwnProfile = (userId == "me")
                        
                        titleText.text = if (isOwnProfile) "Mi perfil" else "Perfil de jugador"
                        nicknameText.text = profile.nickname
                        
                        val avatarDrawable = AvatarDrawableResolver.resolve(profile.species, profile.color)
                        
                        if (avatarDrawable != null) {
                            avatarImage.setImageResource(avatarDrawable)
                            avatarImage.contentDescription = "Avatar de ${profile.nickname}"
                            avatarImage.visibility = View.VISIBLE
                            avatarUnavailable.visibility = View.GONE
                        } else {
                            avatarImage.visibility = View.GONE
                            avatarUnavailable.visibility = View.VISIBLE
                        }
                        
                        chatButton.visibility = if (isOwnProfile) View.GONE else View.VISIBLE
                        
                        chatButton.setOnClickListener {
                            val chatIntent = Intent(this@ProfileActivity, com.example.animoon.ui.chat.ChatActivity::class.java)
                            startActivity(chatIntent)
                        }
                        
                        profileCard.visibility = View.VISIBLE
                    } else {
                        errorText.visibility = View.VISIBLE
                        errorText.text = "Error al cargar perfil"
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    errorText.visibility = View.VISIBLE
                    errorText.text = "Error de conexión"
                }
            }
        }
"""
content = content.replace(old_logic, new_logic)

# Replace myProfileIntent to use "me" instead of DemoProfileSource.myProfile.id
content = content.replace("DemoProfileSource.myProfile.id", '"me"')

with open('animoon/app/src/main/java/com/example/animoon/ui/profile/ProfileActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
