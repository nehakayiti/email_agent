import { startTestServer } from './test-server-setup';

async function globalSetup() {
  console.log('🌍 Global setup: Starting backend test server...');
  
  try {
    // Start the backend test server
    const testServer = await startTestServer();
    
    // Store the server info in a global variable that tests can access
    (global as any).__TEST_SERVER__ = testServer;
    
    console.log('✅ Global setup: Backend test server started successfully');
  } catch (error) {
    console.error('❌ Global setup: Failed to start backend test server:', error);
    throw error;
  }
}

export default globalSetup; 