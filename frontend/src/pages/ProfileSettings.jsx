import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotify } from '../contexts/NotifyContext';
import {
  changePassword, updateMe, uploadResume, uploadProfilePicture,
  getExperiences, addExperience, updateExperience, deleteExperience,
  getEducation, addEducation, updateEducation, deleteEducation,
  getProjects, addProject, updateProject, deleteProject,
  getCertifications, addCertification, updateCertification, deleteCertification,
  getJobPreferences, updateJobPreferences,
  getAISettings, updateAISettings,
  getNotificationPrefs, updateNotificationPrefs,
  getPrivacySettingsApi, updatePrivacySettingsApi,
  getProfileStrength, exportMyData, requestDataDeletion,
  enableMFA, disableMFA,
  getRecruiterProfile, updateRecruiterProfile
} from '../services/api';
import {
  User, Briefcase, Target, Brain, Bell, Shield, Settings, Camera,
  Eye, EyeOff, Check, X, Edit2, Plus, Trash2, ExternalLink,
  ChevronRight, Upload, Award, GraduationCap, FolderGit2,
  MapPin, IndianRupee, Clock, ToggleLeft, ToggleRight,
  Sun, Moon, Download, AlertTriangle, Zap
} from 'lucide-react';
import '../styles/ProfileSettings.css';

const TABS = [
  { id: 'account', label: 'Account', icon: User },
  { id: 'professional', label: 'Professional', icon: Briefcase, role: 'job_seeker' },
  { id: 'company', label: 'Company & Hiring', icon: Briefcase, role: 'recruiter' },
  { id: 'preferences', label: 'Job Preferences', icon: Target, role: 'job_seeker' },
  { id: 'ai', label: 'AI Settings', icon: Brain, role: 'job_seeker' },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'privacy', label: 'Privacy & Security', icon: Shield },
  { id: 'dashboard', label: 'Appearance', icon: Sun },
];

/* ══════════════════════════════════════════════════════════════════════════════
   PROFILE STRENGTH METER
══════════════════════════════════════════════════════════════════════════════ */
const ProfileStrengthMeter = ({ strength }) => {
  const pct = strength?.percentage || 0;
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;
  const color = pct >= 80 ? '#4ade80' : pct >= 50 ? '#fbbf24' : '#f87171';

  return (
    <div className="ps-strength-card">
      <div className="ps-strength-ring-wrap">
        <svg width="130" height="130" viewBox="0 0 130 130">
          <circle cx="65" cy="65" r={radius} fill="none" stroke="var(--glass-border)" strokeWidth="8" />
          <circle
            cx="65" cy="65" r={radius} fill="none" stroke={color} strokeWidth="8"
            strokeDasharray={circumference} strokeDashoffset={offset}
            strokeLinecap="round" transform="rotate(-90 65 65)"
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <span className="ps-strength-pct" style={{ color }}>{Math.round(pct)}%</span>
      </div>
      <h4>Profile Strength</h4>
      {strength?.suggestions?.length > 0 && (
        <ul className="ps-strength-tips">
          {strength.suggestions.slice(0, 3).map((s, i) => (
            <li key={i}><Zap size={14} /> {s}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

/* ══════════════════════════════════════════════════════════════════════════════
   INLINE CRUD LIST — reusable for Experience / Education / Projects / Certs
══════════════════════════════════════════════════════════════════════════════ */
const CrudList = ({ items, fields, onAdd, onUpdate, onDelete, title, icon: Icon }) => {
  const [editing, setEditing] = useState(null); // id or 'new'
  const [form, setForm] = useState({});

  const startAdd = () => { setForm({}); setEditing('new'); };
  const startEdit = (item) => { setForm({ ...item }); setEditing(item.id); };
  const cancel = () => { setEditing(null); setForm({}); };

  const save = async () => {
    if (editing === 'new') await onAdd(form);
    else await onUpdate(editing, form);
    cancel();
  };

  return (
    <div className="ps-crud-section">
      <div className="ps-crud-header">
        <h4><Icon size={18} /> {title}</h4>
        <button className="ps-btn-add" onClick={startAdd}><Plus size={16} /> Add</button>
      </div>

      {editing && (
        <div className="ps-crud-form glass-card">
          {fields.map(f => (
            <div key={f.key} className="ps-form-group">
              <label>{f.label}</label>
              {f.type === 'textarea' ? (
                <textarea
                  value={form[f.key] || ''}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  placeholder={f.placeholder || ''}
                  rows={3}
                />
              ) : f.type === 'chips' ? (
                <ChipsInput
                  value={form[f.key] || []}
                  onChange={val => setForm({ ...form, [f.key]: val })}
                  placeholder={f.placeholder || 'Type and press Enter'}
                />
              ) : (
                <input
                  type={f.type || 'text'}
                  value={form[f.key] || ''}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  placeholder={f.placeholder || ''}
                />
              )}
            </div>
          ))}
          <div className="ps-crud-actions">
            <button className="ps-btn-save" onClick={save}><Check size={16} /> Save</button>
            <button className="ps-btn-cancel" onClick={cancel}><X size={16} /> Cancel</button>
          </div>
        </div>
      )}

      {items.length === 0 && !editing && (
        <p className="ps-empty">No {title.toLowerCase()} added yet.</p>
      )}

      {items.map(item => (
        <div key={item.id} className="ps-crud-item glass-card">
          <div className="ps-crud-item-body">
            {fields.slice(0, 2).map(f => (
              <span key={f.key} className={`ps-crud-field ${f.key}`}>
                {Array.isArray(item[f.key]) ? item[f.key].join(', ') : (item[f.key] || '—')}
              </span>
            ))}
            {fields.length > 2 && (
              <span className="ps-crud-sub">
                {fields.slice(2, 4).map(f =>
                  item[f.key] ? (typeof item[f.key] === 'string' ? item[f.key] : '') : ''
                ).filter(Boolean).join(' · ')}
              </span>
            )}
          </div>
          <div className="ps-crud-item-actions">
            <button onClick={() => startEdit(item)} title="Edit"><Edit2 size={15} /></button>
            <button onClick={() => onDelete(item.id)} className="danger" title="Delete"><Trash2 size={15} /></button>
          </div>
        </div>
      ))}
    </div>
  );
};

/* ══════════════════════════════════════════════════════════════════════════════
   CHIPS INPUT — for skills / tech stack / tags
══════════════════════════════════════════════════════════════════════════════ */
const ChipsInput = ({ value = [], onChange, placeholder }) => {
  const [input, setInput] = useState('');
  const add = () => {
    const trimmed = input.trim();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setInput('');
  };
  return (
    <div className="ps-chips-input">
      <div className="ps-chips-list">
        {value.map((v, i) => (
          <span key={i} className="ps-chip">
            {v}
            <button onClick={() => onChange(value.filter((_, j) => j !== i))}><X size={12} /></button>
          </span>
        ))}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add(); } }}
        placeholder={placeholder}
      />
    </div>
  );
};

/* ══════════════════════════════════════════════════════════════════════════════
   TOGGLE SWITCH
══════════════════════════════════════════════════════════════════════════════ */
const Toggle = ({ checked, onChange, label }) => (
  <label className="ps-toggle-row">
    <span>{label}</span>
    <div className={`ps-toggle ${checked ? 'active' : ''}`} onClick={() => onChange(!checked)}>
      <div className="ps-toggle-thumb" />
    </div>
  </label>
);

/* ══════════════════════════════════════════════════════════════════════════════
   SLIDER with label
══════════════════════════════════════════════════════════════════════════════ */
const Slider = ({ label, value, onChange, min = 0, max = 100 }) => (
  <div className="ps-slider-group">
    <div className="ps-slider-header">
      <span>{label}</span>
      <span className="ps-slider-val">{value}%</span>
    </div>
    <input
      type="range" min={min} max={max} value={value}
      onChange={e => onChange(Number(e.target.value))}
      className="ps-slider"
    />
  </div>
);

/* ══════════════════════════════════════════════════════════════════════════════
   MAIN COMPONENT
══════════════════════════════════════════════════════════════════════════════ */
const ProfileSettings = () => {
  const { user, refreshUser } = useAuth();
  const { confirm } = useNotify();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('account');
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Data state
  const [strength, setStrength] = useState(null);
  const [experiences, setExperiences] = useState([]);
  const [education, setEducationList] = useState([]);
  const [projects, setProjectsList] = useState([]);
  const [certifications, setCertificationsList] = useState([]);
  const [jobPrefs, setJobPrefs] = useState({});
  const [aiSettings, setAiSettings] = useState({ matching_mode: 'balanced', skill_weight: 40, experience_weight: 35, education_weight: 25 });
  const [notifPrefs, setNotifPrefs] = useState({ email_jobs: true, email_messages: true, sms_alerts: false, push_notifications: true, frequency: 'instant' });
  const [privacyData, setPrivacyData] = useState({ profile_visibility: 'public', resume_visible: true, contact_visible: true, blocked_companies: [] });
  const [recruiterProfile, setRecruiterProfile] = useState({
    company_name: '', company_website: '', company_industry: '', company_size: '',
    job_title: '', roles_hiring_for: [], experience_range: '', 
    job_types: [], work_modes: [], default_skills: [], default_location: '', default_deadline: ''
  });

  // Account editing
  const [editName, setEditName] = useState('');
  const [editBio, setEditBio] = useState('');
  const [isEditingName, setIsEditingName] = useState(false);
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [passwordData, setPasswordData] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [showPassword, setShowPassword] = useState({ current: false, new: false, confirm: false });
  const fileInputRef = useRef(null);
  const [profilePhoto, setProfilePhoto] = useState(null);

  // Theme
  const [theme, setTheme] = useState(() => document.documentElement.getAttribute('data-theme') || 'dark');

  const flash = useCallback((type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 4000);
  }, []);

  // ── Load data ──────────────────────────────────────────────────────────────
  useEffect(() => {
    loadStrength();
    
    // Handle deep linking via query params
    const params = new URLSearchParams(location.search);
    const tabParam = params.get('tab');
    if (tabParam && TABS.some(t => t.id === tabParam)) {
      setActiveTab(tabParam);
    }
  }, [location.search]);

  useEffect(() => {
    if (activeTab === 'professional') {
      loadExperiences(); loadEducation(); loadProjects(); loadCertifications();
      loadJobPreferences(); // Needed for skills
    } else if (activeTab === 'preferences') {
      loadJobPreferences();
    } else if (activeTab === 'ai') {
      loadAISettings();
    } else if (activeTab === 'notifications') {
      loadNotifPrefs();
    } else if (activeTab === 'privacy') {
      loadPrivacy();
    } else if (activeTab === 'company') {
      loadRecruiterProfile();
    }
  }, [activeTab]);

  // Handle section scrolling
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const section = params.get('section');
    if (section) {
        setTimeout(() => {
            const el = document.getElementById(`section-${section}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
  }, [location.search, activeTab]);

  const loadStrength = async () => { try { const r = await getProfileStrength(); setStrength(r.data); } catch {} };
  const loadExperiences = async () => { try { const r = await getExperiences(); setExperiences(r.data); } catch {} };
  const loadEducation = async () => { try { const r = await getEducation(); setEducationList(r.data); } catch {} };
  const loadProjects = async () => { try { const r = await getProjects(); setProjectsList(r.data); } catch {} };
  const loadCertifications = async () => { try { const r = await getCertifications(); setCertificationsList(r.data); } catch {} };
  const loadJobPreferences = async () => { try { const r = await getJobPreferences(); setJobPrefs(r.data); } catch {} };
  const loadAISettings = async () => { try { const r = await getAISettings(); setAiSettings(r.data); } catch {} };
  const loadNotifPrefs = async () => { try { const r = await getNotificationPrefs(); setNotifPrefs(r.data); } catch {} };
  const loadPrivacy = async () => { try { const r = await getPrivacySettingsApi(); setPrivacyData(r.data); } catch {} };
  const loadRecruiterProfile = async () => { 
    try { 
      const r = await getRecruiterProfile(); 
      setRecruiterProfile({
        ...r.data,
        roles_hiring_for: r.data.roles_hiring_for || [],
        job_types: r.data.job_types || [],
        work_modes: r.data.work_modes || [],
        default_skills: r.data.default_skills || []
      }); 
    } catch {} 
  };

  // ── Account handlers ───────────────────────────────────────────────────────
  const handleSaveName = async () => {
    if ((!editName.trim() || editName === user.full_name) && 
        (editBio === (user.bio || ''))) { 
      setIsEditingName(false); 
      setIsEditingBio(false);
      return; 
    }
    setLoading(true);
    try {
      await updateMe({ 
        full_name: editName.trim(),
        bio: editBio.trim()
      });
      await refreshUser();
      setIsEditingName(false);
      setIsEditingBio(false);
      flash('success', 'Profile updated successfully!');
      loadStrength();
    } catch (e) {
      flash('error', e.response?.data?.detail || 'Failed to update profile');
    }
    setLoading(false);
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) { flash('error', 'Passwords do not match'); return; }
    if (passwordData.new_password.length < 8) { flash('error', 'Password must be at least 8 characters'); return; }
    setLoading(true);
    try {
      await changePassword({ current_password: passwordData.current_password, new_password: passwordData.new_password });
      flash('success', 'Password changed successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (e) {
      flash('error', e.response?.data?.detail || 'Failed to change password');
    }
    setLoading(false);
  };

  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await uploadProfilePicture(formData);
      const photoUrl = res.data.url;
      await updateMe({ profile_picture_url: photoUrl });
      await refreshUser();
      setProfilePhoto(photoUrl);
      flash('success', 'Profile photo updated!');
      loadStrength();
    } catch (e) {
      flash('error', e.response?.data?.detail || 'Photo upload failed');
    }
    setLoading(false);
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    setLoading(true);
    setUploadProgress(10);
    
    // Simulate progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 5;
      });
    }, 400);

    try {
      await uploadResume(formData);
      clearInterval(interval);
      setUploadProgress(100);
      
      setTimeout(() => {
        flash('success', 'Resume uploaded & processed!');
        loadStrength();
        setUploadProgress(0);
        setLoading(false);
      }, 500);
    } catch (e) {
      clearInterval(interval);
      setUploadProgress(0);
      setLoading(false);
      flash('error', e.response?.data?.detail || 'Upload failed');
    }
  };

  // ── Preferences handler ────────────────────────────────────────────────────
  const savePreferences = async () => {
    setLoading(true);
    try {
      const r = await updateJobPreferences(jobPrefs);
      setJobPrefs(r.data);
      flash('success', 'Preferences saved!');
      loadStrength();
    } catch (e) { flash('error', 'Failed to save preferences'); }
    setLoading(false);
  };

  // ── AI settings handler ────────────────────────────────────────────────────
  const saveAISettings = async () => {
    setLoading(true);
    try {
      const r = await updateAISettings(aiSettings);
      setAiSettings(r.data);
      flash('success', 'AI settings saved!');
    } catch (e) { flash('error', 'Failed to save AI settings'); }
    setLoading(false);
  };

  // ── Notification handler ───────────────────────────────────────────────────
  const saveNotifPrefs = async () => {
    setLoading(true);
    try {
      const r = await updateNotificationPrefs(notifPrefs);
      setNotifPrefs(r.data);
      flash('success', 'Notification settings saved!');
    } catch (e) { flash('error', 'Failed to save'); }
    setLoading(false);
  };

  // ── Privacy handler ────────────────────────────────────────────────────────
  const savePrivacy = async () => {
    setLoading(true);
    try {
      const r = await updatePrivacySettingsApi(privacyData);
      setPrivacyData(r.data);
      flash('success', 'Privacy settings saved!');
    } catch (e) { flash('error', 'Failed to save'); }
    setLoading(false);
  };

  const saveRecProfile = async () => {
    setLoading(true);
    try {
      const r = await updateRecruiterProfile(recruiterProfile);
      setRecruiterProfile({
        ...r.data,
        roles_hiring_for: r.data.roles_hiring_for || [],
        job_types: r.data.job_types || [],
        work_modes: r.data.work_modes || [],
        default_skills: r.data.default_skills || []
      });
      flash('success', 'Profile updated!');
    } catch (e) { 
      flash('error', e.response?.data?.detail || 'Failed to save'); 
    }
    setLoading(false);
  };

  const handleMfaToggle = async (enabled) => {
    setLoading(true);
    try {
      if (enabled) {
        await enableMFA();
        flash('success', 'Multi-Factor Authentication enabled!');
      } else {
        await disableMFA();
        flash('success', 'Multi-Factor Authentication disabled.');
      }
      await refreshUser();
    } catch (e) {
      flash('error', e.response?.data?.detail || 'Failed to update MFA settings');
    }
    setLoading(false);
  };

  // ── Theme ──────────────────────────────────────────────────────────────────
  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  };

  if (!user) return <div className="ps-container page-container">Loading...</div>;

  /* ════════ RENDER ════════ */
  return (
    <div className="ps-container page-container">
      {/* Sidebar */}
      <aside className="ps-sidebar glass-card">
        <ProfileStrengthMeter strength={strength} />
        <nav className="ps-nav">
          {TABS.filter(tab => !tab.role || tab.role === user.role).map(tab => (
            <button
              key={tab.id}
              className={`ps-nav-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={18} />
              <span>{tab.label}</span>
              <ChevronRight size={14} className="ps-nav-arrow" />
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="ps-main">
        {message.text && (
          <div className={`ps-flash ${message.type}`}>{message.text}</div>
        )}

        {/* ── ACCOUNT ────────────────────────────────────────────────── */}
        {activeTab === 'account' && (
          <section className="ps-section" id="settings-account">
            <h2>Account Settings</h2>

            <div className="ps-account-header glass-card">
              <div className="ps-avatar-container" onClick={() => fileInputRef.current?.click()}>
                <div className="ps-avatar">
                  {profilePhoto || user.profile_picture_url ? <img src={profilePhoto || user.profile_picture_url} alt="Profile" /> :
                    user.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="ps-avatar-overlay"><Camera size={22} /><span>Change</span></div>
                <input type="file" ref={fileInputRef} onChange={handlePhotoChange} accept="image/*" style={{ display: 'none' }} />
              </div>

              <div className="ps-account-info">
                {isEditingName ? (
                  <div className="ps-name-edit">
                    <input
                      type="text" value={editName}
                      onChange={e => setEditName(e.target.value)}
                      autoFocus
                      onKeyDown={e => { if (e.key === 'Enter') handleSaveName(); if (e.key === 'Escape') setIsEditingName(false); }}
                    />
                    <button className="ps-btn-icon save" onClick={handleSaveName}><Check size={16} /></button>
                    <button className="ps-btn-icon" onClick={() => setIsEditingName(false)}><X size={16} /></button>
                  </div>
                ) : (
                  <h3 onClick={() => { setEditName(user.full_name); setEditBio(user.bio || ''); setIsEditingName(true); }}>
                    {user.full_name} <Edit2 size={14} className="ps-edit-hint" />
                  </h3>
                )}
                <p className="ps-email">{user.email}</p>
                
                {isEditingBio ? (
                  <div className="ps-bio-edit" style={{ marginTop: '0.5rem' }}>
                    <textarea
                      value={editBio}
                      onChange={e => setEditBio(e.target.value)}
                      placeholder="Write a short bio..."
                      rows={3}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', color: 'white' }}
                      autoFocus
                    />
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                      <button className="ps-btn-save" onClick={handleSaveName}><Check size={14} /> Save Bio</button>
                      <button className="ps-btn-cancel" onClick={() => setIsEditingBio(false)}><X size={14} /> Cancel</button>
                    </div>
                  </div>
                ) : (
                  <p className="ps-bio" onClick={() => { setEditBio(user.bio || ''); setEditName(user.full_name); setIsEditingBio(true); }} style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', cursor: 'pointer', marginTop: '0.5rem' }}>
                    {user.bio || 'Add a bio to your profile...'} <Edit2 size={12} style={{ opacity: 0.5 }} />
                  </p>
                )}

                <span className={`ps-role-badge ${user.role}`} style={{ marginTop: '1rem' }}>
                  {user.role === 'job_seeker' ? 'Candidate' : user.role === 'recruiter' ? 'Recruiter' : 'Admin'}
                </span>
              </div>
            </div>

            <div className="ps-info-grid glass-card">
              <div className="ps-info-item">
                <label>User ID</label>
                <code>{user.id}</code>
              </div>
              <div className="ps-info-item">
                <label>Status</label>
                <span className={user.is_verified ? 'status-ok' : 'status-warn'}>
                  {user.is_verified ? '✓ Verified' : 'Pending Verification'}
                </span>
              </div>
              <div className="ps-info-item">
                <label>Member Since</label>
                <span>{new Date(user.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Password Change */}
            <div className="ps-password-section glass-card">
              <h3>Change Password</h3>
              <form onSubmit={handlePasswordSubmit}>
                {['current_password', 'new_password', 'confirm_password'].map(field => (
                  <div key={field} className="ps-form-group">
                    <label>{field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                    <div className="ps-pw-wrap">
                      <input
                        type={showPassword[field.split('_')[0]] ? 'text' : 'password'}
                        value={passwordData[field]}
                        onChange={e => setPasswordData({ ...passwordData, [field]: e.target.value })}
                        required placeholder="••••••••"
                      />
                      <button type="button" className="ps-pw-toggle"
                        onClick={() => setShowPassword({ ...showPassword, [field.split('_')[0]]: !showPassword[field.split('_')[0]] })}>
                        {showPassword[field.split('_')[0]] ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>
                ))}
                <button type="submit" className="ps-btn-primary" disabled={loading}>
                  {loading ? 'Updating…' : 'Update Password'}
                </button>
              </form>
            </div>
          </section>
        )}

        {/* ── PROFESSIONAL ───────────────────────────────────────────── */}
        {activeTab === 'professional' && (
          <section className="ps-section" id="settings-professional">
            <h2>Professional Profile</h2>

            {/* Resume upload */}
            <div className="ps-resume-upload glass-card">
              <h4><Upload size={18} /> Resume</h4>
              <p>Upload your resume (PDF/DOCX) for AI-powered skill extraction and matching.</p>
              <label className="ps-upload-btn" style={{ 
                opacity: loading ? 0.6 : 1, 
                pointerEvents: loading ? 'none' : 'auto',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'var(--primary-gradient)',
                color: '#fff',
                padding: '0.75rem 1.5rem',
                borderRadius: '12px',
                cursor: 'pointer',
                fontWeight: 600
              }}>
                <Upload size={16} /> {loading ? 'Analyzing...' : 'Upload Resume'}
                <input type="file" accept=".pdf,.docx,.doc" onChange={handleResumeUpload} style={{ display: 'none' }} />
              </label>

              {uploadProgress > 0 && (
                <div className="ps-upload-progress-container">
                  <div className="ps-progress-info">
                    <div className="ps-progress-label">
                      {uploadProgress < 100 ? <Brain className="animate-pulse" size={16} /> : <Check size={16} />}
                      <span>{uploadProgress < 100 ? 'AI is extracting skills...' : 'Analysis Complete'}</span>
                    </div>
                    <div className="ps-progress-pct">{uploadProgress}%</div>
                  </div>
                  <div className="ps-progress-bar">
                    <div className="ps-progress-fill" style={{ width: `${uploadProgress}%` }} />
                  </div>
                </div>
              )}
            </div>

            {/* Headline */}
            <div className="ps-headline-section glass-card" style={{ marginBottom: '1.5rem' }}>
              <h4><Briefcase size={18} /> Headline</h4>
              <p className="ps-hint">A short catchy title for your profile (e.g. 'Senior React Developer')</p>
              <input
                type="text"
                value={jobPrefs.headline || ''}
                onChange={e => setJobPrefs({ ...jobPrefs, headline: e.target.value })}
                placeholder="Ex: Full Stack Developer | Cloud enthusiast"
                style={{ width: '100%', marginBottom: '1rem' }}
              />
              <button className="ps-btn-primary" style={{ marginTop: 0 }} onClick={savePreferences}>Save Headline</button>
            </div>

            {/* Skills */}
            <div className="ps-skills-section glass-card" id="section-skills">
              <h4><Zap size={18} /> Skills</h4>
              <p className="ps-hint">List your technical expertise. At least 5 skills required for 100% completion.</p>
              <ChipsInput
                value={jobPrefs.skills || []}
                onChange={val => setJobPrefs({ ...jobPrefs, skills: val })}
                placeholder="Type a skill and press Enter"
              />
              <button className="ps-btn-primary" style={{ marginTop: '1rem' }} onClick={savePreferences}>Save Skills</button>
            </div>

            <div id="section-experience">
              <CrudList
                title="Experience" icon={Briefcase}
              items={experiences}
              fields={[
                { key: 'job_title', label: 'Job Title', placeholder: 'e.g. Software Engineer' },
                { key: 'company', label: 'Company', placeholder: 'e.g. Google' },
                { key: 'start_date', label: 'Start Date', placeholder: 'YYYY-MM' },
                { key: 'end_date', label: 'End Date', placeholder: 'YYYY-MM or present' },
                { key: 'description', label: 'Description', type: 'textarea', placeholder: 'Describe your role…' },
              ]}
              onAdd={async (data) => { try { await addExperience(data); loadExperiences(); loadStrength(); flash('success', 'Experience added!'); } catch { flash('error', 'Failed to add'); } }}
              onUpdate={async (id, data) => { try { await updateExperience(id, data); loadExperiences(); flash('success', 'Experience updated!'); } catch { flash('error', 'Failed to update'); } }}
              onDelete={async (id) => { try { await deleteExperience(id); loadExperiences(); loadStrength(); flash('success', 'Experience removed'); } catch { flash('error', 'Failed to remove'); } }}
            />
            </div>

            <div id="section-education">
              <CrudList
                title="Education" icon={GraduationCap}
              items={education}
              fields={[
                { key: 'degree', label: 'Degree', placeholder: 'e.g. B.Tech Computer Science' },
                { key: 'institution', label: 'Institution', placeholder: 'e.g. MIT' },
                { key: 'field_of_study', label: 'Field of Study', placeholder: 'e.g. Computer Science' },
                { key: 'end_year', label: 'Graduation Year', type: 'number', placeholder: '2024' },
              ]}
              onAdd={async (data) => { try { await addEducation(data); loadEducation(); loadStrength(); flash('success', 'Education added!'); } catch { flash('error', 'Failed to add'); } }}
              onUpdate={async (id, data) => { try { await updateEducation(id, data); loadEducation(); flash('success', 'Education updated!'); } catch { flash('error', 'Failed to update'); } }}
              onDelete={async (id) => { try { await deleteEducation(id); loadEducation(); loadStrength(); flash('success', 'Education removed'); } catch { flash('error', 'Failed to remove'); } }}
            />
            </div>

            <div id="section-projects">
              <CrudList
                title="Projects" icon={FolderGit2}
              items={projects}
              fields={[
                { key: 'title', label: 'Title', placeholder: 'e.g. E-Commerce Platform' },
                { key: 'description', label: 'Description', type: 'textarea', placeholder: 'What it does…' },
                { key: 'tech_stack', label: 'Tech Stack', type: 'chips', placeholder: 'Add technology' },
                { key: 'github_url', label: 'GitHub URL', placeholder: 'https://github.com/…' },
                { key: 'demo_url', label: 'Demo URL', placeholder: 'https://example.com' },
              ]}
              onAdd={async (data) => { try { await addProject(data); loadProjects(); loadStrength(); flash('success', 'Project added!'); } catch { flash('error', 'Failed to add'); } }}
              onUpdate={async (id, data) => { try { await updateProject(id, data); loadProjects(); flash('success', 'Project updated!'); } catch { flash('error', 'Failed to update'); } }}
              onDelete={async (id) => { try { await deleteProject(id); loadProjects(); loadStrength(); flash('success', 'Project removed'); } catch { flash('error', 'Failed to remove'); } }}
            />
            </div>

            <div id="section-certifications">
              <CrudList
                title="Certifications" icon={Award}
                items={certifications}
                fields={[
                  { key: 'name', label: 'Name', placeholder: 'e.g. AWS Solutions Architect' },
                  { key: 'provider', label: 'Provider', placeholder: 'e.g. Amazon Web Services' },
                  { key: 'issue_date', label: 'Issue Date', placeholder: 'YYYY-MM' },
                  { key: 'credential_url', label: 'Credential URL', placeholder: 'https://…' },
                ]}
                onAdd={async (data) => { await addCertification(data); loadCertifications(); }}
                onUpdate={async (id, data) => { await updateCertification(id, data); loadCertifications(); }}
                onDelete={async (id) => { await deleteCertification(id); loadCertifications(); }}
              />
            </div>
          </section>
        )}

        {/* ── COMPANY & HIRING (Recruiter Only) ─────────────────────── */}
        {activeTab === 'company' && (
          <section className="ps-section" id="settings-company">
            <h2>Company & Hiring Details</h2>
            
            <div className="ps-company-grid">
              <div className="glass-card ps-pref-card">
                <h4>Company Info</h4>
                <div className="ps-form-group">
                  <label>Company Name</label>
                  <input type="text" value={recruiterProfile.company_name || ''} 
                    onChange={e => setRecruiterProfile({ ...recruiterProfile, company_name: e.target.value })} />
                </div>
                <div className="ps-form-group">
                  <label>Website</label>
                  <input type="text" value={recruiterProfile.company_website || ''} 
                    onChange={e => setRecruiterProfile({ ...recruiterProfile, company_website: e.target.value })} />
                </div>
                <div className="ps-form-row">
                  <div className="ps-form-group">
                    <label>Industry</label>
                    <input type="text" value={recruiterProfile.company_industry || ''} 
                      onChange={e => setRecruiterProfile({ ...recruiterProfile, company_industry: e.target.value })} />
                  </div>
                  <div className="ps-form-group">
                    <label>Company Size</label>
                    <input type="text" value={recruiterProfile.company_size || ''} 
                      onChange={e => setRecruiterProfile({ ...recruiterProfile, company_size: e.target.value })} />
                  </div>
                </div>
              </div>

              <div className="glass-card ps-pref-card">
                <h4>Hiring Preferences</h4>
                <div className="ps-form-group">
                  <label>Roles Hiring For</label>
                  <ChipsInput value={recruiterProfile.roles_hiring_for} 
                    onChange={val => setRecruiterProfile({ ...recruiterProfile, roles_hiring_for: val })} placeholder="Add role" />
                </div>
                <div className="ps-form-group">
                  <label>Experience Range</label>
                  <select value={recruiterProfile.experience_range || ''} 
                    onChange={e => setRecruiterProfile({ ...recruiterProfile, experience_range: e.target.value })}>
                    <option value="">Select</option>
                    <option value="0-2 years">Entry (0-2 yrs)</option>
                    <option value="2-5 years">Mid (2-5 yrs)</option>
                    <option value="5-10 years">Senior (5-10 yrs)</option>
                    <option value="10+ years">Lead (10+ yrs)</option>
                  </select>
                </div>
                <div className="ps-form-group">
                  <label>Job Types</label>
                  <ChipsInput value={recruiterProfile.job_types} 
                    onChange={val => setRecruiterProfile({ ...recruiterProfile, job_types: val })} placeholder="e.g. Full-time" />
                </div>
                <div className="ps-form-group">
                  <label>Work Modes</label>
                  <ChipsInput value={recruiterProfile.work_modes} 
                    onChange={val => setRecruiterProfile({ ...recruiterProfile, work_modes: val })} placeholder="e.g. Remote" />
                </div>
              </div>

              <div className="glass-card ps-pref-card">
                <h4>Job Posting Defaults</h4>
                <div className="ps-form-group">
                  <label>Default Skills</label>
                  <ChipsInput value={recruiterProfile.default_skills} 
                    onChange={val => setRecruiterProfile({ ...recruiterProfile, default_skills: val })} placeholder="Add skill" />
                </div>
                <div className="ps-form-group">
                  <label>Default Location</label>
                  <input type="text" value={recruiterProfile.default_location || ''} 
                    onChange={e => setRecruiterProfile({ ...recruiterProfile, default_location: e.target.value })} />
                </div>
                <div className="ps-form-group">
                  <label>Default Deadline</label>
                  <input type="text" value={recruiterProfile.default_deadline || ''} 
                    onChange={e => setRecruiterProfile({ ...recruiterProfile, default_deadline: e.target.value })} 
                    placeholder="e.g. 30 days" />
                </div>
              </div>
            </div>

            <button className="ps-btn-primary" onClick={saveRecProfile} disabled={loading}>
              {loading ? 'Saving…' : 'Save Company Details'}
            </button>
          </section>
        )}

        {/* ── JOB PREFERENCES ────────────────────────────────────────── */}
        {activeTab === 'preferences' && (
          <section className="ps-section" id="settings-preferences">
            <h2>Job Preferences</h2>
            <div className="ps-prefs-grid">
              <div className="glass-card ps-pref-card">
                <h4><Target size={18} /> Preferred Roles</h4>
                <ChipsInput
                  value={jobPrefs.preferred_roles || []}
                  onChange={val => setJobPrefs({ ...jobPrefs, preferred_roles: val })}
                  placeholder="Add a role"
                />
              </div>

              <div className="glass-card ps-pref-card">
                <h4><MapPin size={18} /> Preferred Locations</h4>
                <ChipsInput
                  value={jobPrefs.preferred_locations || []}
                  onChange={val => setJobPrefs({ ...jobPrefs, preferred_locations: val })}
                  placeholder="Add a location"
                />
              </div>

              <div className="glass-card ps-pref-card">
                <h4><IndianRupee size={18} /> Salary Range</h4>
                <div className="ps-salary-row">
                  <input
                    type="number" placeholder="Min"
                    value={jobPrefs.salary_expectation_min || ''}
                    onChange={e => setJobPrefs({ ...jobPrefs, salary_expectation_min: Number(e.target.value) })}
                  />
                  <span>—</span>
                  <input
                    type="number" placeholder="Max"
                    value={jobPrefs.salary_expectation_max || ''}
                    onChange={e => setJobPrefs({ ...jobPrefs, salary_expectation_max: Number(e.target.value) })}
                  />
                </div>
              </div>

              <div className="glass-card ps-pref-card">
                <h4>Job Type</h4>
                <ChipsInput
                  value={jobPrefs.preferred_job_types || []}
                  onChange={val => setJobPrefs({ ...jobPrefs, preferred_job_types: val })}
                  placeholder="e.g. Full-time, Internship"
                />
              </div>

              <div className="glass-card ps-pref-card">
                <h4>Work Mode</h4>
                <div className="ps-radio-group">
                  {['remote', 'hybrid', 'on-site'].map(m => (
                    <label key={m} className={`ps-radio ${jobPrefs.work_mode === m ? 'active' : ''}`}>
                      <input type="radio" name="work_mode" value={m} checked={jobPrefs.work_mode === m}
                        onChange={() => setJobPrefs({ ...jobPrefs, work_mode: m })} />
                      <span>{m.charAt(0).toUpperCase() + m.slice(1)}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="glass-card ps-pref-card">
                <h4>Industry</h4>
                <input
                  type="text" value={jobPrefs.industry || ''}
                  onChange={e => setJobPrefs({ ...jobPrefs, industry: e.target.value })}
                  placeholder="e.g. Technology, Finance"
                />
              </div>

              <div className="glass-card ps-pref-card">
                <h4><Clock size={18} /> Notice Period</h4>
                <select value={jobPrefs.notice_period || ''} onChange={e => setJobPrefs({ ...jobPrefs, notice_period: e.target.value })}>
                  <option value="">Select</option>
                  <option value="immediate">Immediate</option>
                  <option value="2 weeks">2 Weeks</option>
                  <option value="1 month">1 Month</option>
                  <option value="2 months">2 Months</option>
                  <option value="3 months">3 Months</option>
                </select>
              </div>

              <div className="glass-card ps-pref-card">
                <Toggle
                  label="Open to Work"
                  checked={jobPrefs.open_to_work !== false}
                  onChange={val => setJobPrefs({ ...jobPrefs, open_to_work: val })}
                />
              </div>
            </div>

            <button className="ps-btn-primary" onClick={savePreferences} disabled={loading}>
              {loading ? 'Saving…' : 'Save Preferences'}
            </button>
          </section>
        )}

        {/* ── AI SETTINGS ────────────────────────────────────────────── */}
        {activeTab === 'ai' && (
          <section className="ps-section" id="settings-ai">
            <h2>AI Personalization</h2>

            <div className="glass-card ps-ai-mode">
              <h4><Brain size={18} /> Matching Mode</h4>
              <div className="ps-mode-cards">
                {[
                  { id: 'strict', label: 'Strict', desc: 'Only highly relevant matches' },
                  { id: 'balanced', label: 'Balanced', desc: 'Best mix of relevance & discovery' },
                  { id: 'exploratory', label: 'Exploratory', desc: 'Wider range of opportunities' },
                ].map(m => (
                  <div
                    key={m.id}
                    className={`ps-mode-card ${aiSettings.matching_mode === m.id ? 'active' : ''}`}
                    onClick={() => setAiSettings({ ...aiSettings, matching_mode: m.id })}
                  >
                    <strong>{m.label}</strong>
                    <span>{m.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card ps-ai-weights">
              <h4>Matching Weights</h4>
              <p className="ps-hint">Adjust how much each factor influences your job matches</p>
              <Slider label="Skills" value={aiSettings.skill_weight} onChange={v => setAiSettings({ ...aiSettings, skill_weight: v })} />
              <Slider label="Experience" value={aiSettings.experience_weight} onChange={v => setAiSettings({ ...aiSettings, experience_weight: v })} />
              <Slider label="Education" value={aiSettings.education_weight} onChange={v => setAiSettings({ ...aiSettings, education_weight: v })} />
            </div>

            <button className="ps-btn-primary" onClick={saveAISettings} disabled={loading}>
              {loading ? 'Saving…' : 'Save AI Settings'}
            </button>
          </section>
        )}

        {/* ── NOTIFICATIONS ──────────────────────────────────────────── */}
        {activeTab === 'notifications' && (
          <section className="ps-section" id="settings-notifications">
            <h2>Notifications & Alerts</h2>
            <div className="glass-card ps-notif-list">
              <Toggle label="Email — Job matches" checked={notifPrefs.email_jobs} onChange={v => setNotifPrefs({ ...notifPrefs, email_jobs: v })} />
              <Toggle label="Email — Recruiter messages" checked={notifPrefs.email_messages} onChange={v => setNotifPrefs({ ...notifPrefs, email_messages: v })} />
              <Toggle label="SMS Alerts" checked={notifPrefs.sms_alerts} onChange={v => setNotifPrefs({ ...notifPrefs, sms_alerts: v })} />
              <Toggle label="Push Notifications" checked={notifPrefs.push_notifications} onChange={v => setNotifPrefs({ ...notifPrefs, push_notifications: v })} />
              <div className="ps-form-group">
                <label>Frequency</label>
                <select value={notifPrefs.frequency} onChange={e => setNotifPrefs({ ...notifPrefs, frequency: e.target.value })}>
                  <option value="instant">Instant</option>
                  <option value="daily">Daily Digest</option>
                  <option value="weekly">Weekly Summary</option>
                </select>
              </div>
            </div>
            <button className="ps-btn-primary" onClick={saveNotifPrefs} disabled={loading}>
              {loading ? 'Saving…' : 'Save Notifications'}
            </button>
          </section>
        )}

        {/* ── PRIVACY & SECURITY ─────────────────────────────────────── */}
        {activeTab === 'privacy' && (
          <section className="ps-section" id="settings-privacy">
            <h2>Privacy & Security</h2>
            <div className="glass-card ps-privacy-block">
              <h4>Profile Visibility</h4>
              <div className="ps-radio-group">
                {['public', 'recruiters', 'private'].map(v => (
                  <label key={v} className={`ps-radio ${privacyData.profile_visibility === v ? 'active' : ''}`}>
                    <input type="radio" name="visibility" value={v} checked={privacyData.profile_visibility === v}
                      onChange={() => setPrivacyData({ ...privacyData, profile_visibility: v })} />
                    <span>{v.charAt(0).toUpperCase() + v.slice(1)}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="glass-card ps-privacy-block">
              <Toggle label="Show Resume to Recruiters" checked={privacyData.resume_visible} onChange={v => setPrivacyData({ ...privacyData, resume_visible: v })} />
              <Toggle label="Show Contact Info" checked={privacyData.contact_visible} onChange={v => setPrivacyData({ ...privacyData, contact_visible: v })} />
              <hr style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '1rem 0' }} />
              <Toggle 
                label="Two-Factor Authentication (OTP via Email & SMS)" 
                checked={user.mfa_enabled} 
                onChange={handleMfaToggle} 
              />
              <p className="ps-hint" style={{ marginTop: '0.5rem' }}>
                Secure your account by requiring a code sent to your registered devices on every login.
              </p>
            </div>
            <div className="glass-card ps-privacy-block">
              <h4>Blocked Companies</h4>
              <ChipsInput
                value={privacyData.blocked_companies || []}
                onChange={val => setPrivacyData({ ...privacyData, blocked_companies: val })}
                placeholder="Add company name"
              />
            </div>
            <button className="ps-btn-primary" onClick={savePrivacy} disabled={loading}>
              {loading ? 'Saving…' : 'Save Privacy Settings'}
            </button>

            <div className="ps-danger-zone glass-card">
              <h4><AlertTriangle size={18} /> Danger Zone</h4>
              <button className="ps-btn-outline" onClick={async () => {
                try { const r = await exportMyData(); const blob = new Blob([JSON.stringify(r.data, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'my-data.json'; a.click(); flash('success', 'Data downloaded!'); } catch { flash('error', 'Failed to export data'); }
              }}>
                <Download size={16} /> Download My Data
              </button>
              <button className="ps-btn-danger" onClick={async () => {
                const ok = await confirm('Are you sure? This action cannot be undone.');
                if (ok) {
                  try { await requestDataDeletion(); flash('success', 'Deletion request submitted.'); } catch { flash('error', 'Deletion request failed'); }
                }
              }}>
                <Trash2 size={16} /> Delete Account
              </button>
            </div>
          </section>
        )}

        {/* ── DASHBOARD PREFS ────────────────────────────────────────── */}
        {activeTab === 'dashboard' && (
          <section className="ps-section" id="settings-dashboard">
            <h2>Dashboard & UX Preferences</h2>
            <div className="glass-card ps-theme-card">
              <h4>{theme === 'dark' ? <Moon size={18} /> : <Sun size={18} />} Theme</h4>
              <Toggle
                label={theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
                checked={theme === 'dark'}
                onChange={toggleTheme}
              />
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

export default ProfileSettings;
