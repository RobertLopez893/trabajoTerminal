import re

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/AvatarSelectionActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Show loading before launch
content = re.sub(r'(btnContinue\.isEnabled\s*=\s*false\s*lifecycleScope\.launch\s*\{)', r'btnContinue.isEnabled = false\n        showLoading("Creando tu avatar y configurando tu mundo...")\n\n        lifecycleScope.launch {', content)

# Hide loading on success
content = re.sub(r'(if\s*\(res\.isSuccessful\)\s*\{)', r'\n                hideLoading()\n                \1', content)

# Hide loading on error
content = re.sub(r'(else\s*\{[^}]*Toast\.makeText)', r'else {\n                    hideLoading()\n                    Toast.makeText', content)

# Hide loading on exception
content = re.sub(r'(\}\s*catch\s*\(e:\s*Exception\)\s*\{)', r'\1\n                hideLoading()', content)

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/AvatarSelectionActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
