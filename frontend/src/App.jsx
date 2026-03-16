import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import VerifyEmail from './pages/VerifyEmail'
import CandidateDashboard from './pages/CandidateDashboard'
import JobPosting from './pages/JobPosting'
import Matches from './pages/Matches'
import AdminDashboard from './pages/AdminDashboard'
import Profile from './pages/Profile'
import MessageCenter from './components/MessageCenter'
import MessageSidebar from './components/MessageSidebar'
import { MessagingProvider } from './contexts/MessagingContext'
import { useAuth } from './contexts/AuthContext'
import useOneSignal from './hooks/useOneSignal'
import './styles/App.css'
import './styles/Features.css'

const queryClient = new QueryClient()

function OneSignalInitializer() {
  const { user } = useAuth()
  useOneSignal(user)
  return null
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <OneSignalInitializer />
        <MessagingProvider>
          <Router>
            <div className="App">
              <MessageSidebar />
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<div className="auth-page-wrapper"><Navbar /><div className="auth-content"><Login /></div></div>} />
                <Route path="/signup" element={<div className="auth-page-wrapper"><Navbar /><div className="auth-content"><Signup /></div></div>} />
                <Route path="/forgot-password" element={<div className="auth-page-wrapper"><Navbar /><div className="auth-content"><ForgotPassword /></div></div>} />
                <Route path="/reset-password" element={<div className="auth-page-wrapper"><Navbar /><div className="auth-content"><ResetPassword /></div></div>} />
                <Route path="/verify-email" element={<div className="auth-page-wrapper"><Navbar /><div className="auth-content"><VerifyEmail /></div></div>} />
                <Route
                  path="/candidate"
                  element={
                    <ProtectedRoute requireVerified={true} allowedRoles={['job_seeker']}>
                      <><Navbar /><CandidateDashboard /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/jobs"
                  element={
                    <ProtectedRoute requireVerified={true} allowedRoles={['recruiter']}>
                      <><Navbar /><JobPosting /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/matches"
                  element={
                    <ProtectedRoute requireVerified={true}>
                      <><Navbar /><Matches /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute requireVerified={true} allowedRoles={['admin']}>
                      <><Navbar /><AdminDashboard /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <><Navbar /><Profile /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/messages"
                  element={
                    <ProtectedRoute requireVerified={true}>
                      <><Navbar /><div style={{maxWidth:'900px',margin:'24px auto',padding:'0 16px'}}><MessageCenter /></div></>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </div>
          </Router>
        </MessagingProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
