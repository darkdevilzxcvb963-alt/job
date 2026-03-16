import React from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { updateMatchStatus } from '../services/api';
import './ATSPipeline.css';

const COLUMNS = [
    { id: 'applied', label: 'Applied' },
    { id: 'screened', label: 'Screened' },
    { id: 'interview', label: 'Interview' },
    { id: 'offered', label: 'Offered' },
    { id: 'hired', label: 'Hired' },
    { id: 'rejected', label: 'Rejected' },
];

const ATSPipeline = ({ matches, onStatusUpdate }) => {
    const queryClient = useQueryClient();

    const mutation = useMutation(
        ({ matchId, status, jobId }) => updateMatchStatus(matchId, status),
        {
            onSuccess: (_, variables) => {
                queryClient.invalidateQueries(['recruiterJobs']);
                if (onStatusUpdate) {
                    onStatusUpdate(variables.matchId, variables.jobId, variables.status);
                }
            }
        }
    );

    const handleStatusChange = (matchId, jobId, newStatus) => {
        mutation.mutate({ matchId, status: newStatus, jobId });
    };

    const getMatchesByStatus = (status) => {
        return matches.filter(m => m.status === status);
    };

    return (
        <div className="ats-pipeline">
            <div className="pipeline-grid">
                {COLUMNS.map(col => (
                    <div key={col.id} className={`pipeline-column col-${col.id}`}>
                        <div className="column-header">
                            <h3>{col.label}</h3>
                            <span className="count-badge">{getMatchesByStatus(col.id).length}</span>
                        </div>
                        <div className="column-content">
                            {getMatchesByStatus(col.id).map(match => (
                                <div key={match.id} className="pipeline-card">
                                    <div className="card-info">
                                        <h4>{match.candidate_name}</h4>
                                        <p>{match.job_title}</p>
                                        <div className="score-tag">{(match.overall_score * 100).toFixed(0)}% Match</div>
                                        <div className="pipeline-type-badge" style={{ marginTop: '0.4rem' }}>
                                            {match.match_explanation && match.semantic_similarity && match.semantic_similarity > 0 ? (
                                                <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8', borderRadius: '4px', fontWeight: 700, border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                                                    ✨ AI
                                                </span>
                                            ) : (
                                                <span style={{ fontSize: '0.65rem', padding: '2px 6px', background: 'rgba(244, 114, 182, 0.1)', color: '#f472b6', borderRadius: '4px', fontWeight: 700, border: '1px solid rgba(244, 114, 182, 0.2)' }}>
                                                    👤 Manual
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="card-actions">
                                        <select
                                            value={match.status}
                                            onChange={(e) => handleStatusChange(match.id, match.job_id, e.target.value)}
                                        >
                                            {COLUMNS.map(c => (
                                                <option key={c.id} value={c.id}>{c.label}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                            ))}
                            {getMatchesByStatus(col.id).length === 0 && (
                                <div className="empty-column-hint">Empty</div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ATSPipeline;
