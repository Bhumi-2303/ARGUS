import re

def patch_file(filepath, replacements):
    with open(filepath, "r") as f:
        code = f.read()
    for old, new in replacements:
        code = code.replace(old, new)
    with open(filepath, "w") as f:
        f.write(code)

patch_file("web/src/components/DataTable.tsx", [("—", "N/A")])
patch_file("web/src/components/TopBar.tsx", [("—", "-")])
patch_file("web/src/features/benchmark/ModelComparisonPage.tsx", [("—", "-")])
