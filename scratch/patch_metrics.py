import re

with open('scripts/verify_ui_numbers.py', 'r') as f:
    code = f.read()

injection = """
            # New Check: Flag if any numerical column has identical values for all rows
            # or if any row has identical values across all its numerical columns
            if len(api_data) > 1:
                # Check columns
                keys = [k for k in api_data[0].keys() if isinstance(api_data[0][k], (int, float))]
                for k in keys:
                    first_val = api_data[0][k]
                    if all(row.get(k) == first_val for row in api_data):
                        # Kappa and MCC can legitimately be close to 0, but if EVERYTHING is exactly identical, it's suspicious.
                        # Actually, let's flag if it's identical across all models (like 0.0000)
                        if first_val == 0.0:
                            print(f"  [ FAIL ] Column '{k}' has identical repeated value {first_val} across all models in {table_name}")
                            all_matched = False
                
                # Check rows
                for i, row in enumerate(api_data):
                    num_vals = [v for k,v in row.items() if isinstance(v, (int, float))]
                    if len(num_vals) > 2 and all(v == num_vals[0] for v in num_vals):
                        print(f"  [ FAIL ] Row {i} has identical repeated value {num_vals[0]} across all metrics in {table_name}")
                        all_matched = False
"""

# Let's insert it inside verify_metrics after table_match = True
code = code.replace('table_match = True', 'table_match = True' + injection)
with open('scripts/verify_ui_numbers.py', 'w') as f:
    f.write(code)
