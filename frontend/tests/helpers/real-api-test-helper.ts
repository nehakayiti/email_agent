import { Page } from '@playwright/test';

export interface TestUser {
  id: string;
  email: string;
  token: string;
}

export class RealApiTestHelper {
  private static instance: RealApiTestHelper;
  private baseUrl: string = 'http://localhost:5001'; // Add baseUrl property
  private testUser: any = null;
  private authToken: string = '';

  private constructor() {}

  static getInstance(): RealApiTestHelper {
    if (!RealApiTestHelper.instance) {
      RealApiTestHelper.instance = new RealApiTestHelper();
    }
    return RealApiTestHelper.instance;
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

    // Set the auth token in localStorage for the current session
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('auth_token', token);
    }

    return this.testUser;
  }

  /**
   * Setup page for testing with real API
   */
  async setupPage(page: Page, user?: TestUser): Promise<void> {
    const testUser = user || this.testUser || await this.createTestUser();
    
    // Set the API URL to point to the test backend server
    await page.addInitScript((token: string) => {
      // Override the API URL to use the test server
      window.localStorage.setItem('api_url', 'http://localhost:5001');
      window.localStorage.setItem('test_mode', 'true');
      
      // Set test mode environment variable
      (window as any).process = { 
        env: { 
          NEXT_PUBLIC_API_URL: 'http://localhost:5001',
          NEXT_PUBLIC_TEST_MODE: 'true'
        } 
      };
      
      // Set the auth token for testing
      window.localStorage.setItem('auth_token', token);
    }, testUser.token);
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
   * Clean up test data after tests
   */
  async cleanupTestData(): Promise<void> {
    if (!this.testUser) {
      return;
    }

    try {
      // Clean up test categories
      const categoriesResponse = await fetch(`${this.baseUrl}/email-management/categories`, {
        headers: {
          'Authorization': `Bearer ${this.testUser.token}`
        }
      });

      if (categoriesResponse.ok) {
        const categories = await categoriesResponse.json();
        // Delete any test categories created during the test
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
    } catch (error) {
      // Silently ignore cleanup errors - backend might not be running
      console.log('Cleanup warning: Backend not available for cleanup');
    }

    // Reset test user
    this.testUser = null;
  }

  /**
   * Get the current test user
   */
  getTestUser(): TestUser | null {
    return this.testUser;
  }
}

// Export a singleton instance
export const realApiHelper = RealApiTestHelper.getInstance(); 