with open("scripts/verify_ui_numbers.py", "r") as f:
    content = f.read()

new_func = """
def verify_protocol_limits_page():
    print("\\n" + "=" * 80)
    print("        ARGUS PROTOCOL LIMITS PAGE TEXT VERIFICATION")
    print("=" * 80)

    import re
    with open("web/src/features/protocol_limits/ProtocolLimitsPage.tsx", "r") as f:
        page_text = f.read()
    
    # 1. Verify DANN raw metric discrepancy states exactly 0.332095
    if "0.332095" not in page_text:
        print("  [ FAIL ] Missing exact recomputed ROC-AUC (0.332095) in ProtocolLimitsPage")
        return False
    if "1.084%" not in page_text and "0.064%" not in page_text:
        print("  [ FAIL ] Missing exact discrepancy Specificity metrics in ProtocolLimitsPage")
        return False
        
    # 2. Verify V1 feature space duplication statement
    if "82 unique vectors" not in page_text:
        print("  [ FAIL ] Missing legacy V1 representation condensation count (82 unique vectors)")
        return False
        
    # 3. Verify cross-domain leakage vectors
    if "7 target vectors leaked" not in page_text:
        print("  [ FAIL ] Missing cross-domain overlap sum (7 target vectors)")
        return False

    print("  [ PASS ] Protocol Limits Page explicitly states all required open verification discrepancies accurately.")
    return True

"""

content = content.replace("if __name__ == \"__main__\":", new_func + "if __name__ == \"__main__\":")
content = content.replace("t_ok = verify_topology_strings()", "t_ok = verify_topology_strings()\n    p_ok = verify_protocol_limits_page()")
content = content.replace("if not (m_ok and t_ok):", "if not (m_ok and t_ok and p_ok):")

with open("scripts/verify_ui_numbers.py", "w") as f:
    f.write(content)
