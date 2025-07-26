# Frontend Testing with Real Backend API

This directory contains tests that use the **real backend API** instead of mocks, providing more reliable and realistic testing.

## 🎯 Why Real API Testing?

### Problems with Mocking:
- **Brittle tests** - break when API structure changes
- **False confidence** - tests pass but real app fails
- **Maintenance burden** - mocks need constant updates
- **Missing edge cases** - real API behavior differs from mocks

### Benefits of Real API Testing:
- **Realistic testing** - tests actual API behavior
- **Automatic validation** - API changes break tests appropriately
- **Less maintenance** - no mock updates needed
- **Better coverage** - tests real data flows and edge cases

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Test Database │
│   Tests         │───▶│   Test Server   │───▶│   (PostgreSQL)  │
│   (Playwright)  │    │   (FastAPI)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
tests/
├── helpers/
│   └── real-api-test-helper.ts    # Helper utilities for real API testing
├── test-server-setup.ts           # Backend test server management
├── global-setup.ts                # Global test setup
├── global-teardown.ts             # Global test cleanup
├── category-management-simple.spec.ts  # Example test using real API
├── category-management-real-api.spec.ts # More detailed real API test
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have:
- Backend test database running (`email_agent_test_db`)
- Backend dependencies installed
- Frontend dependencies installed

### 2. Run Tests

```bash
# Run tests with real API (headless)
npm run test:real-api

# Run tests with real API (headed - see browser)
npm run test:real-api:headed

# Run tests with real API (debug mode)
npm run test:real-api:debug
```

### 3. Test Configuration

The tests use `playwright.config.test-server.ts` which:
- Starts the backend test server on port 8001
- Starts the frontend dev server on port 3001
- Configures global setup/teardown for server management

## 🛠️ Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';
import { realApiHelper } from './helpers/real-api-test-helper';

test.describe('My Feature with Real API', () => {
  test.beforeEach(async ({ page }) => {
    // Setup page with real API
    await realApiHelper.setupPage(page);
  });

  test.afterEach(async () => {
    // Clean up test data
    await realApiHelper.cleanupTestData();
  });

  test('should do something with real API', async ({ page }) => {
    // Navigate to page
    await realApiHelper.navigateToPage(page, '/my-page');
    
    // Wait for page to load
    await realApiHelper.waitForPageLoad(page, 'Expected Title');
    
    // Your test assertions here
    await expect(page.locator('h1')).toContainText('Expected Title');
  });
});
```

### Helper Methods

The `realApiHelper` provides:

- `setupPage(page)` - Configure page for real API testing
- `navigateToPage(page, path)` - Navigate and wait for load
- `waitForPageLoad(page, title?)` - Wait for page to load properly
- `createTestUser()` - Create a test user with auth token
- `cleanupTestData()` - Clean up test data after tests

## 🔧 Test Server Management

### Automatic Server Management

The test framework automatically:
1. **Starts** backend test server before all tests
2. **Configures** frontend to use test server
3. **Stops** backend test server after all tests

### Manual Server Control

```typescript
import { startTestServer, stopTestServer } from './test-server-setup';

// Start server manually
const server = await startTestServer();

// Use server
const baseUrl = server.getBaseUrl();

// Stop server manually
await stopTestServer();
```

## 🗄️ Test Database

### Database Setup

The backend test server uses:
- **Database**: `email_agent_test_db` (separate from development)
- **Migrations**: Automatic Alembic migrations
- **Seeding**: System categories and test data
- **Isolation**: Transaction rollbacks between tests

### Test Data

The test database includes:
- **System categories**: Important, Work, Newsletter
- **Test users**: Created per test session
- **Clean isolation**: Data cleaned between tests

## 🔍 Debugging

### View Test Server Logs

```bash
# Run tests with verbose output
npm run test:real-api:debug
```

### Check Server Status

```bash
# Test server health endpoint
curl http://localhost:8001/health
```

### Database Inspection

```bash
# Connect to test database
docker exec -i postgres_db psql -U postgres -d email_agent_test_db
```

## 🚨 Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 8001 is available
   - Verify backend dependencies are installed
   - Check test database is running

2. **Tests fail with 404**
   - Verify frontend routes exist
   - Check API endpoints are working
   - Ensure authentication is set up

3. **Database connection issues**
   - Verify test database exists
   - Check database credentials
   - Ensure migrations have run

### Debug Commands

```bash
# Check if test database exists
docker exec -i postgres_db psql -U postgres -l | grep test

# Check backend logs
tail -f backend/logs/email_agent.log

# Check frontend logs
npm run dev 2>&1 | grep -i error
```

## 📚 Migration from Mock Tests

### Step 1: Identify Mock Dependencies

Find tests that use:
- `NEXT_PUBLIC_TEST_MODE = 'true'`
- Mock API responses
- `fetchWithAuth` with test mode

### Step 2: Replace with Real API

```typescript
// OLD: Mock-based test
await page.addInitScript(() => {
  process.env.NEXT_PUBLIC_TEST_MODE = 'true';
});

// NEW: Real API test
await realApiHelper.setupPage(page);
```

### Step 3: Update Assertions

```typescript
// OLD: Mock data assertions
await expect(page.locator('text=Mock Category')).toBeVisible();

// NEW: Real data assertions
await expect(page.locator('text=Important')).toBeVisible();
```

## 🎯 Best Practices

1. **Use real data** - Don't mock responses, use actual API
2. **Clean up data** - Always clean up test data in `afterEach`
3. **Test isolation** - Each test should be independent
4. **Realistic scenarios** - Test actual user workflows
5. **Error handling** - Test both success and error cases

## 🔄 Continuous Integration

The real API tests can be run in CI by:
1. Starting the test database
2. Running backend migrations
3. Starting the test server
4. Running frontend tests

This ensures tests work in the same environment as production. 