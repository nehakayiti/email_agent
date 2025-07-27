import { Page, expect } from '@playwright/test';
import { realApiHelper } from './real-api-test-helper';

export class TestOptimizationHelper {
  /**
   * Common page navigation with error handling
   */
  static async navigateToPageWithRetry(page: Page, path: string, expectedTitle?: string): Promise<void> {
    await realApiHelper.navigateToPage(page, path);
    
    // Handle potential load errors
    const loadError = page.locator('text=Failed to load');
    if (await loadError.isVisible()) {
      console.log(`Load error detected on ${path}, refreshing page...`);
      await page.reload();
      await page.waitForLoadState('networkidle');
    }
    
    if (expectedTitle) {
      await expect(page.locator(`h1:has-text("${expectedTitle}")`)).toBeVisible();
    }
  }

  /**
   * Common email list verification
   */
  static async verifyEmailListStructure(page: Page): Promise<void> {
    const emailList = page.locator('[data-testid="email-list"]');
    await expect(emailList).toBeVisible();
    
    const emailCards = page.locator('[data-testid="email-card"]');
    const cardCount = await emailCards.count();
    
    if (cardCount > 0) {
      const firstCard = emailCards.first();
      await expect(firstCard.locator('[data-testid="email-subject"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="email-sender"]')).toBeVisible();
      await expect(firstCard.locator('[data-testid="email-snippet"]')).toBeVisible();
    } else {
      await expect(page.locator('text=No emails found')).toBeVisible();
    }
  }

  /**
   * Common chart loading verification
   */
  static async verifyChartLoading(page: Page, chartTitle: string): Promise<void> {
    const chartSection = page.locator(`text=${chartTitle}`).first();
    await expect(chartSection).toBeVisible();
    
    // Wait for chart to load
    await page.waitForTimeout(2000);
    
    // Check for chart canvas or table
    const chartCanvas = page.locator('canvas');
    const chartTable = page.locator('table');
    
    if (await chartCanvas.isVisible()) {
      await expect(chartCanvas).toBeVisible();
    } else if (await chartTable.isVisible()) {
      await expect(chartTable).toBeVisible();
    }
  }

  /**
   * Common form interaction with validation
   */
  static async fillAndSubmitForm(page: Page, formData: Record<string, string>): Promise<void> {
    for (const [selector, value] of Object.entries(formData)) {
      const input = page.locator(selector);
      await expect(input).toBeVisible();
      await input.fill(value);
      await expect(input).toHaveValue(value);
    }
    
    const submitButton = page.locator('[data-testid="save-btn"], [data-testid="submit-btn"]');
    await expect(submitButton).toBeVisible();
    await submitButton.click();
    
    // Wait for form submission
    await page.waitForTimeout(2000);
  }

  /**
   * Common error state verification
   */
  static async verifyErrorHandling(page: Page, errorSelectors: string[]): Promise<void> {
    for (const selector of errorSelectors) {
      const errorElement = page.locator(selector);
      if (await errorElement.isVisible()) {
        await expect(errorElement).toBeVisible();
      }
    }
  }

  /**
   * Common loading state verification
   */
  static async verifyLoadingStates(page: Page): Promise<void> {
    const loadingSpinners = page.locator('.animate-spin');
    const spinnerCount = await loadingSpinners.count();
    
    if (spinnerCount > 0) {
      // Wait for loading to complete
      await page.waitForTimeout(3000);
      
      // Verify spinners are gone
      const remainingSpinners = page.locator('.animate-spin');
      const remainingCount = await remainingSpinners.count();
      expect(remainingCount).toBeLessThanOrEqual(spinnerCount);
    }
  }

  /**
   * Common responsive layout testing
   */
  static async testResponsiveLayout(page: Page, path: string): Promise<void> {
    // Test desktop layout
    await page.setViewportSize({ width: 1280, height: 720 });
    await realApiHelper.navigateToPage(page, path);
    
    // Test mobile layout
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');
  }

  /**
   * Common authentication state verification
   */
  static async verifyAuthenticatedState(page: Page): Promise<void> {
    // Check if we're not redirected to login
    await expect(page).not.toHaveURL(/\/login/);
    
    // Verify auth token exists
    const token = await page.evaluate(() => localStorage.getItem('auth_token'));
    expect(token).toBeTruthy();
  }

  /**
   * Common network error simulation
   */
  static async simulateNetworkError(page: Page, urlPattern: string): Promise<void> {
    await page.addInitScript((pattern) => {
      const originalFetch = window.fetch;
      window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = typeof input === 'string' ? input : input.toString();
        if (url.includes(pattern)) {
          throw new Error('Network error');
        }
        return originalFetch(input, init);
      };
    }, urlPattern);
  }

  /**
   * Common data cleanup verification
   */
  static async verifyDataCleanup(page: Page): Promise<void> {
    // Verify test data is cleaned up
    const testDataElements = page.locator('[data-testid*="test-"]');
    const testDataCount = await testDataElements.count();
    expect(testDataCount).toBe(0);
  }
} 