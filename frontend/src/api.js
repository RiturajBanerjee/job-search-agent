import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
});

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const login = (email, password) =>
  API.post("/auth/login", { email, password });

// Jobs
export const searchJobs = (params) => API.post("/jobs/search", params);
export const getRecentJobs = () => API.get("/jobs/recent");

// Config
export const getConfig = () => API.get("/config");
export const saveConfig = (data) => API.post("/config", data);

export default API;