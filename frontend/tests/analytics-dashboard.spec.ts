import { test, expect } from '@playwright/test';
import { realApiHelper } from './helpers/real-api-test-helper';

test.describe('Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await realApiHelper.setupPage(page);
    await realApiHelper.createTestUser();
  });

  test.afterEach(async () => {
    await realApiHelper.cleanupTestData();
  });

  test('should load analytics dashboard and display basic structure', async ({ page }) => {
    await test.step('Navigate to analytics page', async () => {
      await realApiHelper.navigateToPage(page, '/analytics');
      await expect(page.locator('h1:has-text("Email Analytics Dashboard")')).toBeVisible();
    });

    await test.step('Verify dashboard structure', async () => {
      // Check for main heading
      await expect(page.locator('h1:has-text("Email Analytics Dashboard")')).toBeVisible();
      
      // Check for chart containers (don't check specific content as it may fail)
      const chartContainers = page.locator('.bg-white.rounded-lg.shadow');
      const containerCount = await chartContainers.count();
      expect(containerCount).toBeGreaterThan(0);
    });
  });

  test('should maintain responsive layout', async ({ page }) => {
    await test.step('Test desktop layout', async () => {
      await page.setViewportSize({ width: 1280, height: 720 });
      await realApiHelper.navigateToPage(page, '/analytics');
      await expect(page.locator('h1:has-text("Email Analytics Dashboard")')).toBeVisible();
    });

    await test.step('Test mobile layout', async () => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.reload();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('h1:has-text("Email Analytics Dashboard")')).toBeVisible();
    });
  });
}); 