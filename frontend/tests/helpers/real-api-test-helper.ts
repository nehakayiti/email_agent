import { Page } from '@playwright/test';

export interface TestUser {
  id: string;
  email: string;
  token: string;
}

export class RealApiTestHelper {
  private baseUrl: string;
  private testUser: TestUser | null = null;

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  /**
   * Create a test user and return authentication info
   */
  async createTestUser(): Promise<TestUser> {
    const testEmail = `test-${Date.now()}@example.com`;
    
    // For now, use a simple test user creation that works with the existing backend
    // The backend already has a test user mechanism in dependencies.py
    const token = `test_token_${Date.now()}`;
    
    this.testUser = {
      id: `test-user-${Date.now()}`,
      email: testEmail,
      token
    };

    return this.testUser;
  }

  /**
   * Setup page for testing with real API
   */
  async setupPage(page: Page, user?: TestUser): Promise<TestUser> {
    const testUser = user || this.testUser || await this.createTestUser();

    // Configure environment variables
    await page.addInitScript(() => {
      (window as any).process = { 
        env: { 
          NEXT_PUBLIC_API_URL: 'http://localhost:8001',
          NEXT_PUBLIC_TEST_MODE: 'false'
        } 
      };
    });

    // Set auth token
    await page.addInitScript((token) => {
      localStorage.setItem('auth_token', token);
    }, testUser.token);

    return testUser;
  }

  /**
   * Navigate to a page and wait for it to load
   */
  async navigateToPage(page: Page, path: string): Promise<void> {
    await page.goto(path);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Wait for React hydration
  }

  /**
   * Wait for a page to load and verify it's not a 404
   */
  async waitForPageLoad(page: Page, expectedTitle?: string): Promise<void> {
    // Check for 404 page
    const is404Page = await page.locator('text=404').isVisible();
    if (is404Page) {
      console.log('DEBUG: 404 page detected, page content:', await page.content());
      throw new Error('Page returned 404 - route not found');
    }

    // Wait for main content
    if (expectedTitle) {
      await page.waitForSelector(`h1:has-text("${expectedTitle}")`, { timeout: 10000 });
    } else {
      await page.waitForSelector('h1', { timeout: 10000 });
    }
  }

  /**
   * Create test categories for testing
   */
  async createTestCategories(): Promise<void> {
    if (!this.testUser) {
      throw new Error('No test user available. Call createTestUser() first.');
    }

    const categories = [
      {
        name: 'test_category_1',
        display_name: 'Test Category 1',
        description: 'First test category',
        priority: 50,
        is_system: false
      },
      {
        name: 'test_category_2', 
        display_name: 'Test Category 2',
        description: 'Second test category',
        priority: 60,
        is_system: false
      }
    ];

    for (const category of categories) {
      await fetch(`${this.baseUrl}/email-management/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.testUser.token}`
        },
        body: JSON.stringify(category)
      });
    }
  }

  /**
   * Clean up test data
   */
  async cleanupTestData(): Promise<void> {
    if (!this.testUser) return;

    // Clean up test categories
    const categoriesResponse = await fetch(`${this.baseUrl}/email-management/categories`, {
      headers: {
        'Authorization': `Bearer ${this.testUser.token}`
      }
    });

    if (categoriesResponse.ok) {
      const categories = await categoriesResponse.json();
      for (const category of categories.data || []) {
        if (category.name.startsWith('test_')) {
          await fetch(`${this.baseUrl}/email-management/categories/${category.name}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${this.testUser.token}`
            }
          });
        }
      }
    }

    // Clean up test user
    await fetch(`${this.baseUrl}/users/${this.testUser.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.testUser.token}`
      }
    });
  }

  /**
   * Get the current test user
   */
  getTestUser(): TestUser | null {
    return this.testUser;
  }
}

// Export a singleton instance
export const realApiHelper = new RealApiTestHelper(); 