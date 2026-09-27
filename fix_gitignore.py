import os

with open(".gitignore", "r") as f:
    content = f.read()

import re

# We want to replace the git merge conflict markers with a version that keeps the data un-ignores and adds !data/reproduction/
new_content = re.sub(r'<<<<<<< HEAD\n(.*?)\n=======\n(?:.*?)\n>>>>>>> origin/main', r'\1\n!data/reproduction/\n', content, flags=re.DOTALL)

with open(".gitignore", "w") as f:
    f.write(new_content)
