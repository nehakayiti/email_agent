import { spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';
import { exec } from 'child_process';
import path from 'path';

const execAsync = promisify(exec);

export interface TestServerConfig {
  port: number;
  databaseUrl: string;
  baseUrl: string;
}

export class BackendTestServer {
  private process: ChildProcess | null = null;
  private config: TestServerConfig;

  constructor(config: TestServerConfig) {
    this.config = config;
  }

  async start(): Promise<void> {
    console.log('🚀 Starting backend test server...');
    
    // Set environment variables for the test server
    const env = {
      ...process.env,
      DATABASE_URL: this.config.databaseUrl,
      PORT: this.config.port.toString(),
      CORS_ORIGINS: 'http://localhost:3000,http://localhost:3001',
      ENVIRONMENT: 'test',
      TEST_MODE: 'true',
    };

    // Start the backend server using uvicorn with virtual environment
    const backendPath = path.join(process.cwd(), '../backend');
    const venvPath = path.join(process.cwd(), '../venv');
    
    // Use the virtual environment's Python and uvicorn
    const pythonPath = path.join(venvPath, 'bin', 'python');
    const uvicornPath = path.join(venvPath, 'bin', 'uvicorn');
    
    this.process = spawn(pythonPath, [
      uvicornPath,
      'app.main:app',
      '--host', '0.0.0.0',
      '--port', this.config.port.toString(),
      '--reload',
      '--env-file', '.env.test'
    ], {
      cwd: backendPath,
      env,
      stdio: 'pipe'
    });

    // Wait for server to start
    await this.waitForServer();
    console.log(`✅ Backend test server started on ${this.config.baseUrl}`);
  }

  async stop(): Promise<void> {
    if (this.process) {
      console.log('🛑 Stopping backend test server...');
      this.process.kill('SIGTERM');
      await new Promise(resolve => {
        if (this.process) {
          this.process.on('exit', resolve);
        } else {
          resolve(undefined);
        }
      });
      this.process = null;
      console.log('✅ Backend test server stopped');
    }
  }

  private async waitForServer(): Promise<void> {
    const maxAttempts = 60; // Increased from 30 to 60
    const delay = 1000;

    for (let i = 0; i < maxAttempts; i++) {
      try {
        console.log(`Attempting to connect to ${this.config.baseUrl}/health (attempt ${i + 1}/${maxAttempts})`);
        const response = await fetch(`${this.config.baseUrl}/health`);
        if (response.ok) {
          console.log('✅ Health check successful');
          return;
        }
      } catch (error) {
        console.log(`❌ Health check failed (attempt ${i + 1}/${maxAttempts}):`, error);
      }
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    throw new Error(`Backend test server failed to start after ${maxAttempts} attempts`);
  }

  getBaseUrl(): string {
    return this.config.baseUrl;
  }
}

// Default test server configuration - updated to match .env.test
export const defaultTestConfig: TestServerConfig = {
  port: 5001, // Changed from 8001 to 5001 to match .env.test
  databaseUrl: 'postgresql://postgres:postgres@localhost:5432/email_agent_test_db',
  baseUrl: 'http://localhost:5001'
};

// Global test server instance
let globalTestServer: BackendTestServer | null = null;

export async function startTestServer(config: TestServerConfig = defaultTestConfig): Promise<BackendTestServer> {
  if (!globalTestServer) {
    globalTestServer = new BackendTestServer(config);
    await globalTestServer.start();
  }
  return globalTestServer;
}

export async function stopTestServer(): Promise<void> {
  if (globalTestServer) {
    await globalTestServer.stop();
    globalTestServer = null;
  }
}

// Helper function to configure frontend for test server
export function configureFrontendForTestServer(baseUrl: string): void {
  // Set environment variables for the frontend
  process.env.NEXT_PUBLIC_API_URL = baseUrl;
  process.env.NEXT_PUBLIC_TEST_MODE = 'false'; // Disable test mode to use real API
  
  // Clear any cached API configurations
  if (typeof window !== 'undefined') {
    // Clear localStorage if in browser environment
    localStorage.removeItem('auth_token');
  }
}

// Helper function to create test user and get auth token
export async function createTestUser(baseUrl: string): Promise<{ token: string; user: any }> {
  const testEmail = `test-${Date.now()}@example.com`;
  
  // Create a test user (this would need to be implemented in the backend)
  const createUserResponse = await fetch(`${baseUrl}/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: testEmail,
      name: 'Test User',
      credentials: {
        access_token: 'test_token',
        refresh_token: 'test_refresh_token'
      }
    }),
  });

  if (!createUserResponse.ok) {
    throw new Error(`Failed to create test user: ${createUserResponse.statusText}`);
  }

  const user = await createUserResponse.json();
  
  // For testing, we'll use a simple token
  const token = `test_token_${Date.now()}`;
  
  return { token, user };
} 