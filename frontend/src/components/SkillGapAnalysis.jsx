import { useState, useEffect } from 'react'
import { analyzeSkillGap, scoreResume } from '../services/api'
import { Target, TrendingUp, BookOpen, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

export default function SkillGapAnalysis({ candidateId, jobId, jobTitle }) {
  const [gap, setGap] = useState(null)
  const [resumeScore, setResumeScore] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('gap')

  const runAnalysis = async () => {
    setLoading(true)
    try {
      const [gapRes, scoreRes] = await Promise.all([
        analyzeSkillGap(candidateId, jobId),
        scoreResume(candidateId, jobId)
      ])
      setGap(gapRes.data)
      setResumeScore(scoreRes.data)
    } catch (err) {
      console.error('Analysis failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#ef4444'
      case 'moderate': return '#f59e0b'
      case 'low': return '#22c55e'
      default: return '#6b7280'
    }
  }

  const getGradeColor = (grade) => {
    if (grade?.startsWith('A')) return '#22c55e'
    if (grade === 'B') return '#3b82f6'
    if (grade === 'C') return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="skill-gap-container">
      <div className="skill-gap-header">
        <h3><Target size={20} /> AI Skills & Resume Analysis</h3>
        {jobTitle && <span className="target-job">For: {jobTitle}</span>}
      </div>

      {!gap && !loading && (
        <button className="btn-primary analyze-btn" onClick={runAnalysis}>
          <TrendingUp size={16} /> Run Analysis
        </button>
      )}

      {loading && (
        <div className="analysis-loading">
          <div className="pulse-loader"></div>
          <p>Analyzing your skills and resume...</p>
        </div>
      )}

      {gap && (
        <>
          <div className="analysis-tabs">
            <button
              className={`tab ${activeTab === 'gap' ? 'active' : ''}`}
              onClick={() => setActiveTab('gap')}
            >
              Skill Gap
            </button>
            <button
              className={`tab ${activeTab === 'resume' ? 'active' : ''}`}
              onClick={() => setActiveTab('resume')}
            >
              Resume Score
            </button>
            <button
              className={`tab ${activeTab === 'learn' ? 'active' : ''}`}
              onClick={() => setActiveTab('learn')}
            >
              Learning Path
            </button>
          </div>

          {activeTab === 'gap' && (
            <div className="gap-results">
              <div className="coverage-meter">
                <div className="coverage-bar">
                  <div
                    className="coverage-fill"
                    style={{ width: `${(gap.coverage_score * 100)}%` }}
                  ></div>
                </div>
                <span className="coverage-label">
                  {Math.round(gap.coverage_score * 100)}% Skill Coverage
                  ({gap.total_matched}/{gap.total_required} required skills)
                </span>
              </div>

              <div className="skills-grid">
                <div className="skills-column matched">
                  <h4><CheckCircle size={16} /> Matched Skills ({gap.matched_skills.length})</h4>
                  <div className="skill-tags">
                    {gap.matched_skills.map(s => (
                      <span key={s} className="skill-tag skill-matched">{s}</span>
                    ))}
                  </div>
                </div>

                <div className="skills-column missing">
                  <h4><XCircle size={16} /> Missing Skills ({gap.missing_skills.length})</h4>
                  <div className="skill-tags">
                    {gap.missing_skills.map(m => (
                      <span
                        key={m.skill}
                        className="skill-tag skill-missing"
                        style={{ borderColor: getSeverityColor(m.severity) }}
                      >
                        {m.skill}
                        <span className="severity-dot" style={{ background: getSeverityColor(m.severity) }}></span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {gap.bridgeable_skills.length > 0 && (
                <div className="bridgeable-section">
                  <h4><TrendingUp size={16} /> Bridgeable Skills</h4>
                  {gap.bridgeable_skills.map(b => (
                    <div key={b.skill} className="bridgeable-item">
                      <strong>{b.skill}</strong>
                      <span className="bridge-hint">You know {b.you_know} → {b.learning_path}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'resume' && resumeScore && (
            <div className="resume-score-results">
              <div className="score-hero">
                <div className="grade-badge" style={{ color: getGradeColor(resumeScore.grade) }}>
                  {resumeScore.grade}
                </div>
                <div className="score-number">{Math.round(resumeScore.overall_score * 100)}%</div>
                <p>ATS Compatibility Score</p>
              </div>

              <div className="score-breakdown">
                {Object.entries(resumeScore.section_scores || {}).map(([key, val]) => (
                  <div key={key} className="score-row">
                    <span className="score-label">{val.label}</span>
                    <span className={`score-indicator ${val.found ? 'found' : 'missing'}`}>
                      {val.found ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                    </span>
                  </div>
                ))}
              </div>

              <div className="feedback-list">
                <h4>Recommendations</h4>
                {resumeScore.feedback?.map((f, i) => (
                  <div key={i} className="feedback-item">
                    <BookOpen size={14} />
                    <span>{f}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'learn' && gap.recommendations?.length > 0 && (
            <div className="learning-path">
              <h4><BookOpen size={16} /> Recommended Courses</h4>
              {gap.recommendations.map((rec, i) => (
                <div key={i} className="course-card">
                  <div className="course-info">
                    <strong>{rec.skill}</strong>
                    <span className="course-name">{rec.course}</span>
                    <span className="course-meta">{rec.platform} • {rec.duration}</span>
                  </div>
                  {rec.url && (
                    <a href={rec.url} target="_blank" rel="noopener noreferrer" className="course-link">
                      Start Learning →
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
