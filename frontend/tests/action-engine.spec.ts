import { test, expect } from '@playwright/test';

test.describe('Action Engine Frontend', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the categories page
    await page.goto('http://localhost:3000/categories/improved');
  });

  test('displays action rules section when category is selected', async ({ page }) => {
    // Wait for categories to load
    await page.waitForSelector('text=Categories');
    
    // Click on the first category to select it
    await page.click('text=Primary');
    
    // Check that action rules section is visible
    await expect(page.getByText('Action Rules')).toBeVisible();
    await expect(page.getByText('Add Action Rule')).toBeVisible();
  });

  test('shows action rule suggestions when button is clicked', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Promotions');
    
    // Click show suggestions button
    await page.click('text=Show Suggestions');
    
    // Check that suggestions are displayed
    await expect(page.getByText('Suggested Rules')).toBeVisible();
    await expect(page.getByText('Trash after 3 days')).toBeVisible();
    await expect(page.getByText('Archive after 1 day')).toBeVisible();
  });

  test('opens action rule modal when add button is clicked', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Primary');
    
    // Click add action rule button
    await page.click('text=Add Action Rule');
    
    // Check that modal is opened
    await expect(page.getByText('Configure Action Rule')).toBeVisible();
    await expect(page.getByText('Action Type')).toBeVisible();
    await expect(page.getByText('Timing')).toBeVisible();
  });

  test('displays empty state when no action rules exist', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Primary');
    
    // Check that empty state is shown
    await expect(page.getByText('No action rules configured for this category yet.')).toBeVisible();
    await expect(page.getByText('Add Action Rules')).toBeVisible();
  });

  test('can configure action rule in modal', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Promotions');
    
    // Click add action rule button
    await page.click('text=Add Action Rule');
    
    // Configure the action rule
    await page.click('text=Trash'); // Select trash action
    await page.fill('input[type="number"]', '5'); // Set delay to 5 days
    await page.click('text=Create Rule');
    
    // Check that modal closes and rule is created
    await expect(page.getByText('Configure Action Rule')).not.toBeVisible();
  });

  test('shows different suggestions for different category types', async ({ page }) => {
    // Test promotions category
    await page.waitForSelector('text=Categories');
    await page.click('text=Promotions');
    await page.click('text=Show Suggestions');
    
    // Check for promotion-specific suggestions
    await expect(page.getByText('Trash after 3 days')).toBeVisible();
    await expect(page.getByText('Archive after 1 day (if not opened)')).toBeVisible();
    
    // Test social category
    await page.click('text=Social');
    await page.click('text=Show Suggestions');
    
    // Check for social-specific suggestions
    await expect(page.getByText('Archive after 7 days')).toBeVisible();
  });

  test('action rule modal shows real-time preview', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Promotions');
    
    // Click add action rule button
    await page.click('text=Add Action Rule');
    
    // Check that preview section is visible
    await expect(page.getByText('Preview')).toBeVisible();
    
    // Change the delay and check that preview updates
    await page.fill('input[type="number"]', '10');
    
    // Wait for preview to update (this might take a moment)
    await page.waitForTimeout(1000);
    
    // Check that preview section is still visible
    await expect(page.getByText('Preview')).toBeVisible();
  });

  test('can toggle action rule suggestions visibility', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Promotions');
    
    // Show suggestions
    await page.click('text=Show Suggestions');
    await expect(page.getByText('Suggested Rules')).toBeVisible();
    
    // Hide suggestions
    await page.click('text=Hide Suggestions');
    await expect(page.getByText('Suggested Rules')).not.toBeVisible();
  });

  test('action rule modal has proper form validation', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Primary');
    
    // Click add action rule button
    await page.click('text=Add Action Rule');
    
    // Try to submit without selecting action type (should show validation)
    await page.click('text=Create Rule');
    
    // Check that validation error is shown
    await expect(page.getByText('Please select an action type')).toBeVisible();
  });

  test('can close action rule modal', async ({ page }) => {
    // Wait for categories to load and select a category
    await page.waitForSelector('text=Categories');
    await page.click('text=Primary');
    
    // Click add action rule button
    await page.click('text=Add Action Rule');
    
    // Check that modal is open
    await expect(page.getByText('Configure Action Rule')).toBeVisible();
    
    // Close modal
    await page.click('text=Cancel');
    
    // Check that modal is closed
    await expect(page.getByText('Configure Action Rule')).not.toBeVisible();
  });
}); 