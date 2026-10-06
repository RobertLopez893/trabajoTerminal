import re

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/LoginActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'btnLogin\.isEnabled\s*=\s*false\s*lifecycleScope\.launch\s*\{', 'btnLogin.isEnabled = false\n        showLoading("Iniciando sesion...")\n        lifecycleScope.launch {', content)
content = re.sub(r'else\s*\{\s*Toast\.makeText', 'else {\n                    hideLoading()\n                    Toast.makeText', content)
content = re.sub(r'catch\s*\(e:\s*Exception\)\s*\{\s*Toast\.makeText', 'catch (e: Exception) {\n                hideLoading()\n                Toast.makeText', content)
content = re.sub(r'val body = res\.body\(\) \?: return@launch', 'val body = res.body() ?: return@launch\n                    hideLoading()', content)

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/LoginActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
