# ARGUS Demo Backup & Contingency Checklist

This document provides step-by-step procedures for screen recording, static screenshot capture, and offline no-network verification.

---

## 📹 1. Screen-Recording Procedure

1. **Resolution & Environment**:
   * Set display resolution to $1920 \times 1080$ (1080p) or minimum $1280 \times 720$.
   * Open browser in fullscreen or max window mode (`F11`).
2. **Recording Software**:
   * Launch OBS Studio, QuickTime, or Windows Game Bar (`Win + Alt + R`).
   * Select window capture on `http://localhost:8000`.
3. **Timestamp Marker Plan**:
   * `0:00 - 1:00`: Overview Page (`/`) — Highlight 4 story tiles & ProvenanceBadges.
   * `1:00 - 2:00`: Live Monitor (`/monitor`) — Start 10x stream, trigger mid-stream domain switch alert.
   * `2:00 - 3:00`: Model Comparison (`/benchmark`) & SHAP Explainability (`/explain`).
   * `3:00 - 4:00`: Onboarding Wizard (`/onboard`) & Protocol Limits (`/protocol-limits`).

---

## 📸 2. Exporting Static Screenshots of Each Page

Execute Playwright screenshot exporter script:

```bash
npx playwright test e2e/smoke.spec.ts --update-snapshots
```

Static screenshot destination paths for offline slide decks:

1. **Overview Page (`/`)**: `artifacts/figures/phase4/overview_page.png`
2. **Live Monitor (`/monitor`)**: `artifacts/figures/phase4/live_monitor_page.png`
3. **Domain Shift (`/shift`)**: `artifacts/figures/phase4/domain_shift_page.png`
4. **Model Comparison (`/benchmark`)**: `artifacts/figures/phase4/model_comparison_page.png`
5. **SHAP Explainability (`/explain`)**: `artifacts/figures/phase4/explainability_page.png`
6. **Onboarding Wizard (`/onboard`)**: `artifacts/figures/phase4/onboarding_wizard_page.png`
7. **Protocol & Limits (`/protocol-limits`)**: `artifacts/figures/phase4/protocol_limits_page.png`

---

## 🔌 3. Offline "No-Network" Verification Test

To verify that ARGUS operates 100% offline without external network dependency:

1. **Disable Network Interfaces**:
   * Windows PowerShell: `Disable-NetAdapter -Name "*" -Confirm:$false`
   * Or disconnect Wi-Fi and unplug Ethernet cable.
2. **Run Demo Launcher**:
   ```bash
   make demo
   ```
3. **Verify Local Host Access**:
   * Open browser to `http://localhost:8000`.
   * Verify all 7 pages load without console errors or failed network fetches.
   * Run API verification: `python scripts/verify_ui_numbers.py` ($\checkmark$ PASS).
