from docx import Document
doc = Document('ARGUS_paper_v2_representation_resolution.docx')
for i, p in enumerate(doc.paragraphs):
    if 'unverified' in p.text.lower():
        print(f"Paragraph {i}: {p.text}")
