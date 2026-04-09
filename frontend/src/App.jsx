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
import Profile from './pages/Profile'
import ProfileSettings from './pages/ProfileSettings'
import CareerDashboard from './pages/CareerDashboard'
import TrainingDashboard from './pages/TrainingDashboard'

import AnalyticsDashboard from './pages/AnalyticsDashboard'
import AllTalent from './pages/AllTalent'
import ActiveRoles from './pages/ActiveRoles'
import AdminDashboard from './pages/AdminDashboard'
import MessageCenter from './components/MessageCenter'
import MessageSidebar from './components/MessageSidebar'
import { MessagingProvider } from './contexts/MessagingContext'
 import { NotifyProvider } from './contexts/NotifyContext'
import { useAuth } from './contexts/AuthContext'
import useOneSignal from './hooks/useOneSignal'
import './styles/App.css'
import './styles/Features.css'

import ErrorBoundary from './components/ErrorBoundary'

const queryClient = new QueryClient()

function OneSignalInitializer() {
  const { user } = useAuth()
  useOneSignal(user)
  return null
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <AuthProvider>
          <NotifyProvider>
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
                    <ProtectedRoute requireVerified={false} allowedRoles={['job_seeker']}>
                      <><Navbar /><CandidateDashboard /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/jobs"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['recruiter']}>
                      <><Navbar /><JobPosting /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/matches"
                  element={
                    <ProtectedRoute requireVerified={false}>
                      <><Navbar /><Matches /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['recruiter', 'admin']}>
                      <><Navbar /><AnalyticsDashboard /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['admin']}>
                      <><Navbar /><AdminDashboard /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/all-talent"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['recruiter', 'admin']}>
                      <><Navbar /><AllTalent /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/active-roles"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['recruiter', 'admin']}>
                      <><Navbar /><ActiveRoles /></>
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
                  path="/settings"
                  element={
                    <ProtectedRoute requireVerified={false}>
                      <><Navbar /><ProfileSettings /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/messages"
                  element={
                    <ProtectedRoute requireVerified={false}>
                      <><Navbar /><div style={{maxWidth:'900px',margin:'24px auto',padding:'0 16px'}}><MessageCenter /></div></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/career-dashboard"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['job_seeker']}>
                      <><Navbar /><CareerDashboard /></>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/training/:matchId"
                  element={
                    <ProtectedRoute requireVerified={false} allowedRoles={['job_seeker', 'recruiter', 'admin']}>
                      <><Navbar /><TrainingDashboard /></>
                    </ProtectedRoute>
                  }
                />
              </Routes>

              </div>
            </Router>
          </MessagingProvider>
          </NotifyProvider>
        </AuthProvider>
      </ErrorBoundary>
    </QueryClientProvider>
  )
}

export default App
