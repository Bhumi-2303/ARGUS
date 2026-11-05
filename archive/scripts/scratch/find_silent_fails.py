import os
import re

positive_words = ['STABLE', 'VERIFIED', 'HEALTHY', 'NO ISSUES', 'CLEAN', 'PASSED']

def search_dir(d):
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Look for data?.flag ? "bad" : "good"
                # This could be split across lines, so let's just search for the words themselves
                for word in positive_words:
                    if word in content:
                        print(f"File: {path} contains {word}")

search_dir('web/src')
