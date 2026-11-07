import os
import re

positive_words = ['stable', 'verified', 'healthy', 'no issues', 'operational', 'online']

def search_dir(d):
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith('.tsx') or f.endswith('.ts'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                lower_content = content.lower()
                for word in positive_words:
                    if word in lower_content:
                        print(f"File: {path} contains {word}")

search_dir('web/src')
