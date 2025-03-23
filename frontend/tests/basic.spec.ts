import { test, expect } from '@playwright/test';

test('homepage loads', async ({ page }) => {
  await page.goto('http://localhost:3000'); // adjust port if needed
  await expect(page).toHaveTitle(/Email Agent/i); // or look for some text
});