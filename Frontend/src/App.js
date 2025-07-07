import React, { useState, useEffect } from 'react';
import StartRecognitionButton from './components/StartRecognitionButton'; // Make sure it's updated version
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('');

  useEffect(() => {
    // Check if backend is running
    fetch(`${process.env.REACT_APP_API_URL}/face_recognition`)
      .then(response => response.json())
      .then(data => setBackendStatus(data.message))
      .catch(error => setBackendStatus('Backend not connected'));
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Hostel Biometric</h1>
        <p className="backend-status">{backendStatus}</p>
      </header>
      <main className="app-main">
        <StartRecognitionButton />
      </main>
    </div>
  );
}

export default App;
