import { test, expect } from '@playwright/test';

const ACTIVE_PAGES = [
  { path: '/', title: 'System Overview' },
  { path: '/input', title: 'Input & Prediction' },
  { path: '/topology', title: 'Multi-Agent Processing' },
  { path: '/explain', title: 'Explanation & Visualization' },
  { path: '/results', title: 'Results & Evaluation' },
];

ACTIVE_PAGES.forEach(({ path, title }) => {
  test(`Smoke test page: ${title} (${path})`, async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      // Ignore normal react/dev warnings
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (exception) => {
      consoleErrors.push(exception.message);
    });

    await page.goto(path);
    await page.waitForSelector('main', { state: 'visible' });

    // Expect page heading or title container
    const mainContent = await page.locator('main').innerText();
    expect(mainContent.length).toBeGreaterThan(10);
    expect(consoleErrors).toEqual([]);
  });
});

test.describe('3D Topology & Multi-Scene Smoke Tests', () => {
  test('Topology page renders scenes, quality toggles, and controls', async ({ page }) => {
    await page.goto('/topology');
    await page.waitForSelector('main', { state: 'visible' });

    // 1. Verify Verified Flow Replay pill
    const replayBadge = page.locator('text=Verified Flow Replay');
    await expect(replayBadge.or(page.locator('text=WS Connecting'))).toBeVisible();

    // 2. Test switching to Domain Shift scene
    const domainShiftTab = page.locator('button:has-text("Domain Shift (CORAL)")');
    await expect(domainShiftTab).toBeVisible();
    await domainShiftTab.click();

    // 3. Test switching to 3D SHAP Scene
    const shapTab = page.locator('button:has-text("3D SHAP Scene")');
    await expect(shapTab).toBeVisible();
    await shapTab.click();

    // 4. Test switching to Decision Timeline
    const timelineTab = page.locator('button:has-text("Decision Timeline")');
    await expect(timelineTab).toBeVisible();
    await timelineTab.click();

    // 5. Test switching to 2D Schematic
    const schematicTab = page.locator('button:has-text("2D SVG Fallback")');
    await expect(schematicTab).toBeVisible();
    await schematicTab.click();

    // 6. Test Quality toggle
    const qualityBtn = page.locator('button:has-text("Quality:")');
    await expect(qualityBtn).toBeVisible();
    await qualityBtn.click();

    // 7. Test Motion toggle
    const motionBtn = page.locator('button:has-text("Motion:")');
    await expect(motionBtn).toBeVisible();
    await motionBtn.click();
  });
});
