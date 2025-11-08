import { test, expect } from '@playwright/test';

test('xrefs page renders chips and opens side panel', async ({ page }) => {
  const url = process.env.UI_URL || 'http://localhost:5173';

  await page.goto(url, { waitUntil: 'networkidle' });

  // Navigate to Cross-References tab if present
  const tab = page.getByRole('tab', { name: /cross-?references/i });
  if (await tab.count()) await tab.click();

  // Wait for noun cards/chips
  await page.waitForSelector('.xref-chip');

  // Screenshot grid
  await page.screenshot({ path: 'evidence/ui/xrefs_grid.png', fullPage: true });

  // Hover first chip and screenshot
  const chip = page.locator('.xref-chip').first();
  await chip.hover();
  await page.screenshot({ path: 'evidence/ui/xrefs_hover.png' });

  // Click to open side panel and screenshot
  await chip.click();
  await page.waitForSelector('[class*="SidePanel"], [class*="side-panel"], text=/Close/i', { timeout: 3000 });
  // Expect verse text (sample provides Genesis 1:1 / Romans 1:20)
  await page.waitForSelector('text=/In the beginning God created the heaven and the earth|clearly seen/', { timeout: 3000 });
  await page.screenshot({ path: 'evidence/ui/xrefs_sidepanel.png', fullPage: true });
});

