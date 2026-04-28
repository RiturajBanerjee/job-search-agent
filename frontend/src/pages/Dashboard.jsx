import React from 'react'
import { useNavigate } from 'react-router-dom'
import { getJobs } from '../api'
import '../styles/Dashboard.css'

export default function Dashboard() {
  const [jobs, setJobs] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const navigate = useNavigate()

  React.useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await getJobs()
        setJobs(response.data)
      } catch (err) {
        console.error('Failed to fetch jobs:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchJobs()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="dashboard">
      <nav className="navbar">
        <h1>Job Search Agent</h1>
        <div className="nav-buttons">
          <button onClick={() => navigate('/settings')}>Settings</button>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </nav>

      <div className="dashboard-content">
        <h2>Your Job Matches</h2>
        {loading ? (
          <p>Loading...</p>
        ) : jobs.length === 0 ? (
          <p>No jobs found. Configure your preferences in Settings.</p>
        ) : (
          <div className="jobs-list">
            {jobs.map((job) => (
              <div key={job.id} className="job-card">
                <h3>{job.title}</h3>
                <p><strong>Company:</strong> {job.company}</p>
                <p><strong>Location:</strong> {job.location}</p>
                <p><strong>Match Score:</strong> {job.match_score}%</p>
                <a href={job.link} target="_blank" rel="noopener noreferrer">
                  View Job
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
