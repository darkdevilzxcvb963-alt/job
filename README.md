# AI-Powered Resume & Job Matching Platform

An intelligent platform that connects job seekers with relevant job opportunities using Natural Language Processing (NLP) and Large Language Models (LLMs). The system overcomes limitations of traditional keyword-based recruitment by enabling semantic understanding of resumes and job descriptions.

## ✨ Key Features

### Platform Features
- **Resume Parsing**: Extract text and structured data from PDF and DOCX files
- **NLP Processing**: Text preprocessing, Named Entity Recognition (NER), skill extraction
- **Semantic Matching**: Use BERT/Sentence-BERT embeddings for contextual understanding
- **Intelligent Scoring**: Enhanced 6-factor matching formula (Semantic, Skills, Experience, Location, Salary, Seniority)
- **AI Skill Gap Analysis**: Detect missing skills and get personalized course recommendations
- **Resume Scoring (ATS)**: Get ATS compatibility scores and improvements for your resume
- **Interview Intelligence**: Automated interview question generation based on match context
- **Real-time Notifications**: In-app, Email, and SMS alerts for recruiters and candidates
- **Direct Messaging**: Seamless communication between recruiters and candidates
- **Shortlist Management**: Recruiter-side candidate organization and tracking
- **Modern UI**: High-contrast, theme-aware interface with full Dark Mode support
- **LLM Integration**: Generate summaries, normalize job titles, and provide deep match explanations
- **RESTful API**: Modular backend with FastAPI
- **Modern Frontend**: React-based user interface with aurora-styled aesthetics

### 🆕 Admin Panel Features
- **User Management**: Verify, activate, deactivate, or delete user accounts
- **Recruiter Verification**: Approve or reject recruiter companies
- **Real-time Statistics**: Monitor platform metrics and user growth
- **Activity Logging**: Track user actions and login activities
- **Search & Filter**: Find and manage users efficiently
- **Role-Based Access**: Separate access for admins, job seekers, and recruiters
- **Professional Dashboard**: Responsive admin interface

## Project Structure

```
new-project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic (NLP, matching, LLM)
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   ├── uploads/            # Uploaded resume files
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── styles/         # CSS files
│   ├── package.json
│   └── Dockerfile
├── database/               # Database scripts
├── tests/                 # Test files
├── docs/                  # Documentation
└── docker-compose.yml     # Docker orchestration
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker and Docker Compose (optional)
- OpenAI API key (for LLM features)

## Installation

### Option 1: Using Docker (Recommended)

1. Clone or navigate to the project directory:
```bash
cd new-project
```

2. Create a `.env` file in the `backend/` directory:
```bash
cp backend/.env.example backend/.env
```

3. Edit `backend/.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

4. Start all services:
```bash
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Installation

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download SpaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Set up database:
```bash
# Create PostgreSQL database
createdb resume_matching_db

# Run migrations
alembic upgrade head
```

7. Start the server:
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

## Usage

### For Job Seekers

1. Navigate to the Candidate Dashboard
2. Fill in your information (name, email, phone)
3. Upload your resume (PDF or DOCX)
4. The system will automatically:
   - Parse your resume
   - Extract skills and experience
   - Generate semantic embeddings
   - Create a summary

5. View your job matches to see relevant opportunities

### For Recruiters

1. Navigate to Job Posting
2. Fill in job details:
   - Title, company, description
   - Required skills
   - Experience requirements
   - Location and salary (optional)

3. The system will:
   - Generate embeddings for the job
   - Normalize the job title
   - Match with candidates

4. View job matches to see top candidates

### Viewing Matches

- **Candidate Matches**: See all jobs that match a candidate
- **Job Matches**: See all candidates that match a job
- Each match includes:
  - Overall match score
  - Semantic similarity
  - Skill overlap
  - Experience alignment
  - LLM-generated explanation

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎯 Admin Panel

The admin panel is now available for managing users and recruiters!

### Quick Start (Admin Panel)

1. **Initialize Database** (first time only):
```bash
cd backend
python init_db_improved.py
```

2. **Start Services**:
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

3. **Access Admin Panel**:
```
URL: http://localhost:3000/admin
Email: admin@example.com
Password: Admin@1234
```

### Admin Features

#### User Management
- List all users with pagination
- Search by email or name
- Filter by role (Job Seeker, Recruiter, Admin)
- Verify unverified user accounts
- Reject or deactivate suspicious accounts
- View user registration dates and status

#### Recruiter Verification
- View pending recruiter companies
- Review company information
- Approve company verification
- Reject companies with reason

#### Platform Statistics
- Real-time user metrics
- Verification status overview
- User distribution by role
- Recent activity log
- Active user count

### Test Accounts

```
Admin Account (Full Access)
├─ Email: admin@example.com
├─ Password: Admin@1234
└─ URL: http://localhost:3000/admin

Job Seeker (Test)
├─ Email: candidate@example.com
├─ Password: Test@1234
└─ URL: http://localhost:3000/candidate

Recruiter (Test)
├─ Email: recruiter@example.com
├─ Password: Test@1234
└─ URL: http://localhost:3000/jobs
```

### API Documentation

All admin endpoints are documented in the API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Admin endpoints are prefixed with `/api/v1/admin/`

For detailed admin documentation, see:
- [Admin Panel Quick Start](ADMIN_QUICK_START.md)
- [Admin Panel Complete Guide](ADMIN_PANEL_GUIDE.md)
- [Admin Implementation Summary](ADMIN_IMPLEMENTATION_SUMMARY.md)

## Configuration

### Environment Variables

Key environment variables (see `backend/.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for LLM features
- `SECRET_KEY`: Secret key for JWT tokens
- `SPACY_MODEL`: SpaCy model name (default: en_core_web_sm)
- `SENTENCE_TRANSFORMER_MODEL`: Embedding model (default: all-MiniLM-L6-v2)
- `LLM_MODEL`: OpenAI model (default: gpt-4-turbo-preview)

## Testing

Run tests:
```bash
cd backend
pytest tests/
```

## Performance Evaluation

The system can be evaluated using:
- Precision, Recall, F1-score
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG)
- User feedback metrics

Evaluation scripts can be added in the `tests/` directory.

## Technologies Used

### Backend
- FastAPI: Modern Python web framework
- SQLAlchemy: ORM for database operations
- Transformers: Hugging Face transformers for NLP
- Sentence-Transformers: Semantic embeddings
- SpaCy: NLP processing and NER
- OpenAI API: LLM integration
- Alembic: Database migrations

### Frontend
- React: UI framework
- Vite: Build tool
- React Router: Routing
- React Query: Data fetching
- Axios: HTTP client

### Database
- PostgreSQL: Relational database

## Security

- Environment variables for sensitive data
- File upload validation
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)

## Future Enhancements

- User authentication and authorization
- Advanced skill extraction with custom NER models
- Real-time matching notifications
- Dashboard analytics
- Batch processing for multiple resumes
- Integration with job boards
- A/B testing for matching algorithms
- Performance optimization and caching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is for educational purposes. Please ensure compliance with data privacy regulations (GDPR, etc.) when handling personal information.

## Support

For issues and questions, please open an issue in the repository.

## Acknowledgments

- Built with FastAPI, React, and modern NLP/LLM technologies
- Uses open-source libraries from the Python and JavaScript ecosystems
