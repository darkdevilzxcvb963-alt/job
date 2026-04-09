import { useState, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQuery } from 'react-query'
import { uploadAndAnalyzeResume, createCandidate, updateCandidate, getCandidates, processResume, getSelectionStats } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { useNotify } from '../contexts/NotifyContext'
import { Link } from 'react-router-dom'
import { useMessaging } from '../contexts/MessagingContext'
import { MessageCircle } from 'lucide-react'
import '../styles/CandidateDashboard.css'

function CandidateDashboard() {
  const { user } = useAuth()
  const { openChat } = useMessaging()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  })
  const [fileToUpload, setFileToUpload] = useState(null)
  const [resumeStats, setResumeStats] = useState(null)
  const [existingCandidateId, setExistingCandidateId] = useState(null)
  const [existingResumePath, setExistingResumePath] = useState(null)

  // Fetch recruiter selection stats
  const { data: selectionData } = useQuery(
    ['selection-stats', user?.email],
    () => getSelectionStats().then(r => r.data),
    { enabled: !!user, staleTime: 60000 }
  )

  // Pre-populate form with user data from signup
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || ''
      })
    }
  }, [user])

  // Fetch existing candidate profile
  useQuery(
    ['candidate', user?.email],
    () => getCandidates({ email: user?.email }),
    {
      enabled: !!user?.email,
      onSuccess: (data) => {
        console.log('Candidate query response:', data)
        if (data.data && data.data.length > 0) {
          const candidate = data.data[0]
          console.log('Found existing candidate:', candidate.id)
          setExistingCandidateId(candidate.id)
          setExistingResumePath(candidate.resume_file_path)
          setFormData({
            name: candidate.name,
            email: candidate.email,
            phone: candidate.phone || ''
          })

          // If candidate has existing skills data, set stats
          if (candidate.skills) {
            let skillsList = []
            let categorized = null

            if (Array.isArray(candidate.skills)) {
              skillsList = candidate.skills
            } else if (typeof candidate.skills === 'object') {
              categorized = candidate.skills
              // Flatten for totals
              skillsList = Object.values(candidate.skills).flat()
            }

            setResumeStats({
              skills: skillsList,
              skills_extracted: skillsList.length,
              skills_by_category: categorized
            })
          } else if (candidate.resume_file_path) {
            // If resume exists but no skills, set empty stats
            setResumeStats({
              skills: [],
              skills_extracted: 0,
              skills_by_category: null
            })
          }
        } else {
          console.log('No existing candidate found for:', user?.email)
        }
      },
      onError: (error) => {
        console.error('Error fetching candidate:', error)
      }
    }
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFileToUpload(acceptedFiles[0])
      }
    }
  })

  const createCandidateMutation = useMutation(createCandidate)

  const updateCandidateMutation = useMutation(
    ({ id, data }) => updateCandidate(id, data)
  )



  const uploadResumeMutation = useMutation(
    ({ candidateId, file }) => {
      const formData = new FormData()
      formData.append('file', file)
      return uploadAndAnalyzeResume(candidateId, formData)
    },
    {
      onSuccess: (data) => {
        const stats = data.data
        setResumeStats(stats)

        if (stats.warning) {
          warning('Warning: ' + stats.warning)
        } else if (stats.debug_text_len === 0) {
          warning('Warning: No text could be extracted from your resume. Is it a scanned image? Please try uploading a text-based PDF or DOCX.')
        } else if (stats.skills_extracted === 0) {
          warning('Resume uploaded and analyzed, but no specific skills were found. Text length: ' + stats.debug_text_len + ' chars.')
        } else {
          success('Resume uploaded and analyzed successfully! ' + stats.skills_extracted + ' skills found.')
        }
      },
      onError: (error) => {
        console.error('Resume processing error:', error)
        const errorMsg = error.response?.data?.detail
          || error.response?.data?.message
          || error.message
          || JSON.stringify(error)
        notifyError('Error processing resume: ' + errorMsg)
      }
    }
  )

  const reAnalyzeMutation = useMutation(
    ({ candidateId, filePath }) => processResume(candidateId, filePath),
    {
      onSuccess: (data) => {
        const stats = data.data
        setResumeStats(stats)
        success('Resume re-analyzed successfully! Found ' + stats.skills_extracted + ' skills.')
      },
      onError: (error) => {
        console.error('Re-analysis error:', error)
        notifyError('Error re-analyzing resume: ' + (error.response?.data?.detail || error.message))
      }
    }
  )

  const handleReAnalyze = () => {
    if (existingCandidateId && existingResumePath) {
      reAnalyzeMutation.mutate({
        candidateId: existingCandidateId,
        filePath: existingResumePath
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      let candidateId = existingCandidateId

      // Step 1: Create or update candidate profile
      if (existingCandidateId) {
        console.log('Updating existing candidate:', existingCandidateId)
        const { email, ...updateData } = formData
        await updateCandidateMutation.mutateAsync({ id: existingCandidateId, data: updateData })
      } else {
        console.log('Creating new candidate')
        try {
          const result = await createCandidateMutation.mutateAsync(formData)
          candidateId = result.id
          setExistingCandidateId(result.id)
        } catch (error) {
          // If candidate already exists, try to get its ID
          if (error.response?.data?.detail?.includes('already exists')) {
            console.log('Candidate already exists, fetching existing profile...')
            const response = await getCandidates({ email: formData.email })
            if (response.data && response.data.length > 0) {
              candidateId = response.data[0].id
              setExistingCandidateId(candidateId)
            } else {
              throw new Error('Could not find existing profile even though server says it exists.')
            }
          } else {
            throw error
          }
        }
      }

      // Step 2: Upload and Process resume if selected
      if (fileToUpload && candidateId) {
        console.log('Uploading and processing resume for candidate:', candidateId)
        uploadResumeMutation.mutate({
          candidateId: candidateId,
          file: fileToUpload
        })
      } else if (!existingCandidateId) {
        success('Profile created successfully!')
      } else {
        success('Profile updated successfully!')
      }
    } catch (error) {
      console.error('Submit error:', error)
      const errorMsg = error.response?.data?.detail || error.message
      notifyError('Error: ' + errorMsg)
    }
  }

  return (
    <div className="candidate-dashboard page-container">
      <div className="dashboard-header">
        <h1>Candidate Dashboard</h1>
        <p>Create your profile and upload your resume to get matched with job opportunities</p>
      </div>

      {/* CANDIDATE ID CARD */}
      {user && (
        <div className="candidate-id-card">
          <div className="id-card-header">
            <div className="id-card-header-info">
              <h2>Profile Identity</h2>
              <p className="id-card-subtitle">Verified credentials and personalized matching info</p>
            </div>
            <div className="id-card-badge">Candidate</div>
          </div>

          <div className="id-card-grid">
            <div className="id-card-col">
              <div className="id-card-section id-highlight">
                <label>Candidate ID</label>
                <div className="candidate-id-display">
                  <span className="id-value">{user.id}</span>
                  <button
                    className="btn-copy"
                    onClick={() => {
                      navigator.clipboard.writeText(user.id)
                      success('Candidate ID copied to clipboard!')
                    }}
                  >
                    📋 Copy
                  </button>
                </div>
                <p className="id-description">Unique identifier for job applications</p>


              </div>
            </div>

            <div className="id-card-col">
              <div className="id-card-section match-highlight">
                <label>Matches</label>
                <Link to="/matches" className="btn-matches">
                  🚀 Go to Matches
                </Link>
                <p className="id-description">AI-powered job recommendations</p>
              </div>
            </div>

            <div className="id-card-col">
              <div className="id-card-section info-highlight">
                <label>Account</label>
                <div className="user-info">
                  <div className="info-row">
                    <span className="info-label">Name</span>
                    <input 
                      type="text"
                      className="info-data editable-name"
                      value={formData.name || user.full_name || ''}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      onBlur={handleSubmit}
                      placeholder="Click to Edit Name..."
                      title="Click to edit your name. It will auto-save."
                      style={{ 
                        background: 'transparent', 
                        border: 'none', 
                        color: 'inherit',
                        fontWeight: 'inherit',
                        fontSize: 'inherit',
                        fontFamily: 'inherit',
                        padding: '0',
                        margin: '0',
                        outline: 'none',
                        width: '100%',
                        cursor: 'text',
                        borderBottom: '1px dashed rgba(255,255,255,0.3)'
                      }}
                    />
                  </div>
                  <div className="info-row">
                    <span className="info-label">Email</span>
                    <span className="info-data">{user.email}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Role</span>
                    <span className="info-data role-tag">Job Seeker</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recruiter Activity table (full view below) */}
      {user && selectionData?.recent_activity?.length > 0 && (
        <div className="selection-stats-panel">
          <div className="selection-stats-header">
            <h2>Recruiter Activity</h2>
            <p>Jobs you've been matched or applied to since joining the platform</p>
          </div>

          <div className="selection-counters">
            <div className="sel-counter sel-total">
              <span className="sel-num">{selectionData.total_matches}</span>
              <span className="sel-label">Total Matches</span>
            </div>
            <div className="sel-counter sel-applied">
              <span className="sel-num">{selectionData.total_applied}</span>
              <span className="sel-label">Applied Jobs</span>
            </div>
            <div className="sel-counter sel-shortlisted">
              <span className="sel-num">{selectionData.shortlisted}</span>
              <span className="sel-label">Shortlisted</span>
            </div>
            <div className="sel-counter sel-selected">
              <span className="sel-num">{selectionData.selected}</span>
              <span className="sel-label">Selected</span>
            </div>
          </div>

          <div className="sel-activity-table">
            <div className="sel-table-head">
              <span>Job Title</span>
              <span>Company</span>
              <span>Match Score</span>
              <span>Status</span>
              <span>Date</span>
            </div>
            {selectionData.recent_activity.map(item => (
              <div key={item.match_id} className="sel-table-row">
                <span className="sel-job-title">{item.job_title}</span>
                <span className="sel-company">{item.company}</span>
                <span className="sel-score">
                  <span className="score-pill">{item.match_score}%</span>
                </span>
                <span>
                  <span className={`sel-status-badge sel-status-${item.status}`}>
                    {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                  </span>
                </span>
                <span className="sel-date">{item.date}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="dashboard-content">
        <form onSubmit={handleSubmit} className="candidate-form">
          <div className="form-section">
            <h3 className="form-section-title">Personal Information</h3>

            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                placeholder="your.email@example.com"
              />
            </div>

            <div className="form-group">
              <label>Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          <div className="form-section">
            <h3 className="form-section-title">Resume Upload</h3>

            <div className="form-group">
              <label>Upload Resume (PDF or DOCX)</label>
              <div {...getRootProps()} className="dropzone">
                <input {...getInputProps()} />
                {isDragActive ? (
                  <p>Drop the file here...</p>
                ) : (
                  <p>📄 Drag & drop a resume file here, or click to select</p>
                )}
              </div>
              {fileToUpload && (
                <p className="upload-success">File selected: {fileToUpload.name}</p>
              )}

              {!fileToUpload && existingResumePath && (
                <div style={{ marginTop: '1rem' }}>
                  <p className="upload-info">Current resume stored. Would you like to re-analyze it?</p>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={handleReAnalyze}
                    disabled={reAnalyzeMutation.isLoading}
                    style={{ marginTop: '0.5rem' }}
                  >
                    {reAnalyzeMutation.isLoading ? 'Analyzing...' : '🔄 Re-analyze Stored Resume'}
                  </button>
                </div>
              )}
            </div>
          </div>

          <button 
            type="submit" 
            className="btn-primary" 
            disabled={createCandidateMutation.isLoading || updateCandidateMutation.isLoading || uploadResumeMutation.isLoading}
          >
            {createCandidateMutation.isLoading || updateCandidateMutation.isLoading || uploadResumeMutation.isLoading
              ? (uploadResumeMutation.isLoading ? 'AI Analyzing Resume...' : 'Processing...')
              : existingCandidateId ? 'Update Profile' : 'Create Profile'}
          </button>
          
          {uploadResumeMutation.isLoading && (
            <p className="loading-hint" style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              💡 AI analysis can take up to 1-2 minutes for complex resumes. Please don't refresh.
            </p>
          )}
        </form>

        <div className="dashboard-stats">
          <div className="stat-card analysis-card">
            {resumeStats ? (
              <div className="analysis-container">
                <div className="analysis-header">
                  <div className="analysis-header-top">
                    <h3>📊 Resume Analysis</h3>
                    <div className="stat-value">{resumeStats.skills_extracted} Skills</div>
                  </div>
                  <p className="analysis-subtitle">
                    Extracted across 5 key categories from your parsed resume
                  </p>
                </div>

                <div className="analysis-body">
                  {/* Categorized Skills Display */}
                  {resumeStats.skills_by_category && (
                    <div className="skills-categorized">
                    {Object.entries(resumeStats.skills_by_category).map(([category, skills]) => (
                      skills.length > 0 && (
                        <div key={category} className="skill-category-section" style={{ marginBottom: '1.2rem' }}>
                          <h4 style={{
                            fontSize: '0.85rem',
                            fontWeight: '600',
                            marginBottom: '0.5rem',
                            color: 'var(--text-primary)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span style={{
                              fontSize: '1.1rem',
                            }}>
                              {category === 'Technical' && '💻'}
                              {category === 'Software & Tools' && '🛠️'}
                              {category === 'Leadership & Management' && '👔'}
                              {category === 'Communication & Interpersonal' && '🤝'}
                              {category === 'Industry Knowledge' && '📚'}
                            </span>
                            {category}
                            <span style={{
                              fontSize: '0.75rem',
                              color: 'var(--text-secondary)',
                              fontWeight: 'normal'
                            }}>
                              ({skills.length})
                            </span>
                          </h4>
                          <div className="skill-tags-category" style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0.4rem'
                          }}>
                            {skills.slice(0, 8).map(skill => (
                              <span
                                key={skill}
                                style={{
                                  background: category === 'Technical' ? 'rgba(102,126,234,0.1)' :
                                    category === 'Software & Tools' ? 'rgba(76,175,80,0.1)' :
                                      category === 'Leadership & Management' ? 'rgba(255,152,0,0.1)' :
                                        category === 'Communication & Interpersonal' ? 'rgba(233,30,99,0.1)' :
                                          'rgba(156,39,176,0.1)',
                                  border: '1px solid var(--border-color)',
                                  padding: '3px 10px',
                                  borderRadius: '12px',
                                  fontSize: '0.75rem',
                                  fontWeight: '600',
                                  color: 'var(--text-primary)'
                                }}
                              >
                                {skill}
                              </span>
                            ))}
                            {skills.length > 8 && (
                              <span style={{
                                background: 'var(--bg-hover)',
                                padding: '3px 10px',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                color: 'var(--text-secondary)',
                                border: '1px solid var(--border-color)'
                              }}>
                                +{skills.length - 8} more
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <>
                <h3>Get Started</h3>
                <div className="stat-value">3 Steps</div>
                <p style={{ marginTop: '1rem', opacity: 0.9, fontSize: '0.9rem' }}>
                  Complete your profile to start matching
                </p>
              </>
            )}
          </div>

          <div className="info-card">
            <h4>💡 Tips for Better Matches</h4>
            <p>Make sure your resume is up-to-date and includes all relevant skills and experience. The more detailed your resume, the better our AI can match you with opportunities.</p>
          </div>

          <div className="info-card">
            <h4>🔒 Privacy & Security</h4>
            <p>Your resume and personal information are encrypted and secure. We only share your profile with potential employers after you apply.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CandidateDashboard
