import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 300s (5m) timeout for heavy AI processing
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response) {
      console.log(`API Error: ${error.response.status} ${originalRequest.url}`, error.response.data);
    } else {
      console.error('API Network Error:', error.message);
      // Return a more user-friendly error for network issues
      return Promise.reject({
        message: 'Unable to reach the server. Please check your internet connection or ensure the backend server is running.',
        originalError: error
      })
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('401 Unauthorized detected, attempting token refresh...');
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          })
          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          console.log('Token refreshed successfully, retrying original request.');
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth APIs
export const signup = (data) => api.post('/auth/signup', data)
export const login = (data) => api.post('/auth/login', data)
export const googleAuth = (data) => api.post('/auth/google-auth', data)
export const logout = () => api.post('/auth/logout')
export const getCurrentUser = () => api.get('/auth/me')
export const verifyEmail = (token) => api.post('/auth/verify-email', { token })
export const validateResetToken = (token) => api.post('/auth/validate-reset-token', { token })
export const forgotPassword = (email) => api.post('/auth/forgot-password', { email })
export const resetPassword = (token, newPassword) =>
  api.post('/auth/reset-password', { token, new_password: newPassword })
export const refreshToken = (refreshToken) =>
  api.post('/auth/refresh', { refresh_token: refreshToken })
export const changePassword = (data) => api.post('/auth/change-password', data)
export const updateMe = (data) => api.patch('/auth/me', data)

// Admin APIs
export const adminResetPassword = (userId, newPassword) =>
  api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword })
export const listUsers = (params) => api.get('/admin/users', { params })
export const verifyUser = (userId) => api.post(`/admin/users/${userId}/verify`)
export const rejectUser = (userId, reason) => api.post(`/admin/users/${userId}/reject`, null, { params: { reason } })
export const deleteUser = (userId) => api.delete(`/admin/users/${userId}`)
export const getUserDetails = (userId) => api.get(`/admin/users/${userId}`)
export const getAdminStats = () => api.get('/admin/stats/overview')
export const getRecruiters = (params) => api.get('/admin/recruiters', { params })
export const verifyRecruiter = (recruiterId) => api.post(`/admin/recruiters/${recruiterId}/verify`)

// Candidate APIs
export const createCandidate = (data) => api.post('/candidates', data)
export const getCandidates = (params) => api.get('/candidates', { params })
export const getCandidate = (id) => api.get(`/candidates/${id}`)
export const updateCandidate = (id, data) => api.put(`/candidates/${id}`, data)
export const processResume = (candidateId, filePath) =>
  api.post(`/candidates/${candidateId}/process-resume`, { file_path: filePath })

export const uploadAndAnalyzeResume = (candidateId, formData) => {
  const uploadApi = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  const token = localStorage.getItem('access_token')
  if (token) {
    uploadApi.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
  return uploadApi.post(`/candidates/${candidateId}/resume`, formData)
}

// Job APIs
export const createJob = (data) => api.post('/jobs', data)
export const getJobs = () => api.get('/jobs')
export const getJob = (id) => api.get(`/jobs/${id}`)
export const updateJob = (id, data) => api.put(`/jobs/${id}`, data)

// Match APIs
export const createMatch = (candidateId, jobId) =>
  api.post('/matches', null, { params: { candidate_id: candidateId, job_id: jobId } })
export const getMyMatches = (params) =>
  api.get('/matches/my-matches', { params })
export const getCandidateMatches = (candidateId, params) =>
  api.get(`/matches/candidate/${candidateId}`, { params })
export const getJobMatches = (jobId, params) =>
  api.get(`/matches/job/${jobId}`, { params })
export const applyToJob = (matchId) =>
  api.post(`/matches/${matchId}/apply`)
export const applyWithForm = (matchId, coverLetter) =>
  api.post(`/matches/${matchId}/apply-with-form`, { cover_letter: coverLetter })
export const updateMatchStatus = (matchId, status) =>
  api.patch(`/matches/${matchId}/status`, null, { params: { status } })

// Notification APIs
export const getMyNotifications = () => api.get('/notifications/my')
export const markNotificationRead = (id) => api.post(`/notifications/${id}/read`)
export const markAllNotificationsRead = () => api.post('/notifications/read-all')


// Generate matches for the current user
export const generateMatches = (minScore = 0.0) => {
  return api.post(`/matches/generate-for-me`, null, {
    params: { min_score: minScore }
  })
}

export const generateMatchesForRecruiter = () => {
  return api.post(`/matches/generate-for-recruiter`)
}

// AI APIs
export const generateOutreach = (data) => api.post('/ai/generate-outreach', data)
export const generateJD = (data) => api.post('/ai/generate-jd', data)
export const generateInterviewPrep = (data) => api.post('/ai/generate-interview-prep', data)
export const smartSearch = (data) => api.post('/ai/smart-search', data)

// Upload APIs
export const uploadResume = (formData) => {
  const uploadApi = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  const token = localStorage.getItem('access_token')
  if (token) {
    uploadApi.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
  return uploadApi.post('/upload/resume', formData)
}

export const getSelectionStats = () => api.get('/matches/selection-stats')

// Feedback & Analytics APIs
export const submitMatchFeedback = (matchId, data) =>
  api.post(`/feedback/${matchId}/feedback`, data)
export const getSkillDemand = () => api.get('/feedback/analytics/skill-demand')
export const getMatchQualityStats = () => api.get('/feedback/analytics/match-quality')
export const getRecruitmentFunnel = () => api.get('/feedback/analytics/recruitment-funnel')

// Social Integration APIs
export const enrichFromGithub = (username) =>
  api.post('/social/enrich/github', { github_username: username })
export const enrichFromLinkedin = (url) =>
  api.post('/social/enrich/linkedin', { linkedin_url: url })
export const getShareLinks = (data) => api.post('/social/share-links', data)
export const generateReferral = (jobId) =>
  api.post('/social/referral', { job_id: jobId })

// Privacy & Compliance APIs
export const exportMyData = () => api.get('/privacy/my-data')
export const requestDataDeletion = () => api.delete('/privacy/my-data')
export const getPrivacyPolicy = () => api.get('/privacy/privacy-policy')

// ========== NEW FEATURE APIs ==========

// Bookmark APIs
export const saveJob = (data) => api.post('/bookmarks/', data)
export const getSavedJobs = () => api.get('/bookmarks/')
export const unsaveJob = (jobId) => api.delete(`/bookmarks/${jobId}`)

// Skill Gap Analysis APIs
export const analyzeSkillGap = (candidateId, jobId) =>
  api.get(`/skill-gap/${candidateId}/${jobId}`)

// Interview APIs
export const scheduleInterview = (data) => api.post('/interviews/', data)
export const getMyInterviews = () => api.get('/interviews/my')
export const updateInterview = (id, data) => api.patch(`/interviews/${id}`, data)

// Message APIs
export const sendMessage = (data) => api.post('/messages/', data)
export const getConversations = () => api.get('/messages/conversations')
export const getThread = (userId) => api.get(`/messages/thread/${userId}`)
export const getUnreadCount = () => api.get('/messages/unread-count')

// Shortlist APIs
export const createShortlist = (data) => api.post('/shortlists/', data)
export const getShortlists = () => api.get('/shortlists/')
export const addToShortlist = (shortlistId, data) =>
  api.post(`/shortlists/${shortlistId}/candidates`, data)
export const getShortlistCandidates = (shortlistId) =>
  api.get(`/shortlists/${shortlistId}/candidates`)
export const deleteShortlist = (shortlistId) => api.delete(`/shortlists/${shortlistId}`)
export const removeFromShortlist = (shortlistId, candidateId) =>
  api.delete(`/shortlists/${shortlistId}/candidates/${candidateId}`)

// Resume Scoring API
export const scoreResume = (candidateId, jobId) =>
  api.post('/ai/score-resume', null, { params: { candidate_id: candidateId, job_id: jobId } })

export default api
