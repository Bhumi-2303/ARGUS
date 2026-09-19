import os
import glob
from pathlib import Path
import re

def find_root_dynamically_code():
    return """import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists():
        break
    _curr = _curr.parent
BASE = _curr
"""

def replace_in_file(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        return
        
    modified = False
    
    # Replace import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr
    pattern1 = re.compile(r"BASE\s*=\s*Path\(['\"]/Volumes/BLACK-BOX/ARGUS['\"]\)")
    if pattern1.search(content):
        content = pattern1.sub("import os\nfrom pathlib import Path\n_curr = Path(__file__).resolve()\nwhile _curr.parent != _curr:\n    if (_curr / 'src' / 'argus').exists(): break\n    _curr = _curr.parent\nBASE = _curr", content)
        modified = True

    # Replace import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
PROJECT_ROOT = _curr
    pattern2 = re.compile(r"PROJECT_ROOT\s*=\s*Path\(['\"]/Users/tirthkosambia/Documents/ARGUS['\"]\)")
    if pattern2.search(content):
        content = pattern2.sub("import os\nfrom pathlib import Path\n_curr = Path(__file__).resolve()\nwhile _curr.parent != _curr:\n    if (_curr / 'src' / 'argus').exists(): break\n    _curr = _curr.parent\nPROJECT_ROOT = _curr", content)
        modified = True
        
    # Replace import os
from pathlib import Path
_curr = Path(__file__).resolve()
while _curr.parent != _curr:
    if (_curr / 'src' / 'argus').exists(): break
    _curr = _curr.parent
BASE = _curr
    pattern3 = re.compile(r"BASE\s*=\s*Path\(['\"]/Users/tirthkosambia/Documents/ARGUS['\"]\)")
    if pattern3.search(content):
        content = pattern3.sub("import os\nfrom pathlib import Path\n_curr = Path(__file__).resolve()\nwhile _curr.parent != _curr:\n    if (_curr / 'src' / 'argus').exists(): break\n    _curr = _curr.parent\nBASE = _curr", content)
        modified = True

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed paths in {filepath}")

for root, dirs, files in os.walk('.'):
    if '.venv' in root or '.git' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            replace_in_file(os.path.join(root, file))

print("All hardcoded paths replaced dynamically!")
