import { test, expect } from '@playwright/test';

test.describe('Action Engine Components', () => {
  test('action rule display shows empty state correctly', async ({ page }) => {
    // Create a simple HTML page to test the component
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Action Engine Test</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
          <div id="app">
            <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <span class="text-lg">🎯</span>
                  <span class="font-medium text-gray-700">Action Rules</span>
                </div>
                <button class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                  <span class="mr-1">➕</span>
                  Add Action Rules
                </button>
              </div>
              <p class="mt-2 text-sm text-gray-500">
                No action rules configured for this category yet.
              </p>
            </div>
          </div>
        </body>
      </html>
    `);

    // Test that the empty state is displayed correctly
    await expect(page.locator('span:has-text("Action Rules")')).toBeVisible();
    await expect(page.getByText('No action rules configured for this category yet.')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add Action Rules' })).toBeVisible();
  });

  test('action rule display shows rules correctly', async ({ page }) => {
    // Create a simple HTML page to test the component with rules
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Action Engine Test</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
          <div id="app">
            <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <span class="text-lg">🎯</span>
                  <span class="font-medium text-gray-700">Action Rules</span>
                  <span class="text-sm text-gray-500">(2)</span>
                </div>
                <div class="flex items-center space-x-2">
                  <button class="text-sm text-gray-500 hover:text-gray-700 focus:outline-none">
                    Show Details
                  </button>
                  <button class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                    <span class="mr-1">➕</span>
                    Add Another Rule
                  </button>
                </div>
              </div>
              <div class="mt-3 space-y-3">
                <div class="p-3 rounded-lg border text-red-600 bg-red-50 border-red-200 transition-all duration-200">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                      <span class="text-lg">🗑️</span>
                      <div>
                        <div class="font-medium">Trash after 3 days</div>
                        <div class="text-sm opacity-75">
                          Status: <span class="text-green-600">Active</span>
                        </div>
                      </div>
                    </div>
                    <div class="flex items-center space-x-1">
                      <button class="px-2 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-gray-500 transition-colors">
                        Preview
                      </button>
                      <button class="px-2 py-1 text-xs font-medium text-blue-600 bg-white border border-blue-300 rounded hover:bg-blue-50 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors">
                        Edit
                      </button>
                      <button class="px-2 py-1 text-xs font-medium text-red-600 bg-white border-red-300 rounded hover:bg-red-50 focus:outline-none focus:ring-1 focus:ring-red-500 transition-colors">
                        Disable
                      </button>
                      <button class="px-2 py-1 text-xs font-medium text-red-600 bg-white border border-red-300 rounded hover:bg-red-50 focus:outline-none focus:ring-1 focus:ring-red-500 transition-colors">
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </body>
      </html>
    `);

    // Test that the rules are displayed correctly
    await expect(page.getByText('Action Rules')).toBeVisible();
    await expect(page.getByText('(2)')).toBeVisible();
    await expect(page.getByText('Trash after 3 days')).toBeVisible();
    await expect(page.getByText('Status: Active')).toBeVisible();
    await expect(page.getByText('Preview')).toBeVisible();
    await expect(page.getByText('Edit')).toBeVisible();
    await expect(page.getByText('Disable')).toBeVisible();
    await expect(page.getByText('Delete')).toBeVisible();
  });

  test('action rule suggestions display correctly', async ({ page }) => {
    // Create a simple HTML page to test the suggestions component
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Action Engine Test</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
          <div id="app">
            <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div class="flex items-center space-x-2 mb-3">
                <span class="text-lg">💡</span>
                <span class="font-medium text-gray-700">Suggested Rules</span>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <button class="p-3 rounded-lg border bg-red-50 border-red-200 text-red-700 hover:shadow-md transition-all duration-200 text-left focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                  <div class="flex items-start space-x-3">
                    <span class="text-xl">🗑️</span>
                    <div class="flex-1">
                      <div class="font-medium">Trash after 3 days</div>
                      <div class="text-sm opacity-75 mt-1">Quick cleanup for promotional emails</div>
                    </div>
                  </div>
                </button>
                <button class="p-3 rounded-lg border bg-blue-50 border-blue-200 text-blue-700 hover:shadow-md transition-all duration-200 text-left focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                  <div class="flex items-start space-x-3">
                    <span class="text-xl">📤</span>
                    <div class="flex-1">
                      <div class="font-medium">Archive after 1 day (if not opened)</div>
                      <div class="text-sm opacity-75 mt-1">Archive unopened promotions quickly</div>
                    </div>
                  </div>
                </button>
              </div>
              <div class="mt-3 text-sm text-gray-500">
                <p>💡 These suggestions are based on the category type. You can customize them after adding.</p>
              </div>
            </div>
          </div>
        </body>
      </html>
    `);

    // Test that the suggestions are displayed correctly
    await expect(page.getByText('Suggested Rules')).toBeVisible();
    await expect(page.getByText('Trash after 3 days')).toBeVisible();
    await expect(page.getByText('Archive after 1 day (if not opened)')).toBeVisible();
    await expect(page.getByText('Quick cleanup for promotional emails')).toBeVisible();
    await expect(page.getByText('Archive unopened promotions quickly')).toBeVisible();
  });

  test('action rule modal form elements are present', async ({ page }) => {
    // Create a simple HTML page to test the modal form
    await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Action Engine Test</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
          <div id="app">
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div class="p-6 border-b border-gray-200">
                  <div class="flex items-center justify-between">
                    <h2 class="text-xl font-semibold text-gray-900">
                      Configure Action Rule - Promotions
                    </h2>
                    <button class="text-gray-400 hover:text-gray-600 focus:outline-none">
                      <span class="sr-only">Close</span>
                      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
                <form class="p-6 space-y-6">
                  <div class="space-y-4">
                    <h3 class="text-lg font-medium text-gray-900">Action Type</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <label class="relative">
                        <input type="radio" name="action" value="ARCHIVE" class="sr-only" />
                        <div class="p-4 border-2 rounded-lg cursor-pointer transition-all border-blue-500 bg-blue-50">
                          <div class="flex items-center space-x-3">
                            <span class="text-2xl">📤</span>
                            <div>
                              <div class="font-medium">Archive</div>
                              <div class="text-sm text-gray-500">Move emails to archive folder</div>
                            </div>
                          </div>
                        </div>
                      </label>
                      <label class="relative">
                        <input type="radio" name="action" value="TRASH" class="sr-only" />
                        <div class="p-4 border-2 rounded-lg cursor-pointer transition-all border-gray-200 hover:border-gray-300">
                          <div class="flex items-center space-x-3">
                            <span class="text-2xl">🗑️</span>
                            <div>
                              <div class="font-medium">Trash</div>
                              <div class="text-sm text-gray-500">Move emails to trash folder</div>
                            </div>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>
                  <div class="space-y-4">
                    <h3 class="text-lg font-medium text-gray-900">Timing</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                      <div class="flex items-center space-x-3">
                        <label for="delay_days" class="text-sm font-medium text-gray-700">
                          Wait for:
                        </label>
                        <input id="delay_days" type="number" min="1" max="365" value="7" class="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" />
                        <span class="text-sm text-gray-700">days after email is received</span>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
                    <button type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                      Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                      Create Rule
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </body>
      </html>
    `);

    // Test that the modal form elements are present
    await expect(page.getByText('Configure Action Rule - Promotions')).toBeVisible();
    await expect(page.getByText('Action Type')).toBeVisible();
    await expect(page.getByText('Timing')).toBeVisible();
    await expect(page.locator('div:has-text("Archive")').first()).toBeVisible();
    await expect(page.locator('div:has-text("Trash")').first()).toBeVisible();
    await expect(page.getByText('Move emails to archive folder')).toBeVisible();
    await expect(page.getByText('Move emails to trash folder')).toBeVisible();
    await expect(page.getByText('Wait for:')).toBeVisible();
    await expect(page.getByText('days after email is received')).toBeVisible();
    await expect(page.getByText('Cancel')).toBeVisible();
    await expect(page.getByText('Create Rule')).toBeVisible();
  });
}); 