import React, { useState, useRef } from 'react';
import './App.css';

function App() {
  const [inputMode, setInputMode] = useState<'file' | 'youtube'>('file');
  const [file, setFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [filterType, setFilterType] = useState('none');
  const [subtitles, setSubtitles] = useState(false);
  const [stickers, setStickers] = useState(false);
  const [sfx, setSfx] = useState(false);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultVideoUrl, setResultVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollingStatus, setPollingStatus] = useState<string>('');
  const pollIntervalRef = useRef<number | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Use environment variable for API URL or default to localhost for local dev
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleProcess = async () => {
    if (inputMode === 'file' && !file) {
      setError("Please select a video first!");
      return;
    }
    
    if (inputMode === 'youtube' && !youtubeUrl) {
      setError("Please enter a YouTube URL!");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResultVideoUrl(null);

    try {
      let response;
      if (inputMode === 'file') {
        const formData = new FormData();
        formData.append("file", file as File);

        const queryParams = new URLSearchParams({
          filter_type: filterType,
          generate_subtitles: subtitles.toString(),
          add_stickers: stickers.toString(),
          add_sfx: sfx.toString()
        });

        response = await fetch(`${API_BASE_URL}/upload?${queryParams.toString()}`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${API_BASE_URL}/youtube`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            url: youtubeUrl,
            filter_type: filterType,
            generate_subtitles: subtitles,
            subtitle_font_size: 24,
            subtitle_font_color: "white",
            subtitle_outline_color: "black",
            add_stickers: stickers,
            add_sfx: sfx
          })
        });
      }

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Something went wrong during processing.");
      }

      const data = await response.json();
      setPollingStatus('Video uploaded! Starting magical background processing...');
      pollJobStatus(data.job_id);
      
    } catch (err: any) {
      setError(err.message);
      setIsProcessing(false);
    }
  };

  const pollJobStatus = (jobId: string) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    
    pollIntervalRef.current = window.setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/status/${jobId}`);
        if (!res.ok) throw new Error("Failed to get status");
        
        const job = await res.json();
        
        if (job.status === 'completed') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
          
          // Replace Windows backslashes with forward slashes for the URL just in case
          const formattedPath = job.result.output.replace(/\\/g, '/');
          setResultVideoUrl(`${API_BASE_URL}/${formattedPath}`);
          
          setIsProcessing(false);
        } else if (job.status === 'failed') {
          if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
          setError(`Processing failed: ${job.error}`);
          setIsProcessing(false);
        } else {
          setPollingStatus('Magic is happening! Still processing...');
        }
      } catch (e: any) {
        console.error(e);
      }
    }, 2000);
  };

  return (
    <div className="app-container">
      <header className="hero">
        <h1>✨ Kids Video Enhancer ✨</h1>
        <p>Turn normal videos into magical cartoons!</p>
      </header>

      {error && (
        <div className="glass-panel" style={{ backgroundColor: 'rgba(255, 107, 107, 0.2)', color: '#d63031' }}>
          <p><strong>Error:</strong> {error}</p>
        </div>
      )}

      {!isProcessing && !resultVideoUrl && (
        <main className="glass-panel upload-card">
          <div className="input-mode-toggle">
            <button 
              className={inputMode === 'file' ? 'active' : ''} 
              onClick={() => setInputMode('file')}
            >
              📂 Upload File
            </button>
            <button 
              className={inputMode === 'youtube' ? 'active' : ''} 
              onClick={() => setInputMode('youtube')}
            >
              📺 YouTube Link
            </button>
          </div>

          {inputMode === 'file' ? (
            <div 
              className="dropzone"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={() => fileInputRef.current?.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                accept="video/*"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                  }
                }}
              />
              {file ? (
                <p>🎥 {file.name} selected!</p>
              ) : (
                <div>
                  <p style={{ fontSize: '3rem', margin: 0 }}>📂</p>
                  <p>Drag & Drop a video here or click to browse</p>
                </div>
              )}
            </div>
          ) : (
            <div className="youtube-input-container">
              <input 
                type="text" 
                placeholder="Paste YouTube Link here..." 
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                className="youtube-input"
              />
            </div>
          )}

          <div className="options-grid">
            <div className="option-item">
              <label>🎨 Cartoon Filter</label>
              <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                <option value="none">None (Original)</option>
                <option value="light_cartoon">Light Cartoon</option>
                <option value="cartoon">Standard Cartoon</option>
                <option value="heavy_cartoon">Heavy Cartoon</option>
              </select>
            </div>

            <div className="option-item row">
              <label>📝 Auto Subtitles</label>
              <input type="checkbox" checked={subtitles} onChange={(e) => setSubtitles(e.target.checked)} />
            </div>

            <div className="option-item row">
              <label>⭐️ Add Stickers</label>
              <input type="checkbox" checked={stickers} onChange={(e) => setStickers(e.target.checked)} />
            </div>

            <div className="option-item row">
              <label>🎵 Funny SFX</label>
              <input type="checkbox" checked={sfx} onChange={(e) => setSfx(e.target.checked)} />
            </div>
          </div>

          <button className="btn-magic" onClick={handleProcess} disabled={(inputMode === 'file' && !file) || (inputMode === 'youtube' && !youtubeUrl)}>
            🪄 Do the Magic!
          </button>
        </main>
      )}

      {isProcessing && (
        <div className="glass-panel loading-overlay">
          <div className="spinner"></div>
          <h2>Making magic happen...</h2>
          <p>{pollingStatus}</p>
          <p><em>(You can safely leave this page open, the server is doing the heavy lifting!)</em></p>
        </div>
      )}

      {resultVideoUrl && !isProcessing && (
        <div className="glass-panel result-card">
          <h2>🎉 Your Masterpiece is Ready! 🎉</h2>
          <video className="result-video" controls src={resultVideoUrl} />
          
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn-download" onClick={() => window.open(resultVideoUrl, '_blank')}>
              💾 Download Video
            </button>
            <button style={{ background: '#636e72' }} onClick={() => {
              setResultVideoUrl(null);
              setFile(null);
            }}>
              Try Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
