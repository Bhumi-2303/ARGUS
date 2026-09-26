import { test, expect } from '@playwright/test';

const ROUTES = [
  '/',
  '/monitor',
  '/topology',
  '/shift',
  '/benchmark',
  '/explain',
  '/onboard',
  '/protocol-limits',
];

test.describe('ARGUS Platform Multi-Page Smoke Tests', () => {
  ROUTES.forEach((route) => {
    test(`Route '${route}' renders cleanly without console errors`, async ({ page }) => {
      const consoleErrors: string[] = [];

      // Listen for uncaught console errors
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });

      // Listen for uncaught JS exceptions
      page.on('pageerror', (exception) => {
        consoleErrors.push(exception.message);
      });

      await page.goto(route);
      await page.waitForLoadState('domcontentloaded');

      // Assert zero console errors
      expect(consoleErrors).toEqual([]);
    });
  });
});
