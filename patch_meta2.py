with open("src/argus/registry/model_registry.py", "r") as f:
    content = f.read()

content = content.replace(
    'target_domain=meta["target_domain"],\n                provenance=meta["provenance"]',
    'target_domain=meta["target_domain"],\n                status=meta["status"],\n                provenance=meta["provenance"]'
)

with open("src/argus/registry/model_registry.py", "w") as f:
    f.write(content)
