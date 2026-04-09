import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { 
  Bell, MessageCircle, MessageSquare, User, LogOut, LogIn, 
  UserPlus, Menu, X, Settings, Briefcase, BarChart3, Shield, Target, ChevronDown 
} from 'lucide-react'
import DarkModeToggle from './DarkModeToggle'
import { useAuth } from '../contexts/AuthContext'
import { useNotify } from '../contexts/NotifyContext'
import { useMessaging } from '../contexts/MessagingContext'
import { getMyNotifications, markNotificationRead, markAllNotificationsRead } from '../services/api'
import '../styles/Navbar.css'

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const { info } = useNotify()
  const { toggleSidebar, unreadCount: msgUnread } = useMessaging()
  const navigate = useNavigate()
  const location = useLocation()
  const [bellOpen, setBellOpen] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const bellRef = useRef(null)
  const queryClient = useQueryClient()

  // Poll notifications every 30 seconds for recruiters
  const { data: notifData } = useQuery(
    'myNotifications',
    () => getMyNotifications().then(r => r.data),
    {
      enabled: isAuthenticated,
      refetchInterval: 30000,
      refetchOnWindowFocus: true,
    }
  )

  const unreadCount = notifData?.unread_count || 0
  const notifications = notifData?.notifications || []

  const markReadMutation = useMutation(
    (id) => markNotificationRead(id),
    { onSuccess: () => queryClient.invalidateQueries('myNotifications') }
  )

  const markAllMutation = useMutation(
    () => markAllNotificationsRead(),
    { onSuccess: () => queryClient.invalidateQueries('myNotifications') }
  )

  // Close dropdown on outside click
  useEffect(() => {
    function handle(e) {
      if (bellRef.current && !bellRef.current.contains(e.target)) setBellOpen(false)
    }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [])

  const handleLogout = async () => {
    setIsMobileMenuOpen(false)
    await logout()
    queryClient.clear()
    navigate('/login')
  }

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [location.pathname])

  const formatTime = (iso) => {
    const d = new Date(iso)
    const now = new Date()
    const diff = Math.floor((now - d) / 60000)
    if (diff < 1) return 'just now'
    if (diff < 60) return `${diff}m ago`
    if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
    return d.toLocaleDateString()
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🎯</span>
          <span className="logo-text">ResumeMatch</span>
        </Link>

        {/* Desktop Menu */}
        <div className="navbar-menu">
          {isAuthenticated && !['/login', '/signup', '/forgot-password', '/reset-password'].includes(location.pathname) ? (
            <>
              {user?.role === 'job_seeker' && (
                <>
                  <Link to="/career-dashboard" className="nav-link">Career Hub</Link>
                  <Link to="/candidate" className="nav-link">Resume Profile</Link>
                </>
              )}
              {user?.role === 'recruiter' && (
                <Link to="/jobs" className="nav-link">Post Jobs</Link>
              )}
              {(user?.role === 'recruiter' || user?.role === 'admin') && (
                <Link to="/analytics" className="nav-link">Analytics</Link>
              )}
              {user?.role === 'admin' && (
                <Link to="/admin" className="nav-link">Admin Panel</Link>
              )}
              {user?.role !== 'admin' && (
                <Link to="/matches" className="nav-link">Matches</Link>
              )}
              {user?.role !== 'admin' && (
                <button
                  onClick={toggleSidebar}
                  className="nav-link ms-trigger-btn"
                  style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', position: 'relative' }}
                >
                  <MessageCircle size={16} /> Messages
                  {msgUnread > 0 && <span className="nav-badge">{msgUnread}</span>}
                </button>
              )}

              {/* 🔔 Bell — all roles */}
              <div className="bell-wrapper" ref={bellRef}>
                <button
                  className="bell-btn"
                  onClick={() => setBellOpen(o => !o)}
                  title="Notifications"
                >
                  <Bell size={20} />
                  {unreadCount > 0 && (
                    <span className="bell-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
                  )}
                </button>

                {bellOpen && (
                  <div className="notif-dropdown">
                    <div className="notif-header">
                      <span>Notifications</span>
                      {unreadCount > 0 && (
                        <button
                          className="notif-mark-all"
                          onClick={() => markAllMutation.mutate()}
                        >
                          Mark all read
                        </button>
                      )}
                    </div>

                    {notifications.length === 0 ? (
                      <div className="notif-empty">No notifications yet</div>
                    ) : (
                      <div className="notif-list">
                        {notifications.map(n => (
                          <div
                            key={n.id}
                            className={`notif-item ${!n.is_read ? 'unread' : ''}`}
                            onClick={() => {
                              if (!n.is_read) markReadMutation.mutate(n.id)
                              info(`Notification: ${n.message}`);
                              if (n.related_match_id) navigate('/matches')
                              setBellOpen(false)
                            }}
                          >
                            <div className="notif-dot" />
                            <div className="notif-content">
                              <p className="notif-msg">{n.message}</p>
                              <span className="notif-time">{formatTime(n.created_at)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {location.pathname !== '/' && <DarkModeToggle />}
              <div className="user-menu">
                <div className="user-avatar-circle">
                  {user?.profile_picture_url ? (
                    <img src={user.profile_picture_url} alt="Profile" className="user-avatar-img" />
                  ) : (
                    <span className="user-avatar-initial">{user?.full_name?.charAt(0).toUpperCase()}</span>
                  )}
                </div>
                <span className="user-name">{user?.full_name}</span>
                <div className="dropdown">
                  <button className="dropdown-toggle-simple" title="Options">
                    <ChevronDown size={16} />
                  </button>
                  <div className="dropdown-menu">
                    <Link to="/profile" className="dropdown-item icon-anim-item">
                      <User className="dropdown-icon" size={16} /> <span>Profile</span>
                    </Link>
                    <Link to="/settings" className="dropdown-item icon-anim-item">
                      <Settings className="dropdown-icon" size={16} /> <span>Settings</span>
                    </Link>
                    <button onClick={handleLogout} className="dropdown-item icon-anim-item">
                      <LogOut className="dropdown-icon logout-icon" size={16} /> <span>Logout</span>
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              {!['/', '/login', '/signup'].includes(location.pathname) && <DarkModeToggle />}
              <Link to="/login" className="nav-link icon-anim-item" style={{display: 'flex', gap: '6px', alignItems: 'center'}}>
                <LogIn className="dropdown-icon" size={16} /> <span>Login</span>
              </Link>
              <Link to="/signup" className="nav-link btn-signup icon-anim-item" style={{display: 'flex', gap: '6px', alignItems: 'center'}}>
                <UserPlus className="dropdown-icon" size={16} style={{color: 'white'}}/> <span>Sign Up</span>
              </Link>
            </>
          )}
        </div>

        {/* Hamburger Icon */}
        <button 
          className={`mobile-menu-btn ${isMobileMenuOpen ? 'active' : ''}`}
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Mobile Menu Drawer */}
        <div className={`mobile-menu-overlay ${isMobileMenuOpen ? 'open' : ''}`} onClick={() => setIsMobileMenuOpen(false)}>
          <div className="mobile-menu-content" onClick={e => e.stopPropagation()}>
            <div className="mobile-menu-header">
              {/* Removed redundant close button and Menu text */}
            </div>

            <div className="mobile-menu-body">
              {isAuthenticated ? (
                <>
                  <div className="mobile-user-card glass-card">
                    <div className="mobile-user-avatar">
                      {user?.full_name?.charAt(0).toUpperCase()}
                    </div>
                    <div className="mobile-user-details">
                      <span className="mobile-user-name">{user?.full_name}</span>
                      <span className="mobile-user-role">{user?.role?.replace('_', ' ')}</span>
                    </div>
                  </div>
                  
                  <div className="mobile-nav-group">
                    {user?.role === 'job_seeker' && (
                      <>
                        <Link to="/career-dashboard" className="mobile-nav-link"><MessageCircle size={18}/> Career Hub</Link>
                        <Link to="/candidate" className="mobile-nav-link"><User size={18}/> Resume Profile</Link>
                      </>
                    )}
                    {user?.role === 'recruiter' && (
                      <Link to="/jobs" className="mobile-nav-link"><Briefcase size={18}/> Post Jobs</Link>
                    )}
                    {(user?.role === 'recruiter' || user?.role === 'admin') && (
                      <Link to="/analytics" className="mobile-nav-link"><BarChart3 size={18}/> Analytics</Link>
                    )}
                    {user?.role === 'admin' && (
                      <Link to="/admin" className="mobile-nav-link"><Shield size={18}/> Admin Panel</Link>
                    )}
                    {user?.role !== 'admin' && (
                      <Link to="/matches" className="mobile-nav-link"><Target size={18}/> Matches</Link>
                    )}
                    {user?.role !== 'admin' && (
                      <button
                        onClick={() => { toggleSidebar(); setIsMobileMenuOpen(false); }}
                        className="mobile-nav-link"
                      >
                        <MessageSquare size={18}/> Messages {msgUnread > 0 && <span className="mobile-badge">{msgUnread}</span>}
                      </button>
                    )}
                  </div>

                  <div className="mobile-nav-group">
                    <Link to="/profile" className="mobile-nav-link"><User size={18}/> Profile</Link>
                    <Link to="/settings" className="mobile-nav-link"><Settings size={18}/> Settings</Link>
                    {location.pathname !== '/' && (
                      <div className="mobile-nav-link theme-switch-row">
                        <span>Dark Mode</span>
                        <DarkModeToggle />
                      </div>
                    )}
                  </div>

                  <button onClick={handleLogout} className="mobile-nav-link logout-btn">
                    <LogOut size={18}/> Logout
                  </button>
                </>
              ) : (
                <div className="mobile-auth-actions">
                  <Link to="/login" className="mobile-nav-link">Login</Link>
                  <Link to="/signup" className="mobile-btn-signup">Sign Up</Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
