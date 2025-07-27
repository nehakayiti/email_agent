import { test, expect } from '@playwright/test';
import { realApiHelper } from './helpers/real-api-test-helper';

test.describe('Category Management CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    await realApiHelper.setupPage(page);
    await realApiHelper.createTestUser();
  });

  test.afterEach(async () => {
    await realApiHelper.cleanupTestData();
  });

  test('should load categories page and show form elements', async ({ page }) => {
    await test.step('Navigate to categories page', async () => {
      await realApiHelper.navigateToPage(page, '/categories/improved');
      await expect(page.locator('[data-testid="categories-page"]')).toBeVisible();
    });

    await test.step('Verify page elements are visible', async () => {
      // Check main heading
      await expect(page.locator('h1:has-text("Email Categories")')).toBeVisible();
      
      // Check add category button
      await expect(page.locator('[data-testid="add-category-btn"]')).toBeVisible();
      
      // Click add category button to show form
      await page.click('[data-testid="add-category-btn"]');
      
      // Verify form elements are visible
      await expect(page.locator('[data-testid="category-name-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="category-display-name-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="category-description-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="save-category-btn"]')).toBeVisible();
    });
  });
}); 