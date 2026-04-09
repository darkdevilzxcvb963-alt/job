import React, { useState } from 'react';
import { X, Calendar, Clock, Video, MapPin, Loader2 } from 'lucide-react';
import { scheduleInterview } from '../services/api';

const ScheduleInterviewModal = ({ isOpen, onClose, candidate, application_id, onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        scheduled_at: '',
        duration_minutes: 60,
        interview_type: 'technical',
        location_or_link: ''
    });

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await scheduleInterview({
                application_id,
                candidate_id: candidate.id,
                ...formData
            });
            if (onSuccess) onSuccess();
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to schedule interview. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    return (
        <div className="modal-overlay">
            <div className="premium-modal interview-modal">
                <div className="modal-header">
                    <div className="header-content">
                        <Calendar className="header-icon" />
                        <h2>Schedule Interview</h2>
                    </div>
                    <button className="close-btn" onClick={onClose}><X size={20} /></button>
                </div>

                <form onSubmit={handleSubmit} className="modal-body">
                    <div className="candidate-summary-small">
                        <p>Scheduling for: <strong>{candidate.name}</strong></p>
                    </div>

                    <div className="form-grid">
                        <div className="form-group">
                            <label><Calendar size={14} /> Date & Time</label>
                            <input
                                type="datetime-local"
                                name="scheduled_at"
                                value={formData.scheduled_at}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label><Clock size={14} /> Duration (min)</label>
                            <input
                                type="number"
                                name="duration_minutes"
                                value={formData.duration_minutes}
                                onChange={handleChange}
                                min="15"
                                max="240"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Interview Type</label>
                            <select name="interview_type" value={formData.interview_type} onChange={handleChange}>
                                <option value="phone_screen">Phone Screen</option>
                                <option value="technical">Technical Interview</option>
                                <option value="behavioral">Behavioral Interview</option>
                                <option value="onsite">On-site Visit</option>
                                <option value="panel">Panel Interview</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label><Video size={14} /> Meeting Link / Location</label>
                            <input
                                type="text"
                                name="location_or_link"
                                value={formData.location_or_link}
                                onChange={handleChange}
                                placeholder="Zoom link or Office address"
                                required
                            />
                        </div>
                    </div>

                    {error && <div className="error-message-box">{error}</div>}

                    <div className="modal-footer">
                        <button type="button" className="btn-cancel" onClick={onClose} disabled={loading}>Cancel</button>
                        <button type="submit" className="btn-schedule-action" disabled={loading}>
                            {loading ? <><Loader2 className="animate-spin" size={16} /> Scheduling...</> : 'Confirm Schedule'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ScheduleInterviewModal;
