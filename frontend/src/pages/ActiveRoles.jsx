import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { deleteJob, getJobs } from '../services/api'
import { Briefcase, Search, MapPin, ExternalLink, ArrowLeft, Clock, Plus, Trash2 } from 'lucide-react'
import { useNotify } from '../contexts/NotifyContext'
import '../styles/Analytics.css'

function ActiveRoles() {
  const navigate = useNavigate()
  const { confirm, success, error: notifyError } = useNotify()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const response = await getJobs()
      setJobs(response.data)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteRole = async (jobId, title) => {
    const ok = await confirm(`Are you sure you want to delete "${title}"? This will remove all associated matches and pipeline data.`)
    if (!ok) return

    try {
      await deleteJob(jobId)
      setJobs(jobs.filter(j => j.id !== jobId))
      success('Position deleted successfully.')
    } catch (error) {
      console.error('Failed to delete role:', error)
      notifyError('Failed to delete role: ' + (error.response?.data?.detail || error.message))
    }
  }

  const filteredJobs = (jobs || []).filter(j => 
    (j.title || '').toLowerCase().includes((search || '').toLowerCase()) || 
    (j.company || '').toLowerCase().includes((search || '').toLowerCase())
  )

  const activeJobs = filteredJobs.filter(j => j.is_active !== false)
  const closedJobs = filteredJobs.filter(j => j.is_active === false)

  return (
    <div className="analytics-container page-container">
      <div className="analytics-header">
        <button className="back-btn" onClick={() => navigate('/analytics')}>
          <ArrowLeft size={18} /> Back
        </button>
        <div className="header-icon-box u-bg-green">
          <Briefcase size={32} />
        </div>
        <div className="header-text">
          <h1>Active Recruitment Roles</h1>
          <p>Manage and track all open job positions.</p>
        </div>
      </div>

      <div className="search-bar-talent">
        <Search size={20} />
        <input 
          type="text" 
          placeholder="Search by role title or company..." 
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="dashboard-stats-row">
        <button className="post-role-btn-alt" onClick={() => navigate('/jobs')}>
          <Plus size={20} /> Post New Role
        </button>
      </div>

      {loading ? (
        <div className="loading-state">Loading roles...</div>
      ) : filteredJobs.length === 0 ? (
        <div className="empty-state-talent">
          <Briefcase size={48} className="empty-icon" />
          <h3>No active roles found</h3>
          <p>Post a new job opportunity to start matching with candidates.</p>
        </div>
      ) : (
        <div className="roles-sections">
          <section className="roles-list-section">
            <h2 className="section-title-alt">Active Positions ({activeJobs.length})</h2>
            <div className="roles-grid">
              {activeJobs.map(job => (
                <div key={job.id} className="role-card">
                  <div className="role-header">
                    <div className="role-main">
                      <h3>{job.title}</h3>
                      <p className="role-company">{job.company}</p>
                    </div>
                    <div className="role-actions-top">
                      <span className="status-badge-active">Active</span>
                      <button 
                        className="delete-role-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteRole(job.id, job.title);
                        }}
                        title="Delete this role"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="role-details">
                    <p><MapPin size={14} /> {job.location || 'Remote'}</p>
                    <p><Clock size={14} /> Posted {new Date(job.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="role-skills">
                    {(job.required_skills || []).slice(0, 3).map(skill => (
                      <span key={skill} className="skill-tag">{skill}</span>
                    ))}
                    {(job.required_skills || []).length > 3 && (
                      <span className="skill-tag-more">+{ (job.required_skills || []).length - 3} more</span>
                    )}
                  </div>
                  <button 
                    className="view-role-matches"
                    onClick={() => navigate(`/matches?jobId=${job.id}`)}
                  >
                    View Pipeline <ExternalLink size={14} />
                  </button>
                </div>
              ))}
            </div>
          </section>

          {closedJobs.length > 0 && (
            <section className="roles-list-section closed-roles">
              <h2 className="section-title-alt grey">Closed Positions ({closedJobs.length})</h2>
              <div className="roles-grid">
                {closedJobs.map(job => (
                  <div key={job.id} className="role-card closed">
                    <div className="role-header">
                      <div className="role-info">
                        <h3>{job.title}</h3>
                        <p className="role-company">{job.company}</p>
                      </div>
                      <div className="role-actions-top">
                        <span className="status-badge-closed">Closed</span>
                        <button 
                          className="delete-role-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteRole(job.id, job.title);
                          }}
                          title="Delete this role"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                    <button 
                      className="view-role-matches"
                      onClick={() => navigate(`/matches?jobId=${job.id}`)}
                    >
                      View Archive <ExternalLink size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  )
}

export default ActiveRoles
