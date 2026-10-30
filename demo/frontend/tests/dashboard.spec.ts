import { test, expect } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

test("real inference, all theme/language pairs, references, CSV and mobile", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const directory = resolve("../checks/screenshots");
  mkdirSync(directory, { recursive: true });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Không gian dự báo." }),
  ).toBeVisible();
  await expect(page.locator("html")).toHaveClass("dark");
  await expect(page.locator("html")).toHaveAttribute("lang", "vi");
  await expect(
    page.getByRole("button", { name: "Chạy dự báo", exact: true }),
  ).toBeEnabled();
  await page.screenshot({ path: resolve(directory, "dark-vi-ready.png") });
  await page.getByRole("button", { name: "Chạy dự báo", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(20);
  await expect(
    page.getByRole("button", { name: "Tải CSV", exact: true }),
  ).toBeEnabled();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "Tải CSV", exact: true }).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toContain("kronos-small");
  await page.screenshot({ path: resolve(directory, "dark-vi-forecast.png") });
  await page
    .getByRole("button", { name: "Switch to English", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "A space for forecasts." }),
  ).toBeVisible();
  await expect(page.locator("tbody tr")).toHaveCount(20);
  await page.screenshot({ path: resolve(directory, "dark-en.png") });
  await page
    .getByRole("button", { name: "Switch to light theme", exact: true })
    .click();
  await expect(page.locator("html")).not.toHaveClass("dark");
  await page
    .getByRole("switch", { name: "Compare actuals", exact: true })
    .click();
  await expect(
    page.getByRole("columnheader", { name: "Actual · Close" }),
  ).toBeVisible();
  await page.screenshot({ path: resolve(directory, "light-en.png") });
  await page
    .getByRole("button", { name: "Chuyển sang tiếng Việt", exact: true })
    .click();
  await expect(page.locator("html")).toHaveAttribute("lang", "vi");
  await page.screenshot({ path: resolve(directory, "light-vi.png") });
  await page.reload();
  await expect(page.locator("html")).not.toHaveClass("dark");
  await expect(page.locator("html")).toHaveAttribute("lang", "vi");
  await expect(
    page.getByRole("button", { name: "Chạy dự báo", exact: true }),
  ).toBeEnabled();
  // A new origin resets the old forecast and uses its own full observed calendar.
  await page.getByRole("combobox").click();
  const options = page.getByRole("option");
  await options.nth(1).click();
  await expect(
    page.getByRole("button", { name: "Chạy dự báo", exact: true }),
  ).toBeEnabled();
  await page.getByRole("button", { name: "Kronos Mini" }).click();
  await page.getByRole("button", { name: "Chạy dự báo", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(20);
  await page.getByRole("tab", { name: "Mở cửa", exact: true }).click();
  await page.getByRole("button", { name: "5 phiên", exact: true }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: resolve(directory, "mobile-light-vi.png") });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.getByRole("button", { name: "Chuyển sang giao diện tối" }).click();
  await page.locator(".chart-card").scrollIntoViewIfNeeded();
  await page.screenshot({
    path: resolve(directory, "mobile-dark-vi-chart.png"),
  });
  expect(errors).toEqual([]);
  writeFileSync(
    resolve("../checks/browser.json"),
    JSON.stringify(
      {
        status: "pass",
        browser: "Chrome",
        themes: ["dark", "light"],
        languages: ["vi", "en"],
        real_models: ["kronos-small", "kronos-mini"],
        forecast_rows: 20,
        reference_toggle: true,
        csv_download: true,
        preferences_persist: true,
        mobile_no_horizontal_overflow: true,
        page_errors: errors,
      },
      null,
      2,
    ),
  );
});
