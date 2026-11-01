// QA: open index.html at desktop and phone widths, log console errors, take screenshots to qa/.
// Run from the study root with a static server (python3 -m http.server 8941; set PORT to change).
const { chromium } = require("playwright");
// Leaflet from a local npm copy (the CDN is not reachable from the build container); tiles and fonts are blocked here.
const LEAF = process.env.LEAFLET_DIST || "/dev/shm/nuclear/npm/node_modules/leaflet/dist";
(async () => {
  const b = await chromium.launch();
  const errs = [];
  for (const [nm, vw, vh] of (process.env.ONLY ? [[process.env.ONLY, process.env.ONLY === "phone" ? 390 : 1280, 900]] : [["desktop", 1280, 900], ["phone", 390, 844]])) {
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: nm === "phone" ? 2 : 1 });
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    await p.route(/leaflet.min.js/, r => r.fulfill({ path: LEAF + "/leaflet.js" }));
    await p.route(/leaflet.min.css/, r => r.fulfill({ path: LEAF + "/leaflet.css" }));
    p.on("console", m => { if (m.type() === "error" && !/ERR_FAILED|net::/.test(m.text())) errs.push(nm + ": " + m.text()); });
    p.on("pageerror", e => errs.push(nm + " pageerror: " + e.message));
    await p.goto("http://localhost:" + (process.env.PORT || 8941) + "/index.html", { waitUntil: "networkidle" });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `qa/${nm}_top.png` });
    const shot = async (sel, f) => { await p.locator(sel).scrollIntoViewIfNeeded(); await p.waitForTimeout(700); await p.locator(sel).screenshot({ path: `qa/${nm}_${f}.png` }); };
    await shot("#atlas", "map");
    await p.click('#envRow [data-e="atm"]'); await p.waitForTimeout(700); await shot("#atlas", "atm");
    await p.click('#envRow [data-e="ug"]'); await p.click('#colRow [data-c="env"]'); await p.waitForTimeout(700); await shot("#atlas", "ug_env");
    await p.click('#envRow [data-e="all"]'); await p.click('#colRow [data-c="country"]');
    await p.click('#eraRow [data-y="1958,1962"]'); await p.waitForTimeout(700); await shot("#atlas", "era_58_62");
    await p.click('#eraRow [data-y="1945,2017"]');
    await p.click("#focusRow .btn:nth-child(7)"); await p.waitForTimeout(1200); await shot("#atlas", "bikini");
    await p.click("#focusRow .btn:nth-child(4)"); await p.waitForTimeout(1200); await shot("#atlas", "novaya");
    await p.click("#focusRow .btn:nth-child(2)"); await p.click("#play"); await p.waitForTimeout(12500); await shot("#atlas", "playing");
    await p.click("#play"); await p.click('#eraRow [data-y="1945,2017"]');
    await p.click(".lyrBtn"); await p.check('.lyrPanel [data-k="names"]'); await p.selectOption('.lyrPanel [data-k="base"]', "ocean"); await p.waitForTimeout(800); await shot("#map", "layers_panel"); await p.click(".lyrBtn");
    await p.fill("#q", "Tsar"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(1800); await shot("#atlas", "search_tsar");
    await p.fill("#q", "Maralinga"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(1800); await shot("#atlas", "search_maralinga");
    await p.fill("#q", "Castle Bravo"); await p.waitForTimeout(500); await p.keyboard.press("Enter"); await p.waitForTimeout(1800); await shot("#atlas", "search_bravo");
    for (const c of ["yearChart", "envChart", "yieldChart", "bigChart", "kindChart", "siteGrid", "nkChart"]) await shot("#" + c, c);
    await p.click('#yrMode [data-m="env"]'); await p.waitForTimeout(400); await shot("#yearChart", "yearChart_env");
    await p.click('#yrMode [data-m="yield"]'); await p.waitForTimeout(400); await shot("#yearChart", "yearChart_yield");
    await p.click('#ydMode [data-m="s"]'); await p.waitForTimeout(400); await shot("#yieldChart", "yieldChart_sites");
    await p.click("#siteGrid summary, #siteGrid + details summary").catch(() => {});
    if (nm === "phone") {
      await p.click("#theme"); await p.waitForTimeout(1500); await shot("#atlas", "dark_map"); await shot("#yearChart", "dark_year");
      await p.locator("#atlas").scrollIntoViewIfNeeded(); await p.click(".mfs-btn"); await p.waitForTimeout(1500); await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
    } else {
      await p.locator("#atlas").scrollIntoViewIfNeeded(); await p.click(".mfs-btn"); await p.waitForTimeout(1500); await p.screenshot({ path: `qa/${nm}_fullscreen.png` });
      await p.keyboard.press("Escape"); await p.waitForTimeout(500);
    }
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    console.log(nm, "horizontal overflow px:", ov);
    await p.close();
  }
  console.log("errors:", errs.length ? errs : "none");
  await b.close();
})();
