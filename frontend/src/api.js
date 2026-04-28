import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth endpoints
export const login = (email, password) =>
  api.post('/auth/login', { email, password })

export const register = (email, password, full_name) =>
  api.post('/auth/register', { email, password, full_name })

export const getCurrentUser = () =>
  api.get('/auth/me')

// Config endpoints
export const getConfig = () =>
  api.get('/config/')

export const updateConfig = (data) =>
  api.put('/config/', data)

// Jobs endpoints
export const getJobs = (skip = 0, limit = 10) =>
  api.get('/jobs/', { params: { skip, limit } })

export const getJob = (jobId) =>
  api.get(`/jobs/${jobId}`)

export const createJob = (jobData) =>
  api.post('/jobs/', jobData)

export const deleteJob = (jobId) =>
  api.delete(`/jobs/${jobId}`)

export default api
