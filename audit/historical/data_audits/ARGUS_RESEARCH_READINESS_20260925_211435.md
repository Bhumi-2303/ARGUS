# ARGUS CURRENT STATUS & RESEARCH READINESS

## Current Status
- **PROJECT MATURITY**: Prototype / Scaffolding.
- **SCIENTIFIC STATUS**: INVALID. Catastrophic data leakage and fabricated results.
- **EXPERIMENTAL STATUS**: BROKEN.
- **REPRODUCIBILITY**: IMPOSSIBLE (metrics in README do not match any runnable pipeline).
- **PAPER READINESS**: NOT READY.

## Single Biggest Blocker
Data leakage (85%+ identical samples between train and test splits) entirely invalidates all cross-domain experiments.

## What Work is Genuinely Complete?
- Basic agent boilerplate (scaffolding).
- Frontend UI boilerplate (React/Vite).

## What Previous Results Should NOT be Used?
**ALL OF THEM**. None of the metrics in `ARGUS_RESULTS_README.txt` can be used.

## What Must Be Rebuilt?
1. The datasets must be strictly deduplicated and separated to guarantee zero target leakage.
2. The ML pipeline must be rewritten to execute *through* the agents, rather than bypass them.
3. The DG/DA evaluation scripts must be rebuilt to actually optimize and evaluate thresholds properly.
