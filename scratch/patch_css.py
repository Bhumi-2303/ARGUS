import re

with open("web/src/index.css", "r") as f:
    code = f.read()

# Remove glassmorphism completely
code = re.sub(r'/\* Glassmorphism helpers \*/.*', '', code, flags=re.DOTALL)
# Remove purple
code = re.sub(r'--accent-purple.*', '', code)

with open("web/src/index.css", "w") as f:
    f.write(code)
