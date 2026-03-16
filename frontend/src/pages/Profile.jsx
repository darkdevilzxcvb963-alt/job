import React, { useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { changePassword, updateMe } from '../services/api';
import { Eye, EyeOff, Camera, Check, X, Edit2 } from 'lucide-react';
import '../styles/Profile.css';

const Profile = () => {
    const { user, refreshUser } = useAuth();
    const [editName, setEditName] = useState('');
    const [isEditingName, setIsEditingName] = useState(false);
    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: ''
    });
    const [showPassword, setShowPassword] = useState({
        current: false,
        new: false,
        confirm: false
    });
    const [profilePhoto, setProfilePhoto] = useState(null);
    const fileInputRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({ ...prev, [name]: value }));
    };

    const togglePassword = (field) => {
        setShowPassword(prev => ({ ...prev, [field]: !prev[field] }));
    };

    const handlePhotoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setProfilePhoto(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage({ type: '', text: '' });

        if (passwordData.new_password !== passwordData.confirm_password) {
            setMessage({ type: 'error', text: 'New passwords do not match' });
            return;
        }

        if (passwordData.new_password.length < 8) {
            setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
            return;
        }

        setLoading(true);
        try {
            await changePassword({
                current_password: passwordData.current_password,
                new_password: passwordData.new_password
            });
            setMessage({ type: 'success', text: 'Password changed successfully!' });
            setPasswordData({
                current_password: '',
                new_password: '',
                confirm_password: ''
            });
        } catch (error) {
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to change password'
            });
        }
        setLoading(false);
    };

    const handleSaveName = async () => {
        if (!editName.trim() || editName === user.full_name) {
            setIsEditingName(false);
            return;
        }

        setLoading(true);
        try {
            await updateMe({ full_name: editName.trim() });
            await refreshUser();
            setIsEditingName(false);
            setMessage({ type: 'success', text: 'Name updated successfully!' });
        } catch (error) {
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to update name'
            });
        }
        setLoading(false);
    };

    if (!user) return <div className="profile-container">Loading profile...</div>;

    return (
        <div className="profile-container page-container">
            <div className="profile-card">
                <div className="profile-header">
                    <div className="profile-avatar-container" onClick={() => fileInputRef.current?.click()}>
                        <div className="profile-avatar">
                            {profilePhoto ? (
                                <img src={profilePhoto} alt="Profile" className="profile-photo-img" />
                            ) : (
                                user.full_name?.charAt(0).toUpperCase() || 'U'
                            )}
                        </div>
                        <div className="profile-avatar-overlay">
                            <Camera size={24} />
                            <span>Edit Photo</span>
                        </div>
                        <input 
                            type="file" 
                            ref={fileInputRef} 
                            onChange={handlePhotoChange} 
                            accept="image/*" 
                            style={{ display: 'none' }} 
                        />
                    </div>
                    
                    {isEditingName ? (
                        <div className="name-edit-group">
                            <input 
                                type="text" 
                                value={editName} 
                                onChange={(e) => setEditName(e.target.value)}
                                className="name-edit-input"
                                autoFocus
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleSaveName();
                                    if (e.key === 'Escape') setIsEditingName(false);
                                }}
                            />
                            <div className="name-edit-actions">
                                <button onClick={handleSaveName} disabled={loading} className="btn-icon-save" title="Save">
                                    <Check size={18} />
                                </button>
                                <button onClick={() => setIsEditingName(false)} className="btn-icon-cancel" title="Cancel">
                                    <X size={18} />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="name-display-group" onClick={() => { setEditName(user.full_name); setIsEditingName(true); }}>
                            <h2>{user.full_name} <Edit2 size={16} className="edit-icon-inline" /></h2>
                            <span className="edit-hint">Click to edit name</span>
                        </div>
                    )}

                    <p className="user-email">{user.email}</p>
                    <span className={`role-badge ${user.role}`}>
                        {user.role === 'job_seeker' ? 'Candidate' : user.role === 'recruiter' ? 'Recruiter' : 'Admin'}
                    </span>
                </div>

                <div className="profile-details">
                    <h3>Account Information</h3>
                    <div className="info-grid">
                        <div className="info-item">
                            <label>User ID</label>
                            <div className="id-box">
                                <code>{user.id}</code>
                            </div>
                        </div>
                        <div className="info-item">
                            <label>Account Status</label>
                            <p className={user.is_verified ? 'status-ok' : 'status-warn'}>
                                {user.is_verified ? 'Verified ✓' : 'Email Pending Verification'}
                            </p>
                        </div>
                        <div className="info-item">
                            <label>Member Since</label>
                            <p>{new Date(user.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>
                </div>

                <div className="password-section">
                    <h3>Security - Change Password</h3>
                    {message.text && (
                        <div className={`message-banner ${message.type}`}>
                            {message.text}
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="password-form">
                        <div className="form-group password-group">
                            <label>Current Password</label>
                            <div className="password-input-wrapper">
                                <input
                                    type={showPassword.current ? "text" : "password"}
                                    name="current_password"
                                    value={passwordData.current_password}
                                    onChange={handleChange}
                                    required
                                    placeholder="••••••••"
                                />
                                <button type="button" className="password-toggle" onClick={() => togglePassword('current')}>
                                    {showPassword.current ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>
                        <div className="form-group password-group">
                            <label>New Password</label>
                            <div className="password-input-wrapper">
                                <input
                                    type={showPassword.new ? "text" : "password"}
                                    name="new_password"
                                    value={passwordData.new_password}
                                    onChange={handleChange}
                                    required
                                    placeholder="At least 8 characters"
                                />
                                <button type="button" className="password-toggle" onClick={() => togglePassword('new')}>
                                    {showPassword.new ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>
                        <div className="form-group password-group">
                            <label>Confirm New Password</label>
                            <div className="password-input-wrapper">
                                <input
                                    type={showPassword.confirm ? "text" : "password"}
                                    name="confirm_password"
                                    value={passwordData.confirm_password}
                                    onChange={handleChange}
                                    required
                                    placeholder="Repeat new password"
                                />
                                <button type="button" className="password-toggle" onClick={() => togglePassword('confirm')}>
                                    {showPassword.confirm ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>
                        <button type="submit" className="btn-save" disabled={loading}>
                            {loading ? 'Updating...' : 'Update Password'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Profile;
