import { useState, useEffect } from 'react'
import { getShortlists, createShortlist, getShortlistCandidates, deleteShortlist, removeFromShortlist } from '../services/api'
import { Users, Plus, Trash2, ChevronDown, ChevronUp, UserMinus } from 'lucide-react'

export default function ShortlistManager() {
  const [shortlists, setShortlists] = useState([])
  const [expanded, setExpanded] = useState(null)
  const [candidates, setCandidates] = useState({})
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchShortlists()
  }, [])

  const fetchShortlists = async () => {
    try {
      const res = await getShortlists()
      setShortlists(res.data)
    } catch (err) {
      console.error('Failed to load shortlists:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!newName.trim()) return
    try {
      await createShortlist({ name: newName.trim() })
      setNewName('')
      setShowCreate(false)
      fetchShortlists()
    } catch (err) {
      console.error('Failed to create shortlist:', err)
    }
  }

  const toggleExpand = async (id) => {
    if (expanded === id) {
      setExpanded(null)
      return
    }
    setExpanded(id)
    if (!candidates[id]) {
      try {
        const res = await getShortlistCandidates(id)
        setCandidates(prev => ({ ...prev, [id]: res.data }))
      } catch (err) {
        console.error('Failed to load candidates:', err)
      }
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this shortlist?')) return
    try {
      await deleteShortlist(id)
      fetchShortlists()
    } catch (err) {
      console.error('Failed to delete shortlist:', err)
    }
  }

  const handleRemoveCandidate = async (shortlistId, candidateId) => {
    try {
      await removeFromShortlist(shortlistId, candidateId)
      setCandidates(prev => ({
        ...prev,
        [shortlistId]: prev[shortlistId].filter(c => c.candidate_id !== candidateId)
      }))
      fetchShortlists()
    } catch (err) {
      console.error('Failed to remove candidate:', err)
    }
  }

  if (loading) {
    return <div className="shortlist-loading"><div className="pulse-loader"></div></div>
  }

  return (
    <div className="shortlist-manager">
      <div className="sl-header">
        <h3><Users size={20} /> Candidate Shortlists</h3>
        <button className="btn-sm btn-primary" onClick={() => setShowCreate(!showCreate)}>
          <Plus size={14} /> New List
        </button>
      </div>

      {showCreate && (
        <div className="sl-create-form">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Shortlist name..."
            onKeyPress={(e) => e.key === 'Enter' && handleCreate()}
          />
          <button className="btn-sm btn-primary" onClick={handleCreate}>Create</button>
        </div>
      )}

      {shortlists.length === 0 ? (
        <div className="empty-state">
          <Users size={36} strokeWidth={1} />
          <p>No shortlists yet. Create one to organize candidates.</p>
        </div>
      ) : (
        <div className="sl-list">
          {shortlists.map(sl => (
            <div key={sl.id} className="sl-item">
              <div className="sl-item-header" onClick={() => toggleExpand(sl.id)}>
                <div className="sl-item-info">
                  <span className="sl-name">{sl.name}</span>
                  <span className="sl-count">{sl.candidate_count} candidates</span>
                </div>
                <div className="sl-item-actions">
                  <button className="btn-icon" onClick={(e) => { e.stopPropagation(); handleDelete(sl.id) }}>
                    <Trash2 size={14} />
                  </button>
                  {expanded === sl.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>

              {expanded === sl.id && (
                <div className="sl-candidates">
                  {(candidates[sl.id] || []).length === 0 ? (
                    <p className="sl-empty">No candidates in this list yet</p>
                  ) : (
                    candidates[sl.id].map(c => (
                      <div key={c.candidate_id} className="sl-candidate">
                        <div className="sl-cand-info">
                          <strong>{c.candidate_name}</strong>
                          <span>{c.candidate_email}</span>
                          {c.experience_years && <span>{c.experience_years} yrs exp</span>}
                        </div>
                        <button
                          className="btn-icon btn-danger"
                          onClick={() => handleRemoveCandidate(sl.id, c.candidate_id)}
                          title="Remove from shortlist"
                        >
                          <UserMinus size={14} />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
