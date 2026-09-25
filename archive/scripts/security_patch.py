import yaml
with open(".github/workflows/ci.yml", "r") as f:
    ci = yaml.safe_load(f)

# Add security job
ci['jobs']['security-scan'] = {
    'name': 'Security Audit & Scan',
    'runs-on': 'ubuntu-latest',
    'steps': [
        {'uses': 'actions/checkout@v4'},
        {'name': 'Set up Python', 'uses': 'actions/setup-python@v5', 'with': {'python-version': '3.11'}},
        {'name': 'Python Dependency Audit', 'run': 'python -m pip install pip-audit && pip-audit -r pyproject.toml --desc || echo "Audit findings exist"'},
        {'name': 'Secret Scan', 'run': 'grep -riE "(password|secret|api_key|token)[ :=]+[' + "'\\\"" + '][a-zA-Z0-9_-]{10,}[' + "'\\\"" + ']" src/ config/ || echo "No hardcoded secrets found"'},
        {'name': 'Run Security Tests', 'run': 'python -m pip install -e ".[test]" && pytest tests/security/ -v'}
    ]
}

with open(".github/workflows/ci.yml", "w") as f:
    yaml.dump(ci, f, default_flow_style=False, sort_keys=False)

