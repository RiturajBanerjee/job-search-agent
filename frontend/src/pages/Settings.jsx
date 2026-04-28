import React from 'react'
import { useNavigate } from 'react-router-dom'
import { getConfig, updateConfig } from '../api'
import '../styles/Settings.css'

export default function Settings() {
  const [keywords, setKeywords] = React.useState('')
  const [experienceSummary, setExperienceSummary] = React.useState('')
  const [emailFrequency, setEmailFrequency] = React.useState('daily')
  const [message, setMessage] = React.useState('')
  const navigate = useNavigate()

  React.useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await getConfig()
        if (response.data) {
          setKeywords(response.data.keywords || '')
          setExperienceSummary(response.data.experience_summary || '')
          setEmailFrequency(response.data.email_frequency || 'daily')
        }
      } catch (err) {
        console.error('Failed to fetch config:', err)
      }
    }

    fetchConfig()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await updateConfig({
        keywords,
        experience_summary: experienceSummary,
        email_frequency: emailFrequency
      })
      setMessage('Settings updated successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setMessage('Failed to update settings')
    }
  }

  return (
    <div className="settings">
      <nav className="navbar">
        <h1>Settings</h1>
        <button onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
      </nav>

      <div className="settings-content">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="keywords">Job Keywords (comma-separated)</label>
            <textarea
              id="keywords"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g., Python, FastAPI, Backend"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="experience">Experience Summary</label>
            <textarea
              id="experience"
              value={experienceSummary}
              onChange={(e) => setExperienceSummary(e.target.value)}
              placeholder="Describe your relevant experience..."
              rows="5"
            />
          </div>

          <div className="form-group">
            <label htmlFor="frequency">Email Frequency</label>
            <select
              id="frequency"
              value={emailFrequency}
              onChange={(e) => setEmailFrequency(e.target.value)}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <button type="submit">Save Settings</button>
        </form>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  )
}
