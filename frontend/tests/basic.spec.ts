import { test, expect } from '@playwright/test';

test('redirects to login when accessing inbox without login', async ({ page }) => {
  await page.goto('http://localhost:3000/emails?view=inbox');
  await expect(page).toHaveURL(/\/login/);
});

test('shows sign in with Google button when not logged in', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.getByRole('button', { name: /sign in with google/i })).toBeVisible();
});