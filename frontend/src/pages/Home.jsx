import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import '../styles/Home.css'

function Home() {
  const { isAuthenticated, user } = useAuth()
  const navigate = useNavigate()

  const handleGetStarted = () => {
    if (isAuthenticated) {
      if (user?.role === 'job_seeker') {
        navigate('/candidate')
      } else {
        navigate('/jobs')
      }
    } else {
      navigate('/signup')
    }
  }

  return (
    <div className="home-page">
      <Navbar />
      <div className="home-container">
        <header className="hero">
          <div className="hero-content">
            <h1 className="hero-title">
              Find Your Perfect Match with
              <span className="gradient-text"> AI-Powered</span> Matching
            </h1>
            <p className="hero-subtitle">
              Intelligently connect job seekers with opportunities using advanced NLP and LLM technology.
              Get personalized matches based on skills, experience, and career goals.
            </p>
            <div className="hero-actions">
              {!isAuthenticated ? (
                <>
                  <button onClick={handleGetStarted} className="btn-primary btn-large">
                    Get Started Free
                  </button>
                  <Link to="/login" className="btn-secondary btn-large">
                    Sign In
                  </Link>
                </>
              ) : (
                <>
                  {user?.role === 'job_seeker' ? (
                    <Link to="/candidate" className="btn-primary btn-large">
                      Go to Dashboard
                    </Link>
                  ) : (
                    <Link to="/jobs" className="btn-primary btn-large">
                      Post a Job
                    </Link>
                  )}
                  <Link to="/matches" className="btn-secondary btn-large">
                    View Matches
                  </Link>
                </>
              )}
            </div>
          </div>
          <div className="hero-visual desktop-only">
            <div className="floating-card card-1">📄 Resume</div>
            <div className="floating-card card-2">💼 Job</div>
            <div className="floating-card card-3">🎯 Match</div>
          </div>
        </header>

        <section className="features">
          <h2 className="section-title">Why Choose ResumeMatch?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI-Powered Matching</h3>
              <p>Advanced NLP algorithms analyze resumes and job descriptions to find the perfect matches based on skills, experience, and career goals.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Fast & Accurate</h3>
              <p>Get instant matches with detailed scoring breakdowns. Our semantic analysis goes beyond keywords to understand context and meaning.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Detailed Insights</h3>
              <p>See exactly why a match was made with comprehensive explanations, skill overlap analysis, and experience alignment metrics.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Secure & Private</h3>
              <p>Your data is protected with enterprise-grade security. We use encrypted storage and secure authentication.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Easy to Use</h3>
              <p>Intuitive interface designed for both job seekers and recruiters. Upload, match, and connect in minutes.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Career Growth</h3>
              <p>Discover opportunities that align with your career path and help you grow professionally.</p>
            </div>
          </div>
        </section>

        <section className="cta-section">
          <div className="cta-glow"></div>
          <div className="cta-content">
            <h2>Ready to Find Your Perfect Match?</h2>
            <p>Join thousands of job seekers and recruiters using AI-powered matching</p>
            <div className="cta-actions">
              {!isAuthenticated ? (
                <Link to="/signup" className="btn-primary btn-large glow-btn">
                  Create Free Account
                </Link>
              ) : (
                <Link to="/matches" className="btn-primary btn-large glow-btn">
                  Explore Matches Now
                </Link>
              )}
            </div>
          </div>
        </section>
      </div>
      <Footer />
    </div>
  )
}

export default Home

