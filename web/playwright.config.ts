import { defineConfig, devices } from '@playwright/test';

const baseURL =
  process.env.ARGUS_E2E_BASE_URL ||
  (process.env.CI ? 'http://127.0.0.1:8000' : 'http://127.0.0.1:5173');

const hasExplicitBackend = Boolean(process.env.ARGUS_E2E_BASE_URL || process.env.CI);

export default defineConfig({
  testDir: './e2e',
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL,
    trace: 'on-first-retry',
  },
  webServer: hasExplicitBackend
    ? undefined
    : {
        command: 'npm run preview -- --host 127.0.0.1 --port 5173',
        url: 'http://127.0.0.1:5173',
        reuseExistingServer: true,
        timeout: 120 * 1000,
        stdout: 'pipe',
        stderr: 'pipe',
      },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
