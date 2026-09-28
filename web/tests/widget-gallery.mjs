// Open SlicerWeb with the Widget Gallery extension, show the module, report errors, coverage and
// widget failures, and save a screenshot.
// Usage: node tests/widget-gallery.mjs [base url] [screenshot.png]
import { chromium } from "playwright-core";

const base = process.argv[2] ?? "http://localhost:4173/";
const shot = process.argv[3] ?? "gallery.png";
const browser = await chromium.launch({ channel: "chrome", headless: true, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await (await browser.newContext({ viewport: { width: 1700, height: 1100 } })).newPage();
const t0 = Date.now();
const stamp = () => ((Date.now() - t0) / 1000).toFixed(1).padStart(6);
const errors = [];
page.on("pageerror", (e) => { errors.push(String(e)); console.log(`${stamp()} [pageerror] ${String(e).slice(0, 300)}`); });
page.on("console", (m) => {
  const t = m.text();
  if (m.type() === "error" && !/GL Driver|WebGL/.test(t)) { errors.push(t); console.log(`${stamp()} [console.error] ${t.slice(0, 400)}`); }
  else if (/WidgetGallery|Widget Gallery|slicerweb\.qt/.test(t)) console.log(`${stamp()} [${m.type()}] ${t.slice(0, 300)}`);
});
page.on("dialog", (d) => { console.log(`${stamp()} [dialog] ${d.message().slice(0, 100)}`); d.dismiss(); });

await page.goto(base + "?extensions=WidgetGallery&sample=MRHead");
await page.waitForFunction(() => window.slicerWeb?.store?.status === "ready", null, { timeout: 300000 });
console.log(`${stamp()} application ready`);
await page.waitForFunction(() => window.slicerWeb.store.modules.some((m) => m.name === "WidgetGallery"), null, { timeout: 120000 });
console.log(`${stamp()} WidgetGallery module registered`);
await page.waitForFunction(() => /MR-head/i.test(document.body.innerText), null, { timeout: 120000 }).catch(() => console.log("sample not loaded (continuing)"));
await page.evaluate(() => { window.slicerWeb.store.activeModule = "WidgetGallery"; });
await page.waitForFunction(() => document.querySelector(".sw-scripted-module section"), null, { timeout: 120000 });
await page.waitForTimeout(2500);
console.log(`${stamp()} module panel shown`);

const py = async (code) => String(await page.evaluate((c) => window.slicerWeb.bridge.evalPython(c, "eval"), code));
console.log("sections:", await py(`len(slicer.modules.WidgetGalleryWidget._sections)`));
console.log("failures:", await py(`slicer.modules.WidgetGalleryWidget.failures`));
console.log("coverage:", await py(`(lambda rows: {g: {s: sum(1 for gg, n, ss in rows if gg == g and ss == s) for s in ("available", "via base", "placeholder", "missing")} for g in dict.fromkeys(gg for gg, _, _ in rows)})(__import__("WidgetGallery").coverage())`));
console.log("missing:", await py(`sorted(n for g, n, s in __import__("WidgetGallery").coverage() if s == "missing")`));
console.log("placeholders:", await py(`sorted(n for g, n, s in __import__("WidgetGallery").coverage() if s == "placeholder")`));

// exercise a few controls through the page, and create the demo scene
await page.evaluate(() => window.slicerWeb.bridge.evalPython("slicer.modules.WidgetGalleryWidget.createDemoNodes()"));
await page.waitForTimeout(2000);
const log = await py(`slicer.modules.WidgetGalleryWidget.eventLog.plainText`);
console.log("event log:\n" + log.replace(/\\n/g, "\n").slice(0, 3000));
const panel = page.locator(".sw-scripted-module").first();
console.log("widgets in panel:", await panel.locator("*").count(), "custom elements:", await panel.locator("sw-button, sw-checkbox, sw-combobox, sw-lineedit, sw-slider, sw-spinbox, sw-range-slider, sw-node-selector, sw-pathlineedit, sw-colorpicker, sw-progressbar, sw-textedit, sw-label").count());
await page.screenshot({ path: shot, fullPage: false });
console.log(`screenshot: ${shot}; page errors: ${errors.length}`);
await browser.close();
process.exit(errors.length ? 1 : 0);
