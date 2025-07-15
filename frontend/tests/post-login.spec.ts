import { test, expect } from '@playwright/test';

test('authenticated user can access /emails', async ({ page }) => {
  // Set up authenticated state in test mode
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'test_token_' + Date.now());
    (window as any).process = { env: { NEXT_PUBLIC_TEST_MODE: 'true', NODE_ENV: 'test' } };
  });

  // Navigate to the protected page
  await page.goto('/emails');

  // Assert: not redirected to login (this is the core test)
  await expect(page).not.toHaveURL(/\/login/);
  
  // Assert: we're on the emails page
  await expect(page).toHaveURL(/\/emails/);
}); 