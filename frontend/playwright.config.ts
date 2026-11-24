import { defineConfig, devices } from '@playwright/test';

// Browser tests for the built SPA. Every /api call and every non-localhost request is
// mocked or blocked in the browser (see e2e/fixtures.ts), so no Flask API on :5000 is needed.
const port = 4173;

export default defineConfig({
  testDir: './e2e',
  // `*.e2e.ts` never matches Vitest's default `*.test`/`*.spec` include.
  testMatch: '**/*.e2e.ts',
  outputDir: './e2e/test-results',
  globalSetup: './e2e/global-setup.ts',
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  reporter: [['list']],
  use: {
    baseURL: `http://localhost:${port}`,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
  ],
  webServer: {
    command: `npm run build && npx vite preview --port ${port} --strictPort`,
    url: `http://localhost:${port}`,
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
