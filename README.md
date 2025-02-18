# Email Agent

An intelligent email management system that helps users organize, prioritize, and manage their emails effectively using AI-powered categorization and importance scoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Overview

Email Agent is a modern web application that integrates with Gmail to provide smart email management features. It uses machine learning to categorize emails, assign importance scores, and help users focus on what matters most.

### Key Features

- 🤖 AI-powered email categorization
- 📊 Smart importance scoring
- 🔄 Real-time Gmail synchronization
- 📱 Responsive web interface
- 🔐 Secure OAuth2 authentication
- 📋 Email organization and filtering

## 🏗 Architecture

The project consists of two main components:

### Backend (FastAPI)
- RESTful API service
- Gmail API integration
- Machine learning models for email analysis
- PostgreSQL database for email storage
- JWT authentication

### Frontend (Next.js)
- Modern React-based UI
- Server-side rendering
- Responsive design
- Real-time updates
- OAuth2 integration

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js 18.x or later
- PostgreSQL 14 or later
- Google Cloud Platform account with Gmail API enabled

### Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd email-agent
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   cp .env.example .env  # Configure your environment variables
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local  # Configure your environment variables
   ```

4. Start the services:
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
email-agent/
├── backend/                 # FastAPI backend service
│   ├── app/                # Application code
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend application
│   ├── src/               # Source code
│   └── package.json       # Node.js dependencies
├── docs/                   # Documentation
└── docker/                 # Docker configuration
```

## 🛠 Development

### Backend Development

```bash
cd backend
pytest  # Run tests
black .  # Format code
flake8  # Lint code
```

### Frontend Development

```bash
cd frontend
npm run lint  # Lint code
npm run test  # Run tests
npm run build  # Build for production
```

## 📚 Documentation

- [Backend API Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Development Guide](docs/development.md)
- [API Reference](docs/api-reference.md)

## 🔒 Security

- OAuth2 authentication with Google
- JWT for API authentication
- HTTPS enforcement
- Rate limiting
- Input validation
- XSS protection
- CSRF protection

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [Gmail API](https://developers.google.com/gmail/api) for email integration
- All our contributors and supporters

## 📞 Support

- Create an issue for bug reports or feature requests
- Check our [FAQ](docs/faq.md)
- Join our [Discord community](https://discord.gg/your-server)

## 🗺 Roadmap

- [ ] Advanced email analytics
- [ ] Custom categorization rules
- [ ] Email templates
- [ ] Mobile application
- [ ] Calendar integration
- [ ] Team collaboration features

## 🌟 Core Team

- [Your Name](https://github.com/yourusername) - Project Lead
- [Contributor 1](https://github.com/contributor1) - Backend Developer
- [Contributor 2](https://github.com/contributor2) - Frontend Developer