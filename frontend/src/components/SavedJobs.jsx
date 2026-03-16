import { useState, useEffect } from 'react'
import { getSavedJobs, unsaveJob } from '../services/api'
import { Bookmark, Trash2, MapPin, Building2, ExternalLink } from 'lucide-react'

export default function SavedJobs() {
  const [savedJobs, setSavedJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSavedJobs()
  }, [])

  const fetchSavedJobs = async () => {
    try {
      const res = await getSavedJobs()
      setSavedJobs(res.data)
    } catch (err) {
      console.error('Failed to load saved jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleUnsave = async (jobId) => {
    try {
      await unsaveJob(jobId)
      setSavedJobs(prev => prev.filter(j => j.job_id !== jobId))
    } catch (err) {
      console.error('Failed to unsave job:', err)
    }
  }

  if (loading) {
    return (
      <div className="saved-jobs-skeleton">
        {[1, 2, 3].map(i => (
          <div key={i} className="skeleton-card">
            <div className="skeleton-line skeleton-title"></div>
            <div className="skeleton-line skeleton-subtitle"></div>
            <div className="skeleton-line skeleton-text"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="saved-jobs-container">
      <div className="saved-jobs-header">
        <h3><Bookmark size={20} /> Saved Jobs</h3>
        <span className="saved-count">{savedJobs.length} saved</span>
      </div>

      {savedJobs.length === 0 ? (
        <div className="empty-state">
          <Bookmark size={48} strokeWidth={1} />
          <p>No saved jobs yet</p>
          <span>Bookmark interesting jobs from your matches to review later</span>
        </div>
      ) : (
        <div className="saved-jobs-list">
          {savedJobs.map(job => (
            <div key={job.id} className="saved-job-card">
              <div className="saved-job-info">
                <h4>{job.job_title || 'Untitled Job'}</h4>
                <div className="saved-job-meta">
                  {job.company && <span><Building2 size={14} /> {job.company}</span>}
                  {job.location && <span><MapPin size={14} /> {job.location}</span>}
                </div>
                {job.notes && <p className="saved-job-notes">{job.notes}</p>}
              </div>
              <div className="saved-job-actions">
                <button
                  className="btn-icon btn-danger"
                  onClick={() => handleUnsave(job.job_id)}
                  title="Remove from saved"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
