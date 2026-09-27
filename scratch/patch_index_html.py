import re

with open("web/index.html", "r") as f:
    code = f.read()

code = code.replace("<title>web</title>", "<title>ARGUS Platform</title>")

with open("web/index.html", "w") as f:
    f.write(code)
