import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  workers: 1,
  timeout: 60000,
  expect: { timeout: 15000 },
  reporter: "line",
  outputDir: "../../.cache/demo-browser-tests",
  use: {
    baseURL: "http://127.0.0.1:8000",
    channel: "chrome",
    headless: true,
    reducedMotion: "reduce",
    viewport: { width: 1440, height: 1050 },
    screenshot: "only-on-failure",
  },
});
