import LoginButton from '@/components/login-button';

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <h1 className="text-3xl font-bold mb-6">Email Agent</h1>
        <p className="text-gray-600 mb-8">Sign in with your Google account to manage your emails</p>
        <LoginButton />
      </div>
    </main>
  );
}
