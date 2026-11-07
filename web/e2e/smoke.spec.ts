import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const isBackendMode = Boolean(process.env.ARGUS_E2E_BASE_URL || process.env.CI);

test.describe('ARGUS UI Smoke & Real Data Verification', () => {
  test('Page / (System Overview) renders verified research metrics', async ({ page }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        if (!isBackendMode) {
          // When running in local offline mode (no backend), Vite preview proxies /api/* to 502 ECONNREFUSED
          const text = msg.text();
          if (
            text.includes('Failed to load resource') ||
            text.includes('502 (Bad Gateway)') ||
            text.includes('ECONNREFUSED') ||
            text.includes('ERR_CONNECTION_REFUSED')
          ) {
            return;
          }
        }
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => pageErrors.push(err.message));

    await page.goto('/');
    await page.waitForSelector('main', { state: 'visible' });

    // Assert main header and research scope
    await expect(page.locator('text=ARGUS Cross-Domain Research Platform')).toBeVisible();
    await expect(page.locator('text=Binary Detector (Benign vs Attack)')).toBeVisible();

    // In backend mode, verify real benchmark metric MCC 0.3855 is loaded and rendered
    if (isBackendMode) {
      await expect(page.locator('text=0.3855').first()).toBeVisible({ timeout: 10000 });
    }

    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });

  test('Page /input (Input & Prediction) executes live inference', async ({ page }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        if (!isBackendMode) {
          const text = msg.text();
          if (
            text.includes('Failed to load resource') ||
            text.includes('502 (Bad Gateway)') ||
            text.includes('ECONNREFUSED') ||
            text.includes('ERR_CONNECTION_REFUSED')
          ) {
            return;
          }
        }
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => pageErrors.push(err.message));

    await page.goto('/input');
    await page.waitForSelector('main', { state: 'visible' });

    await expect(page.locator('text=Telemetry Input & Live Pipeline Inference')).toBeVisible();

    if (isBackendMode) {
      // Select verified sample from API
      const sampleBtn = page.locator('button:has-text("Domain:")').first();
      await expect(sampleBtn).toBeVisible({ timeout: 10000 });
      await sampleBtn.click();

      // Execute live pipeline inference
      const runBtn = page.locator('button:has-text("Run Live Inference")');
      await expect(runBtn).toBeEnabled();
      await runBtn.click();

      // Assert classification verdict badge renders real result
      const verdict = page.locator('text=ATTACK DETECTED').or(page.locator('text=BENIGN TRAFFIC')).first();
      await expect(verdict).toBeVisible({ timeout: 10000 });
    }

    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });

  test('Page /topology (Multi-Agent Processing) renders 10 nodes and triggers flow events', async ({ page }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        if (!isBackendMode) {
          const text = msg.text();
          if (
            text.includes('Failed to load resource') ||
            text.includes('502 (Bad Gateway)') ||
            text.includes('ECONNREFUSED') ||
            text.includes('ERR_CONNECTION_REFUSED')
          ) {
            return;
          }
        }
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => pageErrors.push(err.message));

    await page.goto('/topology');
    await page.waitForSelector('main', { state: 'visible' });

    // Switch to 2D SVG Fallback schematic
    const schematicTab = page.locator('button:has-text("2D SVG Fallback")');
    await expect(schematicTab).toBeVisible();
    await schematicTab.click();

    // Verify all 10 agent/engine nodes are rendered
    const expectedNodes = [
      'orchestrator',
      'message_bus',
      'api_gateway',
      'policy_engine',
      'data_intelligence',
      'threat_analysis',
      'explainability',
      'risk_prediction',
      'decision_support',
      'knowledge_context',
    ];

    for (const nodeId of expectedNodes) {
      const nodeLocator = page.locator(`[data-testid="topology-node-${nodeId}"]`);
      await expect(nodeLocator).toBeVisible({ timeout: 10000 });
    }

    // Trigger flow and assert events arrive from backend
    if (isBackendMode) {
      const triggerBtn = page.locator('button:has-text("Trigger Flow")');
      await expect(triggerBtn).toBeVisible({ timeout: 5000 });
      await triggerBtn.click();

      const flowEvent = page.locator('[data-testid="flow-event-item"]').first();
      await expect(flowEvent).toBeVisible({ timeout: 10000 });
      const count = await page.locator('[data-testid="flow-event-item"]').count();
      expect(count).toBeGreaterThan(0);
    }

    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });

  test('Page /explain (Explanation & Visualization) renders SHAP table and attributions', async ({ page }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        if (!isBackendMode) {
          const text = msg.text();
          if (
            text.includes('Failed to load resource') ||
            text.includes('502 (Bad Gateway)') ||
            text.includes('ECONNREFUSED') ||
            text.includes('ERR_CONNECTION_REFUSED')
          ) {
            return;
          }
        }
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => pageErrors.push(err.message));

    await page.goto('/explain');
    await page.waitForSelector('main', { state: 'visible' });

    await expect(page.locator('text=SHAP Explainability & Feature Ranking Analysis')).toBeVisible();

    if (isBackendMode) {
      // Assert SHAP vs Target Gain table rendered real features
      const featureCell = page
        .locator('table td:has-text("log_pkt_max")')
        .or(page.locator('table td:has-text("pkt_mean_to_max")'))
        .first();
      await expect(featureCell).toBeVisible({ timeout: 10000 });

      // Assert top contributing feature attribution computed
      await expect(page.locator('text=Top Contributing Feature')).toBeVisible({ timeout: 10000 });
    }

    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });

  test('Page /results (Results & Evaluation) matches verified Table IV MCC from CSV', async ({ page }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        if (!isBackendMode) {
          const text = msg.text();
          if (
            text.includes('Failed to load resource') ||
            text.includes('502 (Bad Gateway)') ||
            text.includes('ECONNREFUSED') ||
            text.includes('ERR_CONNECTION_REFUSED')
          ) {
            return;
          }
        }
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => pageErrors.push(err.message));

    // Read Table IV MCC directly from results/verified/five_model_complete_comparison.csv at test time
    const possiblePaths = [
      path.resolve(process.cwd(), 'results/verified/five_model_complete_comparison.csv'),
      path.resolve(process.cwd(), '../results/verified/five_model_complete_comparison.csv'),
    ];
    const csvPath = possiblePaths.find((p) => fs.existsSync(p));
    expect(csvPath, 'Verified benchmark CSV file must exist').toBeDefined();

    const csvContent = fs.readFileSync(csvPath!, 'utf-8');
    const lines = csvContent.trim().split('\n');
    const headers = lines[0].split(',').map((h) => h.trim());
    const mccIdx = headers.indexOf('MCC');
    expect(mccIdx).toBeGreaterThan(-1);

    const coralLine = lines.find((l) => l.startsWith('Clean Class-aware CORAL'));
    expect(coralLine, 'Clean Class-aware CORAL row must exist in CSV').toBeDefined();
    const rawMCC = parseFloat(coralLine!.split(',')[mccIdx].trim());
    const expectedMCC = rawMCC.toFixed(4); // '0.3855'

    await page.goto('/results');
    await page.waitForSelector('main', { state: 'visible' });

    await expect(page.locator('text=Verified 4-Architecture Performance Matrix')).toBeVisible({ timeout: 10000 });

    if (isBackendMode) {
      // Find row for Clean Class-aware CORAL and assert MCC matches CSV exactly
      const coralRow = page.locator('tr').filter({ hasText: 'Clean Class-aware CORAL' }).first();
      await expect(coralRow).toBeVisible({ timeout: 10000 });
      await expect(coralRow.locator('td').filter({ hasText: expectedMCC }).first()).toBeVisible({ timeout: 5000 });
    }

    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });

  test('3D Topology & Multi-Scene interactions', async ({ page }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        if (!isBackendMode) {
          const text = msg.text();
          if (
            text.includes('Failed to load resource') ||
            text.includes('502 (Bad Gateway)') ||
            text.includes('ECONNREFUSED') ||
            text.includes('ERR_CONNECTION_REFUSED')
          ) {
            return;
          }
        }
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => pageErrors.push(err.message));

    await page.goto('/topology');
    await page.waitForSelector('main', { state: 'visible' });

    // Verify Verified Flow Replay pill or WS status
    const replayBadge = page.locator('text=Verified Flow Replay');
    await expect(replayBadge.or(page.locator('text=WS Connecting')).first()).toBeVisible();

    // Scene switching controls with transition settle
    const domainShiftTab = page.locator('button:has-text("Domain Shift (CORAL)")');
    await expect(domainShiftTab).toBeVisible();
    await domainShiftTab.click();
    await page.waitForTimeout(200);

    const shapTab = page.locator('button:has-text("3D SHAP Scene")');
    await expect(shapTab).toBeVisible();
    await shapTab.click();
    await page.waitForTimeout(200);

    const timelineTab = page.locator('button:has-text("Decision Timeline")');
    await expect(timelineTab).toBeVisible();
    await timelineTab.click();
    await page.waitForTimeout(200);

    const schematicTab = page.locator('button:has-text("2D SVG Fallback")');
    await expect(schematicTab).toBeVisible();
    await schematicTab.click();
    await page.waitForTimeout(200);

    // Toggles
    const qualityBtn = page.locator('button:has-text("Quality:")');
    await expect(qualityBtn).toBeVisible();
    await qualityBtn.click();
    await page.waitForTimeout(100);

    const motionBtn = page.locator('button:has-text("Motion:")');
    await expect(motionBtn).toBeVisible();
    await motionBtn.click();
    await page.waitForTimeout(100);

    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
  });
});
