import { stopTestServer } from './test-server-setup';

async function globalTeardown() {
  console.log('🌍 Global teardown: Stopping backend test server...');
  
  try {
    // Stop the backend test server
    await stopTestServer();
    
    console.log('✅ Global teardown: Backend test server stopped successfully');
  } catch (error) {
    console.error('❌ Global teardown: Failed to stop backend test server:', error);
    // Don't throw here as we want to clean up even if there's an error
  }
}

export default globalTeardown; 