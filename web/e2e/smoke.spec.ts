import { test, expect } from '@playwright/test';

const ROUTES = [
  '/',
  '/monitor',
  '/shift',
  '/benchmark',
  '/explain',
  '/onboard',
  '/protocol-limits',
];

ROUTES.forEach((route) => {
  test(`Smoke test route: ${route} (no console errors)`, async ({ page }) => {
    const consoleErrors: string[] = [];

    // Listen for uncaught browser console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (exception) => {
      consoleErrors.push(exception.message);
    });

    // Navigate to route
    await page.goto(route);

    // Wait for content container to render
    await page.waitForSelector('main', { state: 'visible' });

    // Ensure no severe console errors were logged
    expect(consoleErrors).toEqual([]);
  });
});
