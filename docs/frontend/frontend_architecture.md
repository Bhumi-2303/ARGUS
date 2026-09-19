# ARGUS Frontend Architecture

## Page Structure
The frontend has been transformed into a professional cybersecurity operations interface.
The major views are:
1. **Command Center** (`/`): Shows active incidents, critical risk, events requiring action, and critical assets.
2. **Incident Investigation** (`/incidents/:id`): Detailed view for a specific incident showing threat context, risk score, and response policy, with approval mechanisms.
3. **Agent Execution Trace** (Component in Incident Investigation): Visual pipeline of the agent processing (Detector -> Risk -> Knowledge -> Explainability -> Decision -> Response).
4. **Asset Intelligence** (`/assets`): Asset monitoring and historical risk tracking.
5. **Analytics** (`/analytics`): Separate tracking for research metrics like F1, MCC, FPR.
6. **System Health** (`/health`): Monitors health of the Detector, Risk, Knowledge, Explainability, Decision, Orchestrator, and LLM components.

## API Integration
The frontend uses the actual backend APIs instead of mock data:
- `GET /api/v1/incidents/`
- `GET /api/v1/incidents/{id}`
- `GET /api/v1/incidents/{id}/timeline`
- `PATCH /api/v1/incidents/{id}/status`
- `POST /api/v1/incidents/{id}/approve`
- `GET /api/v1/health`

A clean service layer (`src/services/api.ts`) is implemented using `fetch` with JWT authentication passed through the `Authorization` header.

## State Management
State is managed locally using React's `useState` and `useEffect` hooks for simplicity and modularity. Loading and error states are tracked independently for each view.

## Error Handling
The application handles various failure modes gracefully:
- **Loading:** Displays a "LOADING SOC DATA..." pulse indicator.
- **Error/Timeout:** Displays clear error messages.
- **Backend Unavailable:** System Health view detects backend unavailability and gracefully shows a degraded view.

## Deployment & Testing
- The React 18 / `@react-three/drei` React 19 dependency conflict has been resolved structurally in `package.json` using npm `overrides`, allowing `npm install` and `npm run build` to work natively without `--legacy-peer-deps`.

## Status
1. Frontend pages implemented
2. APIs connected
3. Mock data removed
4. Build status: Passing
5. Remaining issues: None
