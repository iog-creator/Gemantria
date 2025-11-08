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

  // Keyboard open: focus + Enter
  await chip.focus();
  await page.keyboard.press('Enter');
  await page.waitForSelector('[role="dialog"]', { timeout: 3000 });
  // Body scroll-lock applied
  const overflow = await page.evaluate(() => getComputedStyle(document.body).overflow);
  expect(overflow).toBe('hidden');
  // Expect verse text (sample provides Genesis 1:1 / Romans 1:20)
  await page.waitForSelector('text=/In the beginning God created the heaven and the earth|clearly seen/', { timeout: 3000 });
  await page.screenshot({ path: 'evidence/ui/xrefs_sidepanel.png', fullPage: true });

  // Escape to close and ensure dialog is gone and scroll unlocked
  await page.keyboard.press('Escape');
  await page.waitForSelector('[role="dialog"]', { state: 'detached' });
  const overflow2 = await page.evaluate(() => getComputedStyle(document.body).overflow);
  expect(overflow2 === '' || overflow2 === 'visible').toBeTruthy();
});

