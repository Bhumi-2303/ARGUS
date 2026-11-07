# ARGUS ARCHITECTURE AUDIT

## Documented vs Actual Architecture
**Documented**: A complex multi-agent system (Data Intelligence, Threat Analysis, Risk Prediction, Knowledge Context, Decision Support, Explainability).
**Actual**: The agents exist as Python `async` scaffolding in `src/argus/agents/`. However, they are completely decoupled from the actual experimental results reported in the paper. The paper's ML models (XGBoost, CORAL, DANN) were run via standalone monolithic scripts (`generate_d1_d2_baselines.py`, `phase3_execute_all.py`), not through the multi-agent bus. 

## Agent Implementation Status
```
src/argus/agents
├── data_intelligence
│   ├── agent.py
│   ├── __init__.py
│   ├── pipeline.py
│   ├── __pycache__
│   ├── schemas.py
│   └── tools
├── decision_support
│   ├── agent.py
│   ├── docs
│   ├── __init__.py
│   ├── models
│   ├── tests
│   └── tools
├── explainability
│   ├── agent.py
│   ├── __init__.py
│   └── __pycache__
├── __init__.py
├── knowledge_context
│   ├── agent.py
│   ├── __init__.py
│   ├── pipeline.py
│   ├── __pycache__
│   ├── README.md
│   ├── resources
│   ├── schemas.py
│   └── tools
├── __pycache__
│   └── __init__.cpython-314.pyc
├── risk_prediction
│   ├── agent.py
│   ├── docs
│   ├── __init__.py
│   ├── models
│   ├── tests
│   └── tools
└── threat_analysis
    ├── agent.py
    ├── config.py
    ├── docs
    ├── __init__.py
    ├── models
    ├── tests
    └── tools

26 directories, 20 files
```
The agents are **PARTIALLY FUNCTIONAL SCAFFOLDING**. They implement basic load/validate interfaces and a blackboard pattern, but none of the core scientific experiments (DG/DA models) are instantiated inside them or pass through them.
