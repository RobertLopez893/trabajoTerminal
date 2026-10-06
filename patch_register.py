import re

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/RegisterActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Show loading before launch
content = re.sub(r'(btnSendSms\.isEnabled\s*=\s*false\s*lifecycleScope\.launch\s*\{)', r'btnSendSms.isEnabled = false\n        showLoading("Comprobando apelativo...")\n        lifecycleScope.launch {', content)

# Hide loading if nickname fails
content = re.sub(r'(Toast\.makeText\(this@RegisterActivity,\s*"El apelativo ya)', r'hideLoading()\n                    \1', content)

# Hide loading if sms fails
content = re.sub(r'(Toast\.makeText\(this@RegisterActivity,\s*"Error al enviar SMS)', r'hideLoading()\n                    \1', content)

# Hide loading before goToVerification
content = re.sub(r'(goToVerification\(apelativo, phone, password\))', r'hideLoading()\n                \1', content)

# Hide loading on exception
content = re.sub(r'(\}\s*catch\s*\(e:\s*Exception\)\s*\{)', r'\1\n                hideLoading()', content)

with open('animoon/app/src/main/java/com/example/animoon/ui/auth/RegisterActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
