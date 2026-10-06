import re

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/LoginActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'(btnLogin\.isEnabled\s*=\s*false\s*lifecycleScope\.launch\s*\{)', r'btnLogin.isEnabled = false\n        showLoading("Iniciando sesión...")\n        lifecycleScope.launch {', content)
content = re.sub(r'(TokenManager\.saveToken\(res\.body\(\)\!\!.+?\)\s*startActivity\(Intent\(this@LoginActivity,\s*MainActivity::class\.java\)\)\s*finish\(\))', r'hideLoading()\n                    \1', content)
content = re.sub(r'(else\s*\{)', r'else {\n                    hideLoading()', content)
content = re.sub(r'(\}\s*catch\s*\(e:\s*Exception\)\s*\{)', r'\1\n                hideLoading()', content)

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/LoginActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)

