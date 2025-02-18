# Email Agent Frontend

A modern web interface for the Email Agent application, built with Next.js 14, TypeScript, and Tailwind CSS.

## Overview

Email Agent is an intelligent email management system that helps users organize and prioritize their emails. The frontend provides a clean, responsive interface for:

- Viewing and managing emails
- Categorized email organization
- Importance-based email prioritization
- Detailed email insights

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: OAuth 2.0 with Google
- **State Management**: React Hooks
- **API Integration**: REST API with JWT authentication

## Features

- 🔐 Secure Google OAuth authentication
- 📧 Email list view with sorting and filtering
- 📝 Detailed email view with importance scoring
- 🎯 Email categorization
- 🔄 Real-time email synchronization
- 📱 Responsive design for all devices

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn
- Backend API running (see main project README)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd email-agent/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your configuration:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_AUTH_CALLBACK_URL=http://localhost:3000/auth/callback
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app router pages
│   ├── components/          # Reusable React components
│   ├── lib/                 # Utility functions and API clients
│   └── types/              # TypeScript type definitions
├── public/                  # Static assets
└── tailwind.config.js      # Tailwind CSS configuration
```

## Key Components

- `app/page.tsx`: Main landing page with login
- `app/emails/page.tsx`: Email list view
- `app/emails/[id]/page.tsx`: Individual email view
- `components/email-detail.tsx`: Email detail component
- `lib/api.ts`: API client utilities
- `lib/auth.ts`: Authentication utilities

## Development

### Code Style

- Follow TypeScript best practices
- Use functional components with hooks
- Implement proper error handling
- Write descriptive component and function names
- Use Tailwind CSS for styling

### Testing

```bash
npm run test
# or
yarn test
```

### Building for Production

```bash
npm run build
# or
yarn build
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Next.js team for the amazing framework
- Vercel for deployment platform
- Google OAuth for authentication

## Related Projects

- [Email Agent Backend](../backend/README.md)
- [Email Agent Documentation](../docs/README.md)
