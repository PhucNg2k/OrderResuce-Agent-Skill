import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://127.0.0.1:4387', headless: true },
  webServer: { command: 'node_modules/.bin/tsx e2e/test-server.ts', port: 4387, reuseExistingServer: false, timeout: 30_000 },
});
