import os

def replace_in_file(filepath):
    with open(filepath, "r") as f:
        code = f.read()
    
    # We already have some elements that were patched to "text-slate-900 dark:text-slate-100".
    # First, let's revert "text-slate-900 dark:text-slate-900 dark:text-slate-100" bug in Card.tsx
    code = code.replace("text-slate-900 dark:text-slate-900 dark:text-slate-100", "text-slate-900 dark:text-slate-100")
    
    # Replace all naked text-slate-100 with the responsive one, but only if not already prefixed.
    # To be safe, we just replace all "text-slate-100" and then clean up double replacements.
    code = code.replace("text-slate-100", "text-slate-900 dark:text-slate-100")
    code = code.replace("text-slate-900 dark:text-slate-900 dark:text-slate-100", "text-slate-900 dark:text-slate-100")
    code = code.replace("hover:text-slate-900 dark:text-slate-900 dark:text-slate-100", "hover:text-slate-900 dark:hover:text-slate-100")

    with open(filepath, "w") as f:
        f.write(code)

for root, _, files in os.walk("web/src"):
    for file in files:
        if file.endswith((".tsx", ".ts")):
            replace_in_file(os.path.join(root, file))

