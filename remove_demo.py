import re

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove import
content = re.sub(r'import com\.example\.animoon\.ui\.profile\.DemoProfileSource\s*', '', content)

# Remove button listener
content = re.sub(r'findViewById<MaterialButton>\(\s*R\.id\.btnDemoProfiles\s*\)\.setOnClickListener\s*\{\s*showDemoProfiles\(\)\s*\}', '', content)

# Remove any lingering comments
content = re.sub(r'//\s*PERFILES DE DEMOSTRACI.N', '', content)

with open('animoon/app/src/main/java/com/example/animoon/MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
