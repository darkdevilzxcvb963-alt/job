import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Eye, X, Shield, User, Mail, Phone, MapPin, Calendar, Clock, Check, Ban, Key, Trash2,
  FileText, Briefcase, BookOpen
} from 'lucide-react';
import {
  adminResetPassword,
  listUsers,
  verifyUser as apiVerifyUser,
  rejectUser as apiRejectUser,
  deleteUser as apiDeleteUser,
  getAdminStats,
  getUserDetails
} from '../services/api';
import { useNotify } from '../contexts/NotifyContext';
import '../styles/AdminDashboard.css';
import '../styles/AdminModal.css';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { success, error: notifyError, confirm, prompt, warning } = useNotify();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);

  // Unified Users State
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState('all'); // 'all', 'job_seeker', 'recruiter'
  const [message, setMessage] = useState('');
  const [selectedUser, setSelectedUser] = useState(null); // For detail modal
  const [isClosing, setIsClosing] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const [hasFetchedUsers, setHasFetchedUsers] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    if (activeTab === 'overview') {
      fetchStats();
    }
  }, [activeTab]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await getAdminStats();
      setStats(response.data);
    } catch (error) {
      setMessage('Failed to load statistics: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = { skip: 0, limit: 50 };
      if (filterRole !== 'all') params.role = filterRole;
      if (searchQuery) params.search = searchQuery;

      const response = await listUsers(params);
      setUsers(response.data);
      setHasFetchedUsers(true);
    } catch (error) {
      setMessage('Failed to load users: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
    setLoading(false);
  };

  const handleViewUser = async (user) => {
    setSelectedUser(user); // Show basic info immediately
    setDetailsLoading(true);
    try {
      const response = await getUserDetails(user.id);
      setSelectedUser(response.data); // Update with full details (resume, etc.)
    } catch (error) {
      console.error("Failed to fetch user details:", error);
      // Keep showing basic info if detail fetch fails
    }
    setDetailsLoading(false);
  };

  const verifyUser = async (userId) => {
    try {
      await apiVerifyUser(userId);
      setMessage('User verified successfully');
      if (activeTab === 'users') fetchUsers();
      // Update selected user if drawer is open
      if (selectedUser && selectedUser.id === userId) {
        setSelectedUser({ ...selectedUser, is_verified: true });
      }
    } catch (error) {
      setMessage('Failed to verify user: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
  };

  const rejectUser = async (userId) => {
    const reason = await prompt('Enter rejection reason:');
    if (!reason) return;

    try {
      await apiRejectUser(userId, reason);
      setMessage('User rejected successfully');
      success('User rejected successfully');
      if (activeTab === 'users') fetchUsers();
    } catch (error) {
      setMessage('Failed to reject user: ' + (error.response?.data?.detail || error.message));
      notifyError('Failed to reject user: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
  };

  const handleDeleteUser = async (userId) => {
    const ok = await confirm('Are you sure you want to permanently delete this user? This action cannot be undone.');
    if (!ok) return;

    try {
      await apiDeleteUser(userId);
      setMessage('User deleted successfully');
      success('User deleted successfully');
      closeDetailModal();
      if (activeTab === 'users') fetchUsers();
    } catch (error) {
      setMessage('Failed to delete user: ' + (error.response?.data?.detail || error.message));
      notifyError('Failed to delete user: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
  };

  const handleAdminResetPassword = async (userId) => {
    const newPassword = await prompt('Enter new password for this user (min 8 chars):');
    if (!newPassword) return;
    if (newPassword.length < 8) {
      warning('Password must be at least 8 characters long');
      return;
    }

    try {
      await adminResetPassword(userId, newPassword);
      setMessage('User password reset successfully');
      success('User password reset successfully');
    } catch (error) {
      setMessage('Failed to reset user password: ' + (error.response?.data?.detail || error.message));
      notifyError('Failed to reset user password: ' + (error.response?.data?.detail || error.message));
      console.error(error);
    }
  };

  const handleSearch = () => {
    if (activeTab === 'users') fetchUsers();
  };

  const closeDetailModal = () => {
    setIsClosing(true);
    setTimeout(() => {
      setSelectedUser(null);
      setIsClosing(false);
    }, 300); // Match animation duration
  };

  return (
    <div className="admin-dashboard page-container">
      <div className="admin-header">
        <h1>🔐 Admin Dashboard</h1>
        <p>Manage users, verify recruiters, and monitor platform activity</p>
      </div>

      {message && (
        <div className="notification">
          <p>{message}</p>
          <button onClick={() => setMessage('')}>✕</button>
        </div>
      )}

      {/* User Detail Modal */}
      {selectedUser && (
        <div className={`modal-overlay ${isClosing ? 'closing' : ''}`} onClick={closeDetailModal}>
          <div
            className={`user-detail-modal ${isClosing ? 'closing' : ''}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div className="modal-title">
                <div className="modal-avatar">
                  {selectedUser.full_name ? selectedUser.full_name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div>
                  <h2>{selectedUser.full_name}</h2>
                  <span className="modal-id">ID: {selectedUser.id}</span>
                </div>
              </div>
              <button className="modal-close" onClick={closeDetailModal}>
                <X size={24} />
              </button>
            </div>

            <div className="modal-body-scroll">
              <div className="modal-grid">
                <div className="modal-column">
                  <h3>Contact Info</h3>
                  <div className="info-row">
                    <div className="info-icon"><Mail size={18} /></div>
                    <div className="info-text">
                      <label>Email Address</label>
                      <p>{selectedUser.email}</p>
                    </div>
                  </div>
                  <div className="info-row">
                    <div className="info-icon"><Phone size={18} /></div>
                    <div className="info-text">
                      <label>Phone Number</label>
                      <p>{selectedUser.phone || 'Not provided'}</p>
                    </div>
                  </div>
                  <div className="info-row">
                    <div className="info-icon"><MapPin size={18} /></div>
                    <div className="info-text">
                      <label>Location</label>
                      <p>{selectedUser.location || 'Not provided'}</p>
                    </div>
                  </div>
                </div>

                <div className="modal-column">
                  <h3>Account Status</h3>
                  <div className="info-row">
                    <div className="info-icon"><Shield size={18} /></div>
                    <div className="info-text">
                      <label>Role</label>
                      <p className="capitalize">{selectedUser.role.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <div className="status-grid-mini">
                    <div className={`status-pill ${selectedUser.is_active ? 'active' : 'inactive'}`}>
                      {selectedUser.is_active ? <Check size={14} /> : <Ban size={14} />}
                      <span>{selectedUser.is_active ? 'Active' : 'Inactive'}</span>
                    </div>
                    <div className={`status-pill ${selectedUser.is_verified ? 'verified' : 'unverified'}`}>
                      {selectedUser.is_verified ? <Check size={14} /> : <Shield size={14} />}
                      <span>{selectedUser.is_verified ? 'Verified' : 'Unverified'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="modal-grid timeline-section">
                <div className="info-row">
                  <div className="info-icon"><Calendar size={18} /></div>
                  <div className="info-text">
                    <label>Joined Date</label>
                    <p>{new Date(selectedUser.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="info-row">
                  <div className="info-icon"><Clock size={18} /></div>
                  <div className="info-text">
                    <label>Last Login</label>
                    <p>{selectedUser.last_login ? new Date(selectedUser.last_login).toLocaleDateString() : 'Never'}</p>
                  </div>
                </div>
              </div>

              {detailsLoading && (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                  <div className="loading-spinner-mini"></div>
                </div>
              )}

              {/* Resume Data Section */}
              {selectedUser.resume_data && (
                <div className="resume-data-section">
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px', color: '#4f46e5' }}>
                    <FileText size={20} /> AI Resume Insight
                  </h3>

                  {/* Simple AI Summary Only */}
                  {selectedUser.resume_data.summary ? (
                    <div className="resume-summary" style={{ backgroundColor: '#f5f7ff', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #4f46e5' }}>
                      <p style={{ fontSize: '1rem', lineHeight: '1.6', color: '#1e293b', margin: 0 }}>
                        {selectedUser.resume_data.summary}
                      </p>
                    </div>
                  ) : (
                    <p style={{ color: '#94a3b8', fontStyle: 'italic' }}>No AI analysis available for this resume yet.</p>
                  )}
                </div>
              )}

              {selectedUser.bio && (
                <div className="bio-section">
                  <label>Biography</label>
                  <p>{selectedUser.bio}</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-modal-action btn-delete" onClick={() => handleDeleteUser(selectedUser.id)}>
                <Trash2 size={16} /> Delete User
              </button>
              <div style={{ flex: 1 }}></div>
              {!selectedUser.is_verified && (
                <button className="btn-modal-action btn-verify-mini" onClick={() => verifyUser(selectedUser.id)}>
                  <Check size={16} /> Verify
                </button>
              )}
              <button className="btn-modal-action btn-pwd" onClick={() => handleAdminResetPassword(selectedUser.id)}>
                <Key size={16} /> Reset Password
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 Users
        </button>
      </div>

      <div className="admin-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-section">
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner" style={{ borderColor: '#e0e0e0', borderTopColor: '#667eea' }}></div>
                <p style={{ textAlign: 'center', marginTop: '10px', color: '#666' }}>Loading dashboard...</p>
              </div>
            ) : stats ? (
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Candidates</h3>
                  <p className="stat-value">{stats.total_candidates}</p>
                  <p className="stat-label">In Match Engine</p>
                </div>

                <div className="stat-card clickable" onClick={() => { setFilterRole('all'); setActiveTab('users'); fetchUsers(); }}>
                  <h3>Registered Users</h3>
                  <p className="stat-value">{stats.total_users}</p>
                  <div className="card-footer">
                    <span className="stat-label">Verified & Pending</span>
                    <button className="btn-card-view"><Eye size={14} /> View</button>
                  </div>
                </div>

                <div className="stat-card">
                  <h3>Active Users</h3>
                  <p className="stat-value">{stats.active_users}</p>
                  <p className="stat-label">Currently active</p>
                </div>

                <div className="stat-card clickable" onClick={() => { setFilterRole('job_seeker'); setActiveTab('users'); fetchUsers(); }}>
                  <h3>Job Seeker Accounts</h3>
                  <p className="stat-value">{stats.job_seekers}</p>
                  <div className="card-footer">
                    <span className="stat-label">Registered Candidates</span>
                    <button className="btn-card-view"><Eye size={14} /> View</button>
                  </div>
                </div>

                <div className="stat-card clickable" onClick={() => { setFilterRole('recruiter'); setActiveTab('users'); fetchUsers(); }}>
                  <h3>Recruiter Accounts</h3>
                  <p className="stat-value">{stats.recruiters}</p>
                  <div className="card-footer">
                    <span className="stat-label">Indiv. Recruiters</span>
                    <button className="btn-card-view"><Eye size={14} /> View</button>
                  </div>
                </div>
              </div>
            ) : (
              <p>No data available</p>
            )}
          </div>
        )}

        {/* Unified Users Tab */}
        {activeTab === 'users' && (
          <div className="users-section">
            <div className="filters">
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="role-select"
                style={{ padding: '10px', borderRadius: '6px', border: '1px solid #ddd', marginRight: '10px' }}
              >
                <option value="all">All Roles</option>
                <option value="job_seeker">Job Seeker</option>
                <option value="recruiter">Recruiter</option>
              </select>
              <button
                onClick={fetchUsers}
                className="btn-search"
              >
                🔍 Search
              </button>
            </div>

            {!hasFetchedUsers && !loading ? (
              <div className="load-more-container" style={{ textAlign: 'center', padding: '40px' }}>
                <p style={{ marginBottom: '20px', color: '#666' }}>Click below to load users</p>
                <button
                  onClick={fetchUsers}
                  className="btn-primary"
                  style={{ padding: '12px 24px', fontSize: '1.1rem' }}
                >
                  👁️ View Users
                </button>
              </div>
            ) : loading ? (
              <div className="loading-container">
                <div className="loading-spinner" style={{ borderColor: '#e0e0e0', borderTopColor: '#667eea' }}></div>
                <p style={{ textAlign: 'center', marginTop: '10px', color: '#666' }}>Loading users...</p>
              </div>
            ) : users.length === 0 ? (
              <div className="no-results">
                <p>No users found matching your criteria.</p>
              </div>
            ) : (
              <div className="users-table-container">
                <table className="users-table">
                  <thead>
                    <tr>
                      <th>S.No</th>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Verified</th>
                      <th>Active</th>
                      <th>Joined</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user, index) => (
                      <tr key={user.id}>
                        <td data-label="S.No">{index + 1}</td>
                        <td className="col-id" title={user.id} data-label="ID">{user.id}</td>
                        <td className="col-name" data-label="Name">{user.full_name}</td>
                        <td className="col-email" data-label="Email">{user.email}</td>
                        <td data-label="Role">
                          <span className={`role-badge ${user.role}`}>
                            {user.role === 'job_seeker' ? '👤 Job Seeker' :
                              user.role === 'recruiter' ? '🏢 Recruiter' :
                                user.role === 'admin' ? '🛡️ Admin' : user.role}
                          </span>
                        </td>
                        <td data-label="Verified">
                          <span className={`status-badge ${user.is_verified ? 'verified' : 'unverified'}`}>
                            {user.is_verified ? '✓ Yes' : '✗ No'}
                          </span>
                        </td>
                        <td data-label="Active">
                          <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                            {user.is_active ? '✓ Yes' : '✗ No'}
                          </span>
                        </td>
                        <td data-label="Joined">{new Date(user.created_at).toLocaleDateString()}</td>
                        <td className="actions" data-label="Actions">
                          <button
                            className="btn-admin-view"
                            onClick={() => handleViewUser(user)}
                            title="View details"
                          >
                            <Eye size={16} /> View
                          </button>
                          {!user.is_verified && (
                            <button
                              className="btn-verify"
                              onClick={() => verifyUser(user.id)}
                              title="Verify user"
                            >
                              ✓
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
