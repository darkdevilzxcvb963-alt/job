
import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Mail, Phone, FileText, User, Briefcase, CheckCircle, ArrowRight, TrendingUp, MessageCircle, List, Kanban, Calendar } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  getMyMatches, getJobMatches, getJobs, generateMatches, generateMatchesForRecruiter,
  applyToJob, applyWithForm, generateOutreach, updateMatchStatus
} from '../services/api'
import '../styles/Matches.css'
import { useAuth } from '../contexts/AuthContext'
import { useNotify } from '../contexts/NotifyContext'
import ApplicationModal from '../components/ApplicationModal'
import { useMessaging } from '../contexts/MessagingContext'


import ATSPipeline from '../components/ATSPipeline'
import SmartSearch from '../components/SmartSearch'
import ScheduleInterviewModal from '../components/ScheduleInterviewModal'

const getResumeUrl = (path) => {
  if (!path) return '';
  const normalizedPath = path.replace(/\\/g, '/');
  const uploadIndex = normalizedPath.lastIndexOf('uploads/');
  const baseUrl = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1').replace('/api/v1', '');
  if (uploadIndex !== -1) {
    return `${baseUrl}/uploads/${encodeURI(normalizedPath.substring(uploadIndex + 8))}`;
  }
  return `${baseUrl}/uploads/${encodeURI(normalizedPath.split('/').pop())}`;
};

function Matches() {
  const { user } = useAuth()
  const { success } = useNotify()
  const location = useLocation()
  const { openChat } = useMessaging()
  const isRecruiter = user?.role === 'recruiter' || user?.role === 'admin'
  const queryClient = useQueryClient()

  const [expandedJob, setExpandedJob] = useState(null)
  const [allMatches, setAllMatches] = useState({})
  const [loadingAllMatches, setLoadingAllMatches] = useState(false)
  const [expandedMatch, setExpandedMatch] = useState(null)
  const [viewMode, setViewMode] = useState('list') // 'list' or 'pipeline'
  const [matchToDelete, setMatchToDelete] = useState(null)
  const [filterMode, setFilterMode] = useState('all') // 'all', 'ai', 'manual'
  const [applyModal, setApplyModal] = useState(null) // match object or null
  const [scheduleModal, setScheduleModal] = useState(null) // match object or null
  const [applyToast, setApplyToast] = useState('')

  const [outreachDraft, setOutreachDraft] = useState({ matchId: null, text: '' })
  const [isGeneratingOutreach, setIsGeneratingOutreach] = useState(false)

  // Filtering and Sorting State
  const [filters, setFilters] = useState(() => {
    const params = new URLSearchParams(location.search);
    return {
      minScore: parseFloat(params.get('min_score')) || 0.0,
      maxScore: parseFloat(params.get('max_score')) || 1.0,
      jobType: '',
      location: '',
      sortBy: 'score'
    };
  })

  // Mutation for generating matches
  const generateMutation = useMutation(
    async (minScore) => {
      if (isRecruiter) {
        return generateMatchesForRecruiter()
      } else {
        return generateMatches(minScore)
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['myMatches'])
        queryClient.invalidateQueries(['recruiterJobs']) // Also refresh recruiter jobs to check for new matches count
        // Wait a bit and refresh again as it's a bg task
        setTimeout(() => {
          queryClient.invalidateQueries(['myMatches'])
          queryClient.invalidateQueries(['recruiterJobs'])
        }, 2000)
      }
    }
  )

  // Mutation for applying to a job
  const applyMutation = useMutation(
    (matchId) => applyToJob(matchId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['myMatches'])
        success('Application submitted successfully! 🎉')
      }
    }
  )

  // Mutation for applying with cover letter form
  const applyFormMutation = useMutation(
    ({ matchId, coverLetter }) => applyWithForm(matchId, coverLetter),
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['myMatches'])
        setApplyModal(null)
        setApplyToast('🎉 Application sent! The recruiter will be notified by email & SMS.')
        setTimeout(() => setApplyToast(''), 5000)
      }
    }
  )

  // Mutation for AI Outreach
  const outreachMutation = useMutation(
    (data) => generateOutreach(data),
    {
      onSuccess: (response, variables) => {
        setOutreachDraft({ matchId: variables.matchId, text: response.data.message });
        setIsGeneratingOutreach(false);
      }
    }
  )

  // Fetch recruiter's jobs
  const { data: recruiterJobs, isLoading: loadingJobs } = useQuery(
    ['recruiterJobs'],
    () => getJobs(),
    { enabled: isRecruiter && !!user }
  )

  // Fetch current user's matches
  const {
    data: myMatches,
    isLoading: loadingMyMatches,
    refetch: refetchMyMatches
  } = useQuery(
    ['myMatches', filters],
    () => getMyMatches({
      min_score: filters.minScore,
      max_score: filters.maxScore,
      job_type: filters.jobType,
      location: filters.location,
      sort_by: filters.sortBy
    }),
    {
      enabled: !isRecruiter && !!user,
      retry: false
    }
  )

  // Auto-load matches for recruiter
  useEffect(() => {
    if (isRecruiter && recruiterJobs?.data?.length > 0) {
      setLoadingAllMatches(true)
      const fetchAllMatches = async () => {
        try {
          const jobs = recruiterJobs.data;
          const matchPromises = jobs.map(job => 
            getJobMatches(job.id, { min_score: 0.0, limit: 100 })
              .then(res => ({ jobId: job.id, matches: res.data || res || [] }))
              .catch(err => ({ jobId: job.id, matches: [], error: err }))
          );
          
          const results = await Promise.all(matchPromises);
          const matchesData = {};
          results.forEach(res => {
            matchesData[res.jobId] = res.matches;
          });
          setAllMatches(matchesData);
        } catch (error) {
          console.error('Error fetching matches:', error);
        } finally {
          setLoadingAllMatches(false);
        }
      }
      fetchAllMatches()
    }
  }, [isRecruiter, recruiterJobs, filters.minScore, filters.maxScore, filters.sortBy])

  const getMatchColor = (score) => {
    if (score >= 0.8) return '#10b981'
    if (score >= 0.6) return '#f59e0b'
    return '#ef4444'
  }

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({
      ...prev,
      [name]: name === 'minScore' ? parseFloat(value) : value
    }))
  }

  const handleGenerateOutreach = (match) => {
    setIsGeneratingOutreach(true);
    outreachMutation.mutate({
      matchId: match.id,
      candidate_name: match.candidate_name,
      job_title: match.job_title,
      company: match.company,
      match_explanation: match.match_explanation || ''
    });
  }

  const flattenedAllMatches = Object.values(allMatches).flat()

  const [expandedDetails, setExpandedDetails] = useState(null)

  const toggleDetails = (matchId) => {
    if (expandedDetails === matchId) {
      setExpandedDetails(null)
    } else {
      setExpandedDetails(matchId)
    }
  }

  const groupByJob = (matches) => {
    return matches.reduce((acc, match) => {
      const jobId = match.job_id;
      if (!acc[jobId]) {
        acc[jobId] = [];
      }
      acc[jobId].push(match);
      return acc;
    }, {});
  }
  return (
    <div className="matches-page page-container">
      <div className="matches-header-section">
        <h1>🚀 Career OS: AI Match Engine</h1>
        <p>
          {isRecruiter
            ? 'Intelligent candidate pipeline and talent discovery'
            : 'Personalized career opportunities matched to your profile'
          }
        </p>
      </div>

      <div className="controls-section">
        <div className="filters-bar">
          <div className="filter-group">
            <label>Min Match Score: {(filters.minScore * 100).toFixed(0)}%</label>
            <input
              type="range"
              name="minScore"
              min="0"
              max="1"
              step="0.05"
              value={filters.minScore}
              onChange={handleFilterChange}
              className="range-slider"
            />
          </div>

          <div className="filter-group">
            <label>Location</label>
            <input
              type="text"
              name="location"
              placeholder="e.g. Remote, New York"
              value={filters.location}
              onChange={handleFilterChange}
            />
          </div>

          <div className="filter-group">
            <label>Job Type</label>
            <select name="jobType" value={filters.jobType} onChange={handleFilterChange}>
              <option value="">All Types</option>
              <option value="Full-time">Full-time</option>
              <option value="Part-time">Part-time</option>
              <option value="Contract">Contract</option>
              <option value="Freelance">Freelance</option>
            </select>
          </div>
        </div>

        <div className="filter-group">
          <label>Sort By</label>
          <select name="sortBy" value={filters.sortBy} onChange={handleFilterChange}>
            <option value="score">Top Match</option>
            <option value="date">Newest</option>
          </select>
        </div>

        <div className="filter-group">
          <label>&nbsp;</label>
          <button
            className="btn-recalculate"
            onClick={() => generateMutation.mutate(filters.minScore)}
            disabled={generateMutation.isLoading}
          >
            {generateMutation.isLoading ? 'Calculating...' : '↻ Re-calculate Matches'}
          </button>
        </div>
        {isRecruiter && (
          <div className="view-toggle">
            <button
              className={viewMode === 'list' ? 'active' : ''}
              onClick={() => setViewMode('list')}
            > List View </button>
            <button
              className={viewMode === 'pipeline' ? 'active' : ''}
              onClick={() => setViewMode('pipeline')}
            > Kanban Pipeline </button>
          </div>
        )}
      </div>

      {isRecruiter && (
        <div className="recruiter-tools">
          <SmartSearch onCandidateClick={(cand) => console.log('Smart search Result Clicked:', cand)} />
        </div>
      )}

      {isRecruiter ? (
        <div className="recruiter-view">
          {(() => {
            const filteredMatches = (flattenedAllMatches || []).filter(m => {
              // Priority 1: Recruitment Stage Filters (AI vs Manual)
              let passStage = true;
              if (filterMode === 'manual') passStage = m.status !== 'matched';
              if (filterMode === 'ai') passStage = m.status === 'matched';
              if (!passStage) return false;

              // Priority 2: Score Filters
              if (m.overall_score < filters.minScore || m.overall_score > filters.maxScore) return false;

              // Priority 3: Search Terms (if applicable)
              if (filters.location && !m.location?.toLowerCase().includes(filters.location.toLowerCase())) return false;
              if (filters.jobType && m.job_type !== filters.jobType) return false;

              return true;
            });

            // Logic for counts based on current filters (except the stage filter itself)
            const matchesWithScore = (flattenedAllMatches || []).filter(m => 
              m.overall_score >= filters.minScore && m.overall_score <= filters.maxScore
            );
            
            const aiCount = matchesWithScore.filter(m => m.status === 'matched').length;
            const manualCount = matchesWithScore.filter(m => m.status !== 'matched').length;
            const allCount = matchesWithScore.length;

            return viewMode === 'pipeline' ? (
              <ATSPipeline
                matches={filteredMatches}
                onStatusUpdate={(matchId, jobId, newStatus) => {
                  setAllMatches(prev => {
                    const updated = { ...prev };
                    if (updated[jobId]) {
                      updated[jobId] = updated[jobId].map(m => m.id === matchId ? { ...m, status: newStatus } : m);
                    }
                    return updated;
                  });
                }}
                onSchedule={(match) => setScheduleModal(match)}
              />
            ) : (
              <div className="recruiter-dashboard">
                <div className="section-title-premium" style={{ marginBottom: '2rem' }}>
                  <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>Applied Candidates for Job Roles</h2>
                </div>
                <div className="dashboard-header">
                  <div className="view-toggle">
                    <button className={viewMode === 'list' ? 'active' : ''} onClick={() => setViewMode('list')}>
                      <List size={18} /> List View
                    </button>
                    <button className={viewMode === 'pipeline' ? 'active' : ''} onClick={() => setViewMode('pipeline')}>
                      <Kanban size={18} /> Kanban Pipeline
                    </button>
                    
                    <span className="divider" style={{ width: '1px', height: '24px', background: '#e2e8f0', margin: '0 12px' }}></span>
                    <button className={`filter-btn ${filterMode === 'all' ? 'active' : ''}`} onClick={() => setFilterMode('all')}>
                      All ({allCount})
                    </button>
                    <button className={`filter-btn ${filterMode === 'ai' ? 'active' : ''}`} onClick={() => setFilterMode('ai')}>
                      Recommended ({aiCount})
                    </button>
                    <button className={`filter-btn ${filterMode === 'manual' ? 'active' : ''}`} onClick={() => setFilterMode('manual')}>
                      Manual Applied ({manualCount})
                    </button>
                  </div>
                </div>

                <div className="jobs-container">
                  {Object.entries(groupByJob(filteredMatches)).map(([jobId, jobMatches]) => {
                    const job = recruiterJobs?.data?.find(j => j.id === jobId);
                    if (!job) return null;
                    const isExpanded = expandedJob === job.id;

                    return (
                      <div key={job.id} className="job-section">
                        <div
                          className={`job-header ${isExpanded ? 'expanded' : ''}`}
                          onClick={() => setExpandedJob(isExpanded ? null : job.id)}
                        >
                          <div className="job-info">
                            <h3>{job.title}</h3>
                            <p>{job.company} • {job.location}</p>
                          </div>
                          <div className="match-indicator">
                            <span className="count-badge">{jobMatches.length}</span>
                            <span className="arrow">{isExpanded ? '▼' : '▶'}</span>
                          </div>
                        </div>

                        {isExpanded && (
                          <div className="candidates-list">
                            {jobMatches.map((match) => {
                              const progress = (status) => {
                                const stages = ['matched', 'applied', 'screened', 'interview', 'offered', 'hired'];
                                const idx = stages.indexOf(status);
                                if (idx === -1) return 0;
                                return ((idx + 1) / stages.length) * 100;
                              };
                              const currentProgress = progress(match.status);

                              return (
                                <div key={match.id} className="candidate-match-card">
                                  <div className="candidate-card-header">
                                    <div className="candidate-info">
                                      <div className="name-row">
                                        <h4><User size={18} className="icon-inline" style={{ color: '#4f46e5' }} /> {match.candidate_name}</h4>
                                        {match.status !== 'matched' && match.status !== 'applied' && (
                                          <span className="status-badge-inline">{match.status}</span>
                                        )}
                                      </div>
                                      <div className="details-list">
                                        <div className="detail-item"><Mail size={14} style={{ color: '#0ea5e9' }} /><span>{match.candidate_email}</span></div>
                                        {match.candidate_phone && (
                                          <div className="detail-item"><Phone size={14} style={{ color: '#22c55e' }} /><span>{match.candidate_phone}</span></div>
                                        )}
                                      </div>
                                      <div className="application-type" style={{ marginTop: '0.75rem' }}>
                                        {match.status === 'matched' ? (
                                          <span className="type-badge ai-match" style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                                            ✨ Recommended
                                          </span>
                                        ) : (
                                          <span className="type-badge manual-apply" style={{ background: 'rgba(244, 114, 182, 0.1)', color: '#f472b6', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, border: '1px solid rgba(244, 114, 182, 0.2)' }}>
                                            👤 Manual Applied
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                    <div className="score-box-premium">
                                      <div className="score-circle" style={{ background: `conic-gradient(${getMatchColor(match.overall_score)} ${match.overall_score * 360}deg, transparent 0deg)` }}>
                                        <div className="score-inner">
                                          <span className="score-val">{(match.overall_score * 100).toFixed(0)}%</span>
                                        </div>
                                      </div>
                                    </div>
                                  </div>

                                  <div className="recruiter-card-footer">
                                    <div className="status-email-row" style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                                      <select
                                        className="status-select-premium"
                                        value={match.status}
                                        onChange={(e) => updateMatchStatus(match.id, e.target.value).then(() => queryClient.invalidateQueries(['recruiterJobs']))}
                                        onClick={(e) => e.stopPropagation()}
                                        style={{ padding: '8px 12px', borderRadius: '10px', border: '1px solid var(--border-color)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontWeight: 600 }}
                                      >
                                        <option value="matched">Matched</option>
                                        <option value="applied">Applied</option>
                                        <option value="screened">Screened</option>
                                        <option value="interview">Interview</option>
                                        <option value="offered">Offered</option>
                                        <option value="hired">Hired</option>
                                        <option value="rejected">Rejected</option>
                                      </select>
                                      
                                      <a 
                                        href={`mailto:${match.candidate_email}?subject=Interested in your profile for ${match.job_title}&body=Hello ${match.candidate_name}, we are interested in your profile for the ${match.job_title} role at ${match.company}.`} 
                                        className="btn-email-direct"
                                        style={{ 
                                          display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', 
                                          background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', borderRadius: '10px', 
                                          textDecoration: 'none', fontSize: '0.85rem', fontWeight: 600, border: '1px solid rgba(99, 102, 241, 0.2)' 
                                        }}
                                      >
                                        <Mail size={16} /> Email
                                      </a>

                                      <div className="candidate-skills-buttons" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                                        {(match.candidate_skills || []).slice(0, 4).map(skill => (
                                          <button key={skill} style={{ fontSize: '0.75rem', background: 'var(--bg-secondary)', color: 'var(--text-primary)', padding: '5px 14px', borderRadius: '20px', border: '1px solid var(--border-color)', cursor: 'default', fontWeight: 500, boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                                            {skill}
                                          </button>
                                        ))}
                                        <button 
                                          onClick={(e) => { e.stopPropagation(); if (match.candidate_resume_path) window.open(getResumeUrl(match.candidate_resume_path), '_blank') }}
                                          style={{ fontSize: '0.75rem', background: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9', padding: '5px 14px', borderRadius: '20px', border: '1px solid rgba(14, 165, 233, 0.2)', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px', transition: 'all 0.2s' }}
                                          title={match.candidate_resume_summary || "Click to view full Resume Info"}
                                        >
                                          <FileText size={12} /> Candidate Info
                                        </button>
                                      </div>
                                    </div>

                                    <div className="recruiter-card-actions" style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                                      <button 
                                        className="btn-chat-premium"
                                        onClick={(e) => { e.stopPropagation(); openChat(match.candidate_user_id, match.candidate_name); }}
                                        style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', color: '#818cf8', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
                                      >
                                        <MessageCircle size={16} /> <span>Message</span>
                                      </button>
                                      {match.status === 'interview' && (
                                        <button 
                                          className="btn-chat-premium"
                                          onClick={(e) => { e.stopPropagation(); setScheduleModal(match); }}
                                          style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', color: '#10b981', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
                                        >
                                          <Calendar size={16} /> <span>Schedule</span>
                                        </button>
                                      )}
                                      <button 
                                        className="btn-resume-view"
                                        onClick={(e) => { e.stopPropagation(); if (match.candidate_resume_path) window.open(getResumeUrl(match.candidate_resume_path), '_blank') }}
                                        style={{ background: 'transparent', border: '1px solid var(--glass-border)', color: 'var(--text-secondary)', padding: '6px', borderRadius: '8px', cursor: 'pointer' }}
                                      >
                                        <FileText size={18} />
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}
        </div>
      ) : (
        <div className="job-seeker-view">
          {myMatches?.data?.map((match) => {
            const isDetailsExpanded = expandedDetails === match.id;
            return (
              <div key={match.id} className={`job-card ${isDetailsExpanded ? 'expanded' : ''}`}>
                <div className="job-card-content">
                  <div className="card-top">
                    <h3>{match.job_title}</h3>
                    <div className="match-score-badge" style={{ background: getMatchColor(match.overall_score) }}>
                      {(match.overall_score * 100).toFixed(0)}%
                    </div>
                  </div>
                  <p className="company">{match.company}</p>
                  <div className="job-tags">
                    <span>📍 {match.location || 'Remote'}</span>
                    <span>💼 {match.job_type}</span>
                  </div>

                  <div className="match-insights-grid">
                    <div className="insight-text">
                      <strong>💡 AI Insight:</strong>
                      <p>{match.match_explanation?.split('.')[0]}.</p>
                    </div>
                  </div>

                  <div className="card-actions">
                    <button
                      className="btn-primary"
                      onClick={() => setApplyModal(match)}
                    >
                      {match.status === 'applied' ? 'Applied ✅' : 'Quick Apply'}
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => toggleDetails(match.id)}
                    >
                      {isDetailsExpanded ? 'Show Less' : 'View Details'}
                    </button>
                  </div>

                  {isDetailsExpanded && (
                    <div className="match-details-expanded">

                      <div className="ai-analysis-split">
                        <div className="analysis-section">
                          <h4>📃 Resume Insights</h4>
                          <div className="contact-info">
                            <strong>Recruiter Details:</strong>
                            <div className="recruiter-info-row">
                              <span className="recruiter-info-label">Name</span>
                              <span className="recruiter-info-val">{match.recruiter_name || '—'}</span>
                            </div>
                            <div className="recruiter-info-row">
                              <span className="recruiter-info-label">Email</span>
                              <span className="recruiter-info-val">
                                {match.recruiter_email
                                  ? <a href={`mailto:${match.recruiter_email}`} className="recruiter-email-link">{match.recruiter_email}</a>
                                  : '—'}
                              </span>
                            </div>
                            <div className="recruiter-info-row">
                              <span className="recruiter-info-label">Phone</span>
                              <span className="recruiter-info-val">
                                {match.recruiter_phone
                                  ? <a href={`tel:${match.recruiter_phone}`} className="phone-number">{match.recruiter_phone}</a>
                                  : '—'}
                              </span>
                            </div>
                          </div>
                          <p className="resume-summary">
                            <strong>AI Summary:</strong>
                            {match.match_explanation?.split('\n')[0]}...
                          </p>
                        </div>

                        <div className="analysis-section">
                          <h4>🔍 Extracted Skills</h4>
                          <div className="tags-list">
                            {match.candidate_skills?.length > 0
                              ? match.candidate_skills.map(skill => (
                                <span key={skill} className="tag extracted">{skill}</span>
                              ))
                              : <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontStyle: 'italic' }}>
                                No skills extracted yet. Re-processing your resume may help.
                              </span>
                            }
                          </div>
                        </div>
                      </div>

                      <div className="match-breakdown-section">
                        <h4>📊 Match Breakdown</h4>
                        <div className="breakdown-grid">
                          <div className="breakdown-item">
                            <span className="label">🚀 Semantic Similarity:</span>
                            <span className="value">{(match.semantic_similarity * 100).toFixed(1)}%</span>
                          </div>
                          <div className="breakdown-item">
                            <span className="label">🔧 Skills Coverage:</span>
                            <span className="value">{(match.skill_overlap_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="breakdown-item">
                            <span className="label">📅 Experience Alignment:</span>
                            <span className="value">{(match.experience_alignment * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="job-requirements-section">
                        <h4>🎯 Skill Comparison</h4>
                        {(() => {
                          const candidateSkills = (match.candidate_skills || []).map(s => s.toLowerCase());
                          const matched = (match.required_skills || []).filter(s => candidateSkills.includes(s.toLowerCase()));
                          const missing = (match.required_skills || []).filter(s => !candidateSkills.includes(s.toLowerCase()));
                          // Deduplicate extra skills
                          const extraRaw = (match.candidate_skills || []).filter(s => !((match.required_skills || []).map(rs => rs.toLowerCase()).includes(s.toLowerCase())));
                          const extraSeen = new Set();
                          const extra = extraRaw.filter(s => {
                            const key = s.toLowerCase();
                            if (extraSeen.has(key)) return false;
                            extraSeen.add(key);
                            return true;
                          });

                          const MAX_GAPS = 8;
                          const MAX_EXTRA = 10;
                          const visibleMissing = missing.slice(0, MAX_GAPS);
                          const hiddenMissingCount = missing.length - visibleMissing.length;
                          const visibleExtra = extra.slice(0, MAX_EXTRA);
                          const hiddenExtraCount = extra.length - visibleExtra.length;

                          return (
                            <div className="skills-comparison-grid">
                              {/* Matched skills — shown first, positive emphasis */}
                              {matched.length > 0 && (
                                <div className="skills-group" style={{ marginBottom: '1.5rem' }}>
                                  <div className="req-header">
                                    <h5>✅ Skills You Match ({matched.length}/{(match.required_skills || []).length})</h5>
                                  </div>
                                  <div className="tags-list">
                                    {matched.map(skill => (
                                      <span key={`match-${skill}`} className="tag match">✅ {skill}</span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Missing skills — limited to MAX_GAPS, softer wording */}
                              {visibleMissing.length > 0 && (
                                <div className="skills-group" style={{ marginBottom: '1.5rem' }}>
                                  <div className="req-header">
                                    <h5>📚 Skills to Explore ({missing.length})</h5>
                                  </div>
                                  <div className="tags-list">
                                    {visibleMissing.map(skill => (
                                      <span key={`miss-${skill}`} className="tag missing">🔖 {skill}</span>
                                    ))}
                                    {hiddenMissingCount > 0 && (
                                      <span className="tag" style={{ background: 'rgba(148,163,184,0.1)', color: '#94a3b8', border: '1px dashed #94a3b8', fontSize: '0.8rem' }}>
                                        +{hiddenMissingCount} more
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* Extra skills — capped, deduplicated */}
                              {visibleExtra.length > 0 && (
                                <div className="skills-group">
                                  <h5>✨ Your Extra Skills (Value Add)</h5>
                                  <div className="tags-list">
                                    {visibleExtra.map(skill => (
                                      <span key={`extra-${skill}`} className="tag extra">{skill}</span>
                                    ))}
                                    {hiddenExtraCount > 0 && (
                                      <span className="tag" style={{ background: 'rgba(168,85,247,0.08)', color: '#a855f7', border: '1px dashed #a855f7', fontSize: '0.8rem' }}>
                                        +{hiddenExtraCount} more
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </div>

                      <div className="ai-analysis-section">
                        <h4>🤖 Comprehensive AI Analysis</h4>
                        {match.match_explanation
                          ? <p>{match.match_explanation}</p>
                          : <p style={{ color: '#64748b', fontStyle: 'italic', fontSize: '0.88rem' }}>
                            ⏳ AI analysis is being generated in the background. Check back shortly after refreshing.
                          </p>
                        }
                      </div>

                      <div className="job-description-section">
                        <h4>📄 Job Description</h4>
                        <p className="job-desc-text">
                          {match.description || match.job_description || 'Job description not available.'}
                        </p>
                      </div>

                    </div>
                  )}

                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Application Modal */}
      {applyModal && (
        <ApplicationModal
          match={applyModal}
          isApplied={applyModal.status === 'applied'}
          onClose={() => setApplyModal(null)}
          isSubmitting={applyFormMutation.isLoading}
          onSubmit={(coverLetter) => applyFormMutation.mutate({ matchId: applyModal.id, coverLetter })}
        />
      )}

      {/* Schedule Interview Modal */}
      {scheduleModal && (
        <ScheduleInterviewModal
          isOpen={!!scheduleModal}
          candidate={{ id: scheduleModal.candidate_id, name: scheduleModal.candidate_name }}
          application_id={scheduleModal.id} // match.id is often used as application identifier in this flow
          onClose={() => setScheduleModal(null)}
          onSuccess={() => {
            setApplyToast('📅 Interview scheduled! Candidate will be notified.');
            setTimeout(() => setApplyToast(''), 5000);
            queryClient.invalidateQueries(['recruiterJobs']);
          }}
        />
      )}

      {/* Success Toast */}
      {applyToast && (
        <div style={{
          position: 'fixed', bottom: '28px', left: '50%', transform: 'translateX(-50%)',
          background: 'linear-gradient(135deg,#059669,#10b981)', color: '#fff',
          padding: '14px 28px', borderRadius: '14px', fontWeight: 600, fontSize: '0.92rem',
          boxShadow: '0 8px 30px rgba(16,185,129,0.4)', zIndex: 2000,
          animation: 'slideUp 0.3s ease', whiteSpace: 'nowrap'
        }}>
          {applyToast}
        </div>
      )}

    </div>
  )
}

export default Matches

