// Load the standalone CTK gallery page, report console errors, the build status and a screenshot.
// Usage: node tests/ctk-gallery.mjs [base url] [screenshot.png]
import { chromium } from "playwright-core";
const base = process.argv[2] ?? "http://localhost:4173/";
const shot = process.argv[3] ?? "ctk-gallery.png";
const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await (await browser.newContext({ viewport: { width: 1500, height: 1100 }, deviceScaleFactor: 1 })).newPage();
const errors = [];
page.on("pageerror", (e) => { errors.push(String(e)); console.log("[pageerror] " + String(e).slice(0, 300)); });
page.on("console", (m) => { if (m.type() === "error") { errors.push(m.text()); console.log("[console.error] " + m.text().slice(0, 300)); } });
await page.goto(base + "ctk-gallery.html");
await page.waitForFunction(() => /replicas built/.test(document.getElementById("status").textContent), null, { timeout: 180000 });
console.log("status:", await page.locator("#status").textContent());
const notes = await page.locator(".rep .missing").allTextContents();
console.log("notes:", notes.length, notes.filter((n) => n.startsWith("failed")));
console.log("custom elements:", await page.locator(".rep sw-button, .rep sw-checkbox, .rep sw-combobox, .rep sw-lineedit, .rep sw-slider, .rep sw-spinbox, .rep sw-range-slider, .rep sw-pathlineedit, .rep sw-colorpicker, .rep sw-progressbar, .rep sw-textedit, .rep sw-label").count());
// use a few replicas: the signals should be reported under them
await page.locator("#rep-ctkPushButton sw-button button").first().click();
await page.locator("#rep-ctkCheckBox input[type=checkbox]").first().click();
await page.locator("#rep-ctkCollapsibleButton > section > button").first().click();
await page.waitForTimeout(300);
for (const n of ["ctkPushButton", "ctkCheckBox", "ctkCollapsibleButton"]) console.log(n, "->", await page.locator(`[id="sig-${n}"]`).textContent());
await page.screenshot({ path: shot, fullPage: false });
await page.locator("#rep-QTabWidget").scrollIntoViewIfNeeded();
await page.waitForTimeout(200);
await page.screenshot({ path: shot.replace(".png", "-qt.png"), fullPage: false });
await page.locator("#theme").click();
await page.waitForTimeout(300);
await page.locator("#rep-ctkSliderWidget").scrollIntoViewIfNeeded();
await page.screenshot({ path: shot.replace(".png", "-dark.png"), fullPage: false });
console.log(`screenshots: ${shot}; errors: ${errors.length}`);
await browser.close();
process.exit(errors.length ? 1 : 0);
