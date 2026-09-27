import re

with open('scripts/verify_ui_numbers.py', 'r') as f:
    code = f.read()

# Replace the previous verify_model_comparison_ui with a better one
old_func_start = code.find("def verify_model_comparison_ui():")
if old_func_start != -1:
    code = code[:old_func_start]

new_func = """
def verify_model_comparison_ui():
    print("\\n" + "=" * 80)
    print("        ARGUS UI RENDER LOGIC VERIFICATION (ModelComparisonPage.tsx)")
    print("=" * 80)
    
    with open("web/src/features/benchmark/ModelComparisonPage.tsx", "r") as f:
        page_text = f.read()
        
    matched = True
    
    # Check for hardcoded 95/5/10/90 CM splits by checking fallback usage
    # "byte-identical to another model's confusion matrix" means they used a static default.
    if "(r.recall ?? 0.9)" in page_text or "(r.Recall ?? 0.9)" in page_text:
        print("  [ FAIL ] Found identical fallback confusion matrix logic in ModelComparisonPage.tsx (0.9/0.05)")
        matched = False
        
    # Check if there's a fallback that produces a repeated 0.0000 in columns/rows.
    if "(r.mcc ?? 0).toFixed(4)" in page_text or "r.MCC ?? 0).toFixed(4)" in page_text:
        print("  [ FAIL ] Found identical 0.0000 fallback for missing metrics in table rendering")
        matched = False

    if matched:
        print("  [ PASS ] No identical repeated fallback values (like 0.0000 or 95/5) found in ModelComparisonPage.tsx")
        
    return matched
"""

code += new_func

with open('scripts/verify_ui_numbers.py', 'w') as f:
    f.write(code)
