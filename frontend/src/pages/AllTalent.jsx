import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCandidates } from '../services/api'
import { Users, Search, Mail, MapPin, ExternalLink, ArrowLeft } from 'lucide-react'
import '../styles/Analytics.css' // Reuse some styles

function AllTalent() {
  const navigate = useNavigate()
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchCandidates()
  }, [])

  const fetchCandidates = async () => {
    try {
      const response = await getCandidates({ limit: 100 })
      setCandidates(response.data)
    } catch (error) {
      console.error('Failed to fetch candidates:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredCandidates = (candidates || []).filter(c => 
    (c.name || '').toLowerCase().includes((search || '').toLowerCase()) || 
    (c.email || '').toLowerCase().includes((search || '').toLowerCase())
  )

  return (
    <div className="analytics-container page-container">
      <div className="analytics-header">
        <button className="back-btn" onClick={() => navigate('/analytics')}>
          <ArrowLeft size={18} /> Back
        </button>
        <div className="header-icon-box u-bg-blue">
          <Users size={32} />
        </div>
        <div className="header-text">
          <h1>Total Candidates</h1>
          <p>Browse all registered candidates in your recruitment pipeline.</p>
        </div>
      </div>

      <div className="search-bar-talent">
        <Search size={20} />
        <input 
          type="text" 
          placeholder="Search by name or email..." 
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="loading-state">Loading candidate pool...</div>
      ) : filteredCandidates.length === 0 ? (
        <div className="empty-state-talent">
          <Users size={48} className="empty-icon" />
          <h3>No candidates found</h3>
          <p>Try refining your search or add new candidates to your jobs.</p>
        </div>
      ) : (
        <div className="talent-grid">
          {filteredCandidates.map(candidate => (
            <div key={candidate.id} className="talent-card">
              <div className="talent-avatar">
                {(candidate.name || 'U').charAt(0).toUpperCase()}
              </div>
              <div className="talent-info">
                <h3>{candidate.name || 'Anonymous candidate'}</h3>
                <p className="talent-email"><Mail size={14} /> {candidate.email}</p>
                {candidate.location && (
                  <p className="talent-loc"><MapPin size={14} /> {candidate.location}</p>
                )}
                <div className="talent-skills">
                  {Object.values(candidate.skills || {}).flat().slice(0, 5).map(skill => (
                    <span key={skill} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>
              <button 
                className="view-matches-btn"
                onClick={() => navigate(`/matches?search=${candidate.name}`)}
              >
                View Matches <ExternalLink size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AllTalent
