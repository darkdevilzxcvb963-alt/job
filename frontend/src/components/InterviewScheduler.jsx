import { useState, useEffect } from 'react'
import { getMyInterviews, updateInterview } from '../services/api'
import { Calendar, Clock, Video, MapPin, MoreVertical, CheckCircle, XCircle } from 'lucide-react'

export default function InterviewScheduler() {
  const [interviews, setInterviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchInterviews()
  }, [])

  const fetchInterviews = async () => {
    try {
      const res = await getMyInterviews()
      setInterviews(res.data)
    } catch (err) {
      console.error('Failed to load interviews:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (id, status) => {
    try {
      await updateInterview(id, { status })
      fetchInterviews()
    } catch (err) {
      console.error('Failed to update interview:', err)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return '#3b82f6'
      case 'completed': return '#22c55e'
      case 'cancelled': return '#ef4444'
      case 'no_show': return '#f59e0b'
      default: return '#6b7280'
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'phone_screen': return '📞'
      case 'technical': return '💻'
      case 'behavioral': return '🗣'
      case 'onsite': return '🏢'
      default: return '📋'
    }
  }

  const filtered = interviews.filter(i => filter === 'all' || i.status === filter)

  if (loading) {
    return <div className="interview-loading"><div className="pulse-loader"></div></div>
  }

  return (
    <div className="interview-scheduler">
      <div className="is-header">
        <h3><Calendar size={20} /> Interviews</h3>
        <div className="is-filters">
          {['all', 'scheduled', 'completed', 'cancelled'].map(f => (
            <button
              key={f}
              className={`filter-btn ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <Calendar size={36} strokeWidth={1} />
          <p>No interviews {filter !== 'all' ? `with status "${filter}"` : 'scheduled'}</p>
        </div>
      ) : (
        <div className="is-list">
          {filtered.map(interview => (
            <div key={interview.id} className="interview-card">
              <div className="ic-left">
                <span className="ic-type-icon">{getTypeIcon(interview.interview_type)}</span>
                <div className="ic-details">
                  <div className="ic-time">
                    <Calendar size={14} />
                    {new Date(interview.scheduled_at).toLocaleDateString()}
                    <Clock size={14} />
                    {new Date(interview.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="ic-duration">{interview.duration_minutes} minutes</div>
                  {interview.location_or_link && (
                    <div className="ic-location">
                      {interview.location_or_link.startsWith('http') ? (
                        <a href={interview.location_or_link} target="_blank" rel="noopener noreferrer">
                          <Video size={14} /> Join Meeting
                        </a>
                      ) : (
                        <span><MapPin size={14} /> {interview.location_or_link}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="ic-right">
                <span
                  className="ic-status"
                  style={{ color: getStatusColor(interview.status), borderColor: getStatusColor(interview.status) }}
                >
                  {interview.status}
                </span>

                {interview.status === 'scheduled' && (
                  <div className="ic-actions">
                    <button
                      className="btn-icon btn-success"
                      onClick={() => handleStatusChange(interview.id, 'completed')}
                      title="Mark completed"
                    >
                      <CheckCircle size={16} />
                    </button>
                    <button
                      className="btn-icon btn-danger"
                      onClick={() => handleStatusChange(interview.id, 'cancelled')}
                      title="Cancel"
                    >
                      <XCircle size={16} />
                    </button>
                  </div>
                )}
              </div>

              {interview.questions_json && interview.questions_json.length > 0 && (
                <div className="ic-questions">
                  <h5>Suggested Questions</h5>
                  <ol>
                    {interview.questions_json.slice(0, 5).map((q, i) => (
                      <li key={i}>{typeof q === 'string' ? q : q.question || JSON.stringify(q)}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
