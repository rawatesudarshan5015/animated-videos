import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState('checking...')

  useEffect(() => {
    // Check if backend API is running
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'OK') {
          setApiStatus('Backend is connected!')
        }
      })
      .catch(() => {
        setApiStatus('Backend is offline')
      })
  }, [])

  return (
    <div className="app">
      <h1>Kids Video Enhancer Tool</h1>
      <p className="status">App is running</p>
      <p className="api-status">API Status: {apiStatus}</p>
      <div className="features">
        <h2>Features (Coming Soon)</h2>
        <ul>
          <li>Upload normal videos</li>
          <li>Apply cartoon-style filters</li>
          <li>Add auto-generated subtitles</li>
          <li>Overlay stickers and emojis</li>
          <li>Add sound effects</li>
          <li>Download enhanced video</li>
        </ul>
      </div>
    </div>
  )
}

export default App
