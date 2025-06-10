# 🚀 EETL AI Platform - Deployment Guide

This guide covers different deployment options for the EETL AI Platform.

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- OpenRouter API key
- PostgreSQL database (for production)
- Redis instance (for production)

## 🔧 Environment Setup

1. **Clone the repository:**
```bash
git clone https://github.com/adimiw/eetl-ai-platform.git
cd eetl-ai-platform
```

2. **Create environment file:**
```bash
cp .env.example .env
```

3. **Configure environment variables:**
Edit `.env` file with your settings:
```env
# Required
OPENROUTER_API_KEY=your-openrouter-api-key
SECRET_KEY=your-secret-key
DB_PASSWORD=your-db-password

# Optional (defaults provided)
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

## 🐳 Docker Deployment (Recommended)

### Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/

### Production Environment

```bash
# Build and start production services
docker-compose --profile production up -d

# Or use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 Manual Deployment

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run migrations:**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

4. **Create superuser:**
```bash
python manage.py createsuperuser
```

5. **Start development server:**
```bash
python manage.py runserver 0.0.0.0:8000
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Build for production:**
```bash
npm run build
```

3. **Start development server:**
```bash
npm run dev
```

## ☁️ Cloud Deployment

### AWS Deployment

1. **Using AWS ECS with Fargate:**
```bash
# Build and push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t eetl-backend ./backend
docker tag eetl-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/eetl-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/eetl-backend:latest

docker build -t eetl-frontend ./frontend
docker tag eetl-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/eetl-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/eetl-frontend:latest
```

2. **Deploy using ECS CLI or CloudFormation templates**

### Google Cloud Platform

1. **Using Cloud Run:**
```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT-ID/eetl-backend ./backend
gcloud run deploy eetl-backend --image gcr.io/PROJECT-ID/eetl-backend --platform managed

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/eetl-frontend ./frontend
gcloud run deploy eetl-frontend --image gcr.io/PROJECT-ID/eetl-frontend --platform managed
```

### Digital Ocean

1. **Using App Platform:**
```yaml
# app.yaml
name: eetl-ai-platform
services:
- name: backend
  source_dir: backend
  github:
    repo: adimiw/eetl-ai-platform
    branch: main
  run_command: gunicorn --bind 0.0.0.0:8000 core.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  
- name: frontend
  source_dir: frontend
  github:
    repo: adimiw/eetl-ai-platform
    branch: main
  build_command: npm run build
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
```

## 🗄️ Database Setup

### PostgreSQL (Production)

1. **Create database:**
```sql
CREATE DATABASE eetl_db;
CREATE USER eetl_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE eetl_db TO eetl_user;
```

2. **Install pgvector extension:**
```sql
CREATE EXTENSION vector;
```

### Redis Setup

1. **Install Redis:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt with Nginx

1. **Install Certbot:**
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Obtain SSL certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

3. **Auto-renewal:**
```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### Application Monitoring

1. **Sentry Integration:**
```python
# In settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

2. **Health Checks:**
```bash
# Backend health check
curl http://localhost:8000/api/health/

# Frontend health check
curl http://localhost:3000/health
```

### Log Management

1. **Centralized logging with ELK Stack:**
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  
  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
```

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows for:

- **Continuous Integration:** Automated testing and security scanning
- **Continuous Deployment:** Automated deployment to staging and production
- **Container Registry:** Automated image building and pushing

### Manual Deployment Commands

```bash
# Deploy to staging
git push origin develop

# Deploy to production
git push origin main

# Manual deployment
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Error:**
```bash
# Check database status
docker-compose ps postgres
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

2. **Redis Connection Error:**
```bash
# Check Redis status
docker-compose ps redis
docker-compose logs redis

# Test Redis connection
redis-cli ping
```

3. **Frontend Build Issues:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

4. **Backend Migration Issues:**
```bash
# Reset migrations
cd backend
python manage.py migrate --fake-initial
python manage.py migrate
```

### Performance Optimization

1. **Database Optimization:**
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_data_source_user ON data_sources(user_id);
CREATE INDEX idx_conversation_user ON ai_conversations(user_id);
```

2. **Redis Caching:**
```python
# Cache frequently accessed data
from django.core.cache import cache

def get_user_data(user_id):
    cache_key = f"user_data_{user_id}"
    data = cache.get(cache_key)
    if not data:
        data = expensive_database_query(user_id)
        cache.set(cache_key, data, 300)  # 5 minutes
    return data
```

3. **Frontend Optimization:**
```bash
# Analyze bundle size
npm run build
npx webpack-bundle-analyzer build/static/js/*.js
```

## 📞 Support

For deployment issues or questions:

- **GitHub Issues:** [Create an issue](https://github.com/adimiw/eetl-ai-platform/issues)
- **Documentation:** [Full documentation](https://docs.eetl-ai-platform.com)
- **Email:** adhithanraja6@gmail.com

---

**Happy Deploying! 🚀**
