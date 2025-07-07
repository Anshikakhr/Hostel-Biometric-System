import React, { useState } from 'react';

export default function HostelEntryExitButton() {
  const [message, setMessage] = useState('');

  const handleStart = async () => {
    try {
      const response = await fetch('http://localhost:5000/face_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: localStorage.getItem('capturedImage')
        })
      });

      const data = await response.json();
      if (response.ok) {
        setMessage(`${data.name} - ${data.message}`);
      } else {
        setMessage('Error: ' + data.message);
      }
    } catch (err) {
      setMessage('Fetch error: ' + err.message);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: 50 }}>
      <button
        onClick={handleStart}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: 'rgb(35,73,154)',
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
        }}
      >
        Capture Face
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}
