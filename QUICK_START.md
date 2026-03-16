# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key (optional, for LLM features)

### Steps

1. **Navigate to project directory**
   ```bash
   cd new-project
   ```

2. **Configure environment**
   ```bash
   # Copy environment file
   cp backend/.env.example backend/.env
   
   # Edit backend/.env and add your OpenAI API key
   # OPENAI_API_KEY=your-key-here
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Initialize database (first time only)**
   ```bash
   # Enter backend container
   docker-compose exec backend bash
   
   # Run migrations
   alembic upgrade head
   
   # Exit container
   exit
   ```

### Test the Application

1. **Upload a resume**
   - Go to http://localhost:3000/candidate
   - Fill in candidate information
   - Upload a PDF or DOCX resume
   - Click "Create Profile"

2. **Post a job**
   - Go to http://localhost:3000/jobs
   - Fill in job details
   - Add required skills
   - Click "Post Job"

3. **View matches**
   - Go to http://localhost:3000/matches
   - Enter candidate ID or job ID
   - View match scores and explanations

### Troubleshooting

**Port already in use?**
- Change ports in `docker-compose.yml`

**Database connection error?**
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check database URL in `backend/.env`

**SpaCy model not found?**
- Run: `docker-compose exec backend python -m spacy download en_core_web_sm`

**Need to restart?**
```bash
docker-compose down
docker-compose up -d
```

### Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Review [API_REFERENCE.md](docs/API_REFERENCE.md) for API details

Happy coding! 🎉
