with open("web/src/api/client.ts", "r") as f:
    content = f.read()

content = content.replace(
    "  features: string[];\n}",
    "  features: string[];\n  status: string;\n}"
)

content = content.replace(
    "  target_domain: string;\n  provenance: ModelProvenance;\n}",
    "  target_domain: string;\n  status: string;\n  provenance: ModelProvenance;\n}"
)

with open("web/src/api/client.ts", "w") as f:
    f.write(content)
