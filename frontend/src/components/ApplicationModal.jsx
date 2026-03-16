import { useState } from 'react'
import { X, Send, Sparkles, Briefcase, Building, MapPin, Calendar, Clock, CheckCircle } from 'lucide-react'
import './ApplicationModal.css'

function ApplicationModal({ match, isApplied, onClose, onSubmit, isSubmitting }) {
    const [coverLetter, setCoverLetter] = useState('')
    const maxChars = 1500

    const handleSubmit = (e) => {
        e.preventDefault()
        onSubmit(coverLetter)
    }

    const aiPrefill = () => {
        setCoverLetter(
            `Dear Hiring Manager,\n\nI am excited to apply for the ${match.job_title} position at ${match.company}. ` +
            `With my background and skills, I am confident I would be a strong addition to your team.\n\n` +
            `I have carefully reviewed the job requirements and believe my experience aligns well with what you are looking for. ` +
            `I am particularly drawn to this opportunity because of the impactful work being done at ${match.company}.\n\n` +
            `I look forward to discussing how I can contribute to your team.\n\nBest regards`
        )
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <div className="modal-title-group">
                        <div className="modal-job-icon">
                            <Briefcase size={20} />
                        </div>
                        <div>
                            <h2 className="modal-title">Apply for {match.job_title}</h2>
                            <p className="modal-subtitle">
                                <Building size={13} style={{ display: 'inline', marginRight: 4 }} />
                                {match.company}
                            </p>
                        </div>
                    </div>
                    <button className="modal-close-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                {/* Match Score Banner */}
                <div className="modal-match-banner">
                    <span className="modal-match-score">
                        🎯 {(match.overall_score * 100).toFixed(0)}% Match
                    </span>
                    <span className="modal-match-hint">You're a great fit for this role!</span>
                </div>

                {/* Body Content based on Application Status */}
                {isApplied ? (
                    <div className="modal-body applied-view" style={{ padding: '24px' }}>
                        <div className="success-banner" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#059669', padding: '16px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                            <CheckCircle size={24} />
                            <div>
                                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Application Submitted</h3>
                                <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', opacity: 0.9 }}>The recruiter has been notified.</p>
                            </div>
                        </div>

                        <div className="application-details-grid" style={{ display: 'grid', gap: '16px', background: 'var(--bg-secondary)', padding: '20px', borderRadius: '12px' }}>
                            <div className="detail-row" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Calendar size={18} style={{ color: 'var(--text-secondary)' }} />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Date Applied</div>
                                    <div style={{ fontWeight: 500 }}>{match.applied_at ? new Date(match.applied_at).toLocaleDateString() : 'Just now'}</div>
                                </div>
                            </div>
                            <div className="detail-row" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Clock size={18} style={{ color: 'var(--text-secondary)' }} />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Time</div>
                                    <div style={{ fontWeight: 500 }}>{match.applied_at ? new Date(match.applied_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '—'}</div>
                                </div>
                            </div>
                            <div className="detail-row" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Briefcase size={18} style={{ color: 'var(--text-secondary)' }} />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Job Role</div>
                                    <div style={{ fontWeight: 500 }}>{match.job_title}</div>
                                </div>
                            </div>
                            <div className="detail-row" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <Building size={18} style={{ color: 'var(--text-secondary)' }} />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Company Name</div>
                                    <div style={{ fontWeight: 500 }}>{match.company}</div>
                                </div>
                            </div>
                            <div className="detail-row" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <MapPin size={18} style={{ color: 'var(--text-secondary)' }} />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Location</div>
                                    <div style={{ fontWeight: 500 }}>{match.location || 'Remote'}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit}>
                        {/* Cover Letter */}
                        <div className="modal-body">
                            <div className="cover-label-row">
                                <label className="cover-label">Cover Letter <span className="optional-badge">optional</span></label>
                                <button type="button" className="ai-prefill-btn" onClick={aiPrefill}>
                                    <Sparkles size={14} /> AI Draft
                                </button>
                            </div>
                            <textarea
                                className="cover-textarea"
                                placeholder="Tell the recruiter why you're a great fit for this role..."
                                value={coverLetter}
                                onChange={e => setCoverLetter(e.target.value.slice(0, maxChars))}
                                rows={8}
                            />
                            <div className="char-count" style={{ color: coverLetter.length > maxChars * 0.9 ? '#f59e0b' : '#6b7280' }}>
                                {coverLetter.length}/{maxChars}
                            </div>
                        </div>

                        {/* Info box */}
                        <div className="modal-info-box">
                            📬 The recruiter will receive an <strong>email + SMS notification</strong> instantly when you apply.
                        </div>

                        {/* Actions */}
                        <div className="modal-footer">
                            <button type="button" className="modal-btn-cancel" onClick={onClose}>
                                Cancel
                            </button>
                            <button type="submit" className="modal-btn-submit" disabled={isSubmitting}>
                                {isSubmitting
                                    ? <><span className="spinner-ring" /> Submitting...</>
                                    : <><Send size={16} /> Submit Application</>
                                }
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    )
}

export default ApplicationModal
