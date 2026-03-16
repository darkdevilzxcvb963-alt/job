import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Bell, MessageCircle, User, LogOut, LogIn, UserPlus, Menu, X } from 'lucide-react'
import DarkModeToggle from './DarkModeToggle'
import { useAuth } from '../contexts/AuthContext'
import { useMessaging } from '../contexts/MessagingContext'
import { getMyNotifications, markNotificationRead, markAllNotificationsRead } from '../services/api'
import '../styles/Navbar.css'

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
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
      enabled: isAuthenticated && user?.role === 'recruiter',
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
    navigate('/')
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

        <div className="navbar-menu">
          {isAuthenticated && !['/', '/login', '/signup', '/forgot-password', '/reset-password'].includes(location.pathname) ? (
            <>
              {user?.role === 'job_seeker' && (
                <Link to="/candidate" className="nav-link">Dashboard</Link>
              )}
              {user?.role === 'recruiter' && (
                <Link to="/jobs" className="nav-link">Post Jobs</Link>
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

              {/* 🔔 Bell — recruiter only */}
              {user?.role === 'recruiter' && (
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
                                // Show info shortly as requested
                                alert(`Notification: ${n.message}`);
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
              )}

              <DarkModeToggle />
              <div className="user-menu">
                <span className="user-name">{user?.full_name}</span>
                <div className="dropdown">
                  <button className="dropdown-toggle">▼</button>
                  <div className="dropdown-menu">
                    <Link to="/profile" className="dropdown-item icon-anim-item">
                      <User className="dropdown-icon" size={16} /> <span>Profile</span>
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
          className="mobile-menu-btn" 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Mobile Menu Drawer */}
        {isMobileMenuOpen && (
          <div className="mobile-menu-overlay">
            <div className="mobile-menu-content">
              {isAuthenticated && !['/', '/login', '/signup', '/forgot-password', '/reset-password'].includes(location.pathname) ? (
                <>
                  <div className="mobile-user-info">
                    <User size={24} className="mobile-user-icon" />
                    <span>{user?.full_name}</span>
                  </div>
                  
                  {user?.role === 'job_seeker' && (
                    <Link to="/candidate" className="mobile-nav-link" onClick={() => setIsMobileMenuOpen(false)}>Dashboard</Link>
                  )}
                  {user?.role === 'recruiter' && (
                    <Link to="/jobs" className="mobile-nav-link" onClick={() => setIsMobileMenuOpen(false)}>Post Jobs</Link>
                  )}
                  {user?.role === 'admin' && (
                    <Link to="/admin" className="mobile-nav-link" onClick={() => setIsMobileMenuOpen(false)}>Admin Panel</Link>
                  )}
                  {user?.role !== 'admin' && (
                    <Link to="/matches" className="mobile-nav-link" onClick={() => setIsMobileMenuOpen(false)}>Matches</Link>
                  )}
                  {user?.role !== 'admin' && (
                    <button
                      onClick={() => { toggleSidebar(); setIsMobileMenuOpen(false); }}
                      className="mobile-nav-link"
                      style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%' }}
                    >
                      Messages {msgUnread > 0 && `(${msgUnread})`}
                    </button>
                  )}

                  <Link to="/profile" className="mobile-nav-link" onClick={() => setIsMobileMenuOpen(false)}>Profile</Link>
                  
                  <div style={{ padding: '15px' }}>
                    <DarkModeToggle />
                  </div>

                  <button onClick={handleLogout} className="mobile-nav-link text-danger" style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%' }}>
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="mobile-nav-link" onClick={() => setIsMobileMenuOpen(false)}>Login</Link>
                  <Link to="/signup" className="mobile-nav-link mobile-btn-signup" onClick={() => setIsMobileMenuOpen(false)}>Sign Up</Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
