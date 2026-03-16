# Setup Guide

## Quick Start

### 1. Prerequisites Check

Ensure you have:
- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL 15+ installed and running
- OpenAI API key (optional, for LLM features)

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download SpaCy model
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Setup

```bash
# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Troubleshooting

### Common Issues

1. **SpaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Database connection error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env

3. **Port already in use**
   - Change ports in docker-compose.yml or
   - Stop other services using the ports

4. **OpenAI API errors**
   - Verify API key in .env
   - Check API quota/limits
   - LLM features will have fallbacks if API unavailable

## Next Steps

1. Upload a test resume
2. Create a test job posting
3. Generate matches
4. Review match explanations
