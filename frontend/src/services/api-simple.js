/**
 * Simplified API service that uses /auth-simple endpoints
 * Use this if the main auth endpoints are not working
 * 
 * To use: Import from this file instead of api.js
 * Example: import { login, signup } from './services/api-simple'
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
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

    // Log network errors for debugging
    if (!error.response) {
      console.error('Network Error:', {
        message: error.message,
        code: error.code,
        url: originalRequest?.url
      })
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
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
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
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

// Simplified Auth APIs (no email verification required)
export const signup = (data) => api.post('/auth-simple/signup', data)
export const login = (data) => api.post('/auth-simple/login', data)
export const logout = () => api.post('/auth/logout')
export const getCurrentUser = () => api.get('/auth/me')

// Keep other APIs the same
export const createCandidate = (data) => api.post('/candidates', data)
export const getCandidates = () => api.get('/candidates')
export const getCandidate = (id) => api.get(`/candidates/${id}`)
export const updateCandidate = (id, data) => api.put(`/candidates/${id}`, data)
export const processResume = (candidateId, filePath) => 
  api.post(`/candidates/${candidateId}/process-resume`, { file_path: filePath })

export const createJob = (data) => api.post('/jobs', data)
export const getJobs = () => api.get('/jobs')
export const getJob = (id) => api.get(`/jobs/${id}`)
export const updateJob = (id, data) => api.put(`/jobs/${id}`, data)

export const createMatch = (candidateId, jobId) => 
  api.post('/matches', null, { params: { candidate_id: candidateId, job_id: jobId } })
export const getCandidateMatches = (candidateId) => 
  api.get(`/matches/candidate/${candidateId}`)
export const getJobMatches = (jobId) => 
  api.get(`/matches/job/${jobId}`)

export const uploadResume = (formData) => {
  const uploadApi = axios.create({
    baseURL: API_BASE_URL,
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

export default api
