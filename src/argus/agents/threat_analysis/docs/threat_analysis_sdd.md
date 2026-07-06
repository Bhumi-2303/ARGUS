# Threat Analysis Agent (SDD)

## Overview
The Threat Analysis Agent is responsible for analyzing features of system events to determine if malicious activity is present. It sits downstream of the Data Intelligence Agent and relies on machine learning models for anomaly detection and threat classification.

## Architecture
The agent is built on top of the ARGUS `BaseAgent` and strictly adheres to its 10 lifecycle methods. The agent delegates its core functionalities to isolated, single-responsibility `BaseTool` implementations.

### Tools
1. **Model Loader (`ta_model_loader`)**: Loads and caches Scikit-Learn/XGBoost models from the filesystem. Validates checksums.
2. **Inference Engine (`ta_inference_engine`)**: Runs model predictions asynchronously to avoid blocking the event loop.
3. **Confidence Calculator (`ta_confidence_calc`)**: Maps raw model scores and probabilities into a normalized confidence score (0.0-1.0) and a discrete `ThreatLevel`.
4. **Evidence Collector (`ta_evidence_collector`)**: Packages raw features and inference metrics into structured `Evidence` schemas.
5. **Gemini Reasoner (`ta_gemini_reasoner`)**: For events exceeding the confidence threshold, calls the Gemini API to formulate human-readable analysis and recommended actions.
6. **Threat Publisher (`ta_threat_publisher`)**: Persists the final `ThreatAnalysisResult` to the `IBlackboard` and publishes an `EventMessage` to the `IMessageBus`.

## Lifecycle Implementation
- **initialize()**: Instantiates and initializes all tools, and loads the configured active model.
- **validate()**: Uses Pydantic to ensure the incoming payload matches the `FeatureEventInput` schema, and queries `ISecurityProvider` to block injection attacks.
- **reason()**: Executes Inference, Confidence Calculation, and Evidence Collection.
- **plan()**: Conditionally triggers Gemini analysis if threat confidence is significant.
- **execute()**: Assembles the final `ThreatAnalysisResult`.
- **update_memory()**: Caches the result in `IMemoryStore`.
- **publish()**: Broadcasts the result to the blackboard and message bus.
- **health()**: Reports agent status and metrics.
- **shutdown()**: Safely cleans up resources.

## Configuration
Configuration is managed via Pydantic Settings in `config.py`.
- `model_dir`: Path to ML models
- `default_model_type`: Default model framework
- `confidence_threshold`: Minimum score to trigger Gemini reasoning
- `gemini_enabled`: Feature flag for LLM
