# 🤖 EETL AI Platform - Talk-to-Data ETL Solution

A comprehensive Generative AI-powered web-based ETL platform that allows users to interact with structured data using natural language for cleaning, transformation, querying, and summarization.

## 🚀 Features

### Core Capabilities
- **Natural Language Data Interaction**: Chat with your data using plain English
- **AI-Powered Data Cleaning**: Automated data quality assessment and cleaning suggestions
- **Smart Query Generation**: Convert natural language to SQL and Python code
- **Intelligent Insights**: Automated data summarization and pattern detection
- **Multi-Format Support**: CSV, Excel, JSON, and database connections
- **Real-time Visualization**: Interactive charts, tables, and reports

### AI Integration
- **OpenRouter API**: Powered by DeepSeek Chat model for advanced reasoning
- **RAG Implementation**: Vector database for grounded, contextual responses
- **Code Generation**: Automatic SQL and Python code generation
- **Data Quality AI**: Intelligent data profiling and cleaning recommendations

### User Experience
- **Conversational Interface**: Chat-based data exploration
- **Role-Based Access**: Business analysts, developers, and public access levels
- **Export Capabilities**: CSV, PDF, PowerPoint report generation
- **Scheduled Reporting**: Automated insights delivery
- **Mobile Responsive**: Works seamlessly across all devices

## 🏗️ Architecture

### Backend (Django REST API)
- **Data Ingestion Module**: Multi-source data connectivity
- **AI Engine**: OpenRouter integration with RAG capabilities
- **Query Processor**: Natural language to code conversion
- **Visualization Engine**: Chart and report generation
- **Authentication**: JWT-based security with role management

### Frontend Options
1. **React Web Application**: Full-featured dashboard and chat interface
2. **Hugging Face Spaces**: Two interactive demos showcasing core functionality

### Technology Stack
- **Backend**: Django 4.2+, Django REST Framework, PostgreSQL, ChromaDB
- **Frontend**: React 18+, TypeScript, Vite, TailwindCSS
- **AI**: OpenRouter API (DeepSeek Chat), Vector embeddings
- **Deployment**: Docker, GitHub Actions CI/CD
- **Demos**: Gradio for Hugging Face Spaces

## 📁 Project Structure

```
eetl-ai-platform/
├── backend/                    # Django REST API
│   ├── core/                  # Core Django settings
│   ├── apps/
│   │   ├── authentication/    # User management & JWT
│   │   ├── data_ingestion/    # File upload & DB connections
│   │   ├── ai_engine/         # AI processing & RAG
│   │   ├── query_processor/   # Natural language queries
│   │   └── visualization/     # Charts & reports
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Main application pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API integration
│   │   └── utils/            # Helper functions
│   ├── package.json
│   └── Dockerfile
├── huggingface_demos/         # HF Spaces demos
│   ├── data_cleaning_demo/    # Data cleaning showcase
│   └── query_interface_demo/  # Natural language querying
├── docker-compose.yml         # Multi-container setup
├── .github/workflows/         # CI/CD pipelines
└── docs/                      # Comprehensive documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose

### Environment Setup
1. Clone the repository
2. Set up environment variables (see `.env.example`)
3. Run with Docker Compose: `docker-compose up -d`
4. Access the application at `http://localhost:3000`

## 🔑 API Configuration

The platform uses OpenRouter API with DeepSeek Chat model for AI capabilities. Configure your API key in the environment variables.

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [User Manual](./docs/user-guide.md)
- [Developer Guide](./docs/development.md)

## 🧪 Testing

- Backend: `python manage.py test`
- Frontend: `npm test`
- Integration: `docker-compose -f docker-compose.test.yml up`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

- **adimiw** - *Initial work* - [GitHub](https://github.com/adimiw)

## 🙏 Acknowledgments

- OpenRouter for AI API access
- Hugging Face for demo hosting
- Django and React communities

---

**Built with ❤️ for the data community**
