import { test, expect } from '@playwright/test';

test('should have correct title', async ({ page }) => {
  // Navigate to the home page
  await page.goto('/');
  
  // Check that the page title is "Email Agent"
  await expect(page).toHaveTitle('Email Agent');
}); 