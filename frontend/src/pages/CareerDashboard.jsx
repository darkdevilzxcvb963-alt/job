import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  getProfileCompleteness, 
  getCareerSuggestionsApi, 
  completeCareerSuggestionApi,
  getMyMatches
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { 
  Trophy, 
  Target, 
  Zap, 
  CheckCircle, 
  ArrowRight, 
  TrendingUp,
  Sparkles,
  Info
} from 'lucide-react';
import '../styles/CareerDashboard.css';

const CareerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('insights');

  // Queries
  const { data: completeness, isLoading: loadingCompleteness } = useQuery(
    'profile-completeness',
    () => getProfileCompleteness().then(res => res.data)
  );

  const { data: suggestions, isLoading: loadingSuggestions } = useQuery(
    'career-suggestions',
    () => getCareerSuggestionsApi().then(res => res.data)
  );

  const { data: matches } = useQuery(
    ['my-matches', { limit: 5 }],
    () => getMyMatches({ limit: 5 }).then(res => res.data)
  );

  // Identify top match for training
  const topMatch = matches && matches.length > 0 ? matches[0] : null;

  // Manual skill gap calculation for preview if match weights aren't detailed enough
  const missingSkillsPreview = topMatch?.missing_skills || [];

  // Mutations
  const completeSuggestion = useMutation(
    (id) => completeCareerSuggestionApi(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('career-suggestions');
        queryClient.invalidateQueries('profile-completeness');
      }
    }
  );

  const getSettingsTabForSuggestion = (item) => {
    const title = item.title.toLowerCase();
    const cat = item.category.toLowerCase();
    
    if (title.includes('skill')) return { tab: 'professional', section: 'skills' };
    if (title.includes('project')) return { tab: 'professional', section: 'projects' };
    if (title.includes('experience')) return { tab: 'professional', section: 'experience' };
    if (title.includes('education')) return { tab: 'professional', section: 'education' };
    
    if (title.includes('salary')) return { tab: 'preferences', section: 'salary' };
    if (title.includes('location')) return { tab: 'preferences', section: 'location' };
    
    if (cat === 'skills') return { tab: 'professional', section: 'skills' };
    if (cat === 'preferences') return { tab: 'preferences', section: 'general' };
    
    return { tab: 'account', section: 'account' };
  };

  const handleUpdateClick = (item) => {
    const { tab, section } = getSettingsTabForSuggestion(item);
    navigate(`/settings?tab=${tab}&section=${section}`);
  };

  if (loadingCompleteness || loadingSuggestions) {
    return (
      <div className="dashboard-loading-skeleton">
        <div className="skeleton-header">
          <div className="skeleton-line skeleton-title shimmer"></div>
          <div className="skeleton-line skeleton-subtitle shimmer"></div>
        </div>
        <div className="skeleton-progress-bar shimmer"></div>
        <div className="skeleton-grid">
          <div className="skeleton-card shimmer"></div>
          <div className="skeleton-card shimmer"></div>
          <div className="skeleton-card shimmer"></div>
        </div>
        <p className="skeleton-label">Analyzing your career path...</p>
      </div>
    );
  }

  return (
    <div className="career-dashboard page-container">
      {/* Hero Section */}
      <section className="dashboard-hero">
        <div className="hero-content">
          <div className="welcome-badge">
            <Sparkles size={16} />
            <span>AI Career Intelligence Active</span>
          </div>
          <h1>Welcome back, {user?.full_name?.split(' ')[0]}!</h1>
          <p>Your career profile is evolving. Here's your personalized intelligence report.</p>
        </div>
        
        <div className="profile-strength-card glass-panel">
          <div className="strength-header">
            <h3>Profile Strength</h3>
            <span className="strength-value">{completeness?.overall_score}%</span>
          </div>
          <div className="strength-bar-container">
            <div 
              className="strength-bar-fill" 
              style={{ width: `${completeness?.overall_score}%` }}
            ></div>
          </div>
          <p className="strength-footer">
            {completeness?.overall_score < 100 
              ? `Complete your profile to unlock high-priority job matches.` 
              : "Excellent! Your profile is fully optimized for AI matching."}
          </p>
        </div>
      </section>

      {/* Main Stats Grid */}
      <div className="dashboard-grid">
        {/* Left Column: Intelligence Hub */}
        <div className="dashboard-main">
          <div className="tabs-header">
            <button 
              className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveTab('insights')}
            >
              Intelligence Insights
            </button>
            <button 
              className={`tab-btn ${activeTab === 'suggestions' ? 'active' : ''}`}
              onClick={() => setActiveTab('suggestions')}
            >
              Career Actions ({suggestions?.length || 0})
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'insights' ? (
              <div className="insights-view">
                <div className="insight-card glass-panel highlight-purple">
                  <div className="insight-icon"><Target /></div>
                  <div className="insight-info">
                    <h4>Market Alignment</h4>
                    <p>Your current skill set aligns 85% with Senior Software Engineer roles in your target locations.</p>
                  </div>
                </div>

                <div className="insight-card glass-panel highlight-blue">
                  <div className="insight-icon"><TrendingUp /></div>
                  <div className="insight-info">
                    <h4>Growth Pattern</h4>
                    <p>High demand detected for your "React" and "FastAPI" expertise in current job market.</p>
                  </div>
                </div>

                <div className="completeness-breakdown-wrapper">
                    <div className="completeness-breakdown glass-panel">
                        <h4>Profile Completeness Breakdown</h4>
                        <div className="breakdown-grid">
                            {completeness?.breakdown && Object.entries(completeness.breakdown).map(([key, value]) => {
                                const weights = {
                                    bio: 10, headline: 5, profile_picture: 5, 
                                    skills: 20, experience: 25, education: 15, 
                                    projects: 10, location_prefs: 5, salary_prefs: 5
                                };
                                const weight = weights[key] || 10;
                                const percentage = Math.round(Math.min((value / weight) * 100, 100));

                                return (
                                    <div key={key} className={`breakdown-item ${percentage === 100 ? 'status-completed' : 'status-incomplete'}`}>
                                        <div className="item-info">
                                            <span className="item-label">{key.replace('_', ' ')}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* AI TRAINING HUB - Utilizing empty space */}
                    <div className="ai-training-hub glass-panel highlight-purple-glow">
                        <div className="hub-header">
                            <Sparkles size={20} color="#a78bfa" />
                            <h4>AI Career Training Hub</h4>
                        </div>
                        {topMatch ? (
                            <div className="hub-content">
                                <div className="training-target">
                                    <span className="target-label">Priority Training Target</span>
                                    <p className="target-job">{topMatch.job_title} at {topMatch.company}</p>
                                    <div className="target-score">
                                        <div className="score-ring">
                                            <span>{Math.round(topMatch.overall_score * 100)}%</span>
                                        </div>
                                        <div className="score-info">
                                            <p>Match Score</p>
                                            <span className="uplift-potential">Potential Core Uplift: +15%</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="training-action">
                                    <p>Start your AI-powered preparation to bridge critical skill gaps and ace the interview questions.</p>
                                    <Link to={`/training/${topMatch.id}`} className="btn-hub-primary">
                                        Launch AI Coach <ArrowRight size={18} />
                                    </Link>
                                </div>
                            </div>
                        ) : (
                            <div className="hub-empty">
                                <Info size={32} color="#64748b" />
                                <p>No active matches found. Upload a fresh resume or browse jobs to start AI training.</p>
                                <Link to="/matches" className="btn-hub-secondary">Browse Matches</Link>
                            </div>
                        )}
                    </div>
                </div>
              </div>
            ) : (
              <div className="suggestions-view">
                {suggestions?.length === 0 ? (
                  <div className="empty-suggestions glass-panel">
                    <CheckCircle size={48} className="empty-icon" />
                    <h4>All Caught Up!</h4>
                    <p>Your profile is looking great. We'll notify you when we have new growth suggestions.</p>
                  </div>
                ) : (
                  <div className="suggestions-list">
                    {suggestions?.map((item) => (
                      <div key={item.id} className={`suggestion-item glass-panel priority-${item.priority}`}>
                        <div className="suggestion-body">
                          <div className="suggestion-tags">
                            <span className="tag-category">{item.category}</span>
                            <span className={`tag-priority ${item.priority}`}>{item.priority}</span>
                          </div>
                          <h4>{item.title}</h4>
                          <p>{item.description}</p>
                        </div>
                        <div className="suggestion-btns" style={{ display: 'flex', gap: '0.8rem' }}>
                          <button 
                            className="btn-action-primary"
                            onClick={() => handleUpdateClick(item)}
                            style={{ 
                              background: 'var(--grad-primary)', 
                              color: 'white', 
                              border: 'none', 
                              padding: '0.6rem 1.2rem', 
                              borderRadius: '10px', 
                              fontWeight: '700',
                              fontSize: '0.85rem',
                              cursor: 'pointer',
                              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)'
                            }}
                          >
                            Update Now
                          </button>
                          <button 
                            className="btn-complete"
                            onClick={() => completeSuggestion.mutate(item.id)}
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Sidebar */}
        <div className="dashboard-sidebar">
          <div className="sidebar-section glass-panel">
            <div className="section-header">
              <h3>Top Matches</h3>
              <Link to="/matches" className="view-all">View All</Link>
            </div>
            <div className="mini-match-list">
              {matches?.slice(0, 3).map((match) => (
                <div key={match.id} className="mini-match-card">
                  <div className="match-score-bubble">
                    {Math.round(match.overall_score * 100)}%
                  </div>
                  <div className="match-details">
                    <h5>{match.job_title}</h5>
                    <p>{match.company}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-section glass-panel">
            <h4><Info size={16} /> Pro Tip #1</h4>
            <p>Users who complete their "Projects" section see 40% more recruiter outreach on average.</p>
          </div>

          <div className="sidebar-section glass-panel highlight-blue-glow">
            <h4><TrendingUp size={16} /> Pro Tip #2</h4>
            <p>Tailor your headline to include your most proficient framework (e.g., 'Senior React Developer') for 3x higher search relevancy.</p>
          </div>

          <div className="sidebar-section glass-panel highlight-purple-glow">
            <h4><Sparkles size={16} /> Pro Tip #3</h4>
            <p>Quantify your achievements in the experience section (e.g., 'Reduced latency by 40%') to impress technical recruiters.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CareerDashboard;
