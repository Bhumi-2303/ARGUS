# ARGUS Academic Manuscripts (`paper/manuscripts/`)

This directory manages the formal academic manuscripts, section revisions, and historical draft archives for ARGUS.

---

## Directory Organization

```text
paper/manuscripts/
├── README.md                      # Manuscript management guide and version catalog
├── main/                          # Authoritative current journal draft and plain-text transcript
│   ├── ARGUS_paper_v2_representation_resolution.docx # Authoritative Word manuscript (1.12 MB)
│   └── paper_text.txt             # Verbatim plain-text transcript (32.8 KB)
├── drafts/                        # Active working revisions and individual section drafts
└── archived_versions/             # Superseded historical drafts and writing outlines
```

---

## Authoritative Manuscript Inventory

| Artifact | Canonical Path | Size | SHA-256 Checksum | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Journal Draft (DOCX)** | [`paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/ARGUS_paper_v2_representation_resolution.docx) | 1,119,018 B | `b074f4f0d064ecb7f36f82c9a6ae82bfcd936b26437b33bc7720d1612e7e1b25` | Primary authoritative draft containing all core claims, mathematical derivations, figures, and tables. |
| **Plain-Text Transcript** | [`paper/manuscripts/main/paper_text.txt`](file:///home/bhumi/GitHub/ARGUS/paper/manuscripts/main/paper_text.txt) | 32,782 B | `6cae4ceedbaf19cb7561302bbd3a55ecdebd195983cb05b67a1eaacc3365586d` | Verbatim text transcript used for automated claim verification, text-matching, and NLP audits. |

*Note: For backward compatibility with legacy tooling, symbolic links are maintained at `paper/manuscripts/ARGUS_paper_v2_representation_resolution.docx` and `paper/manuscripts/paper_text.txt`.*

---

## Working Guidelines for Academic Collaborators

1. **Version Control**: Do not overwrite the authoritative draft directly without committing section drafts under `drafts/`.
2. **Scientific Precision**: Maintain strict adherence to empirical confidence tiers. Do not convert unverified hypotheses into empirical findings.
3. **Manuscript Audit & Peer Review Notes**: Before modifying text, consult the Senior Reviewer audit report at [`audit/independent/RESEARCH_PAPER_READINESS.md`](file:///home/bhumi/GitHub/ARGUS/audit/independent/RESEARCH_PAPER_READINESS.md) for target venue expectations and identified revision requirements.
