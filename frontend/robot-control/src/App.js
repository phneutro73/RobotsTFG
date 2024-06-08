import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [robot, setRobot] = useState('');
  const [destination, setDestination] = useState('');
  const [videoSrc, setVideoSrc] = useState('');

  const handleStart = async () => {
    try {
      const response = await axios.post('http://localhost:5000/start_navigation', {
        robot_id: robot,
        target_marker_id: destination
      });

      if (response.data.status === 'completed') {
        alert("Navigation completed!");
        setVideoSrc('');
      } else {
        setVideoSrc('http://localhost:5000/start_navigation');
      }
    } catch (error) {
      console.error("Error starting the script", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Robotics Control Interface</h1>
        <div>
          <label>Select Robot:</label>
          <select value={robot} onChange={(e) => setRobot(e.target.value)}>
            <option value="">--Select--</option>
            <option value="71">Robot 1</option>
            <option value="101">Robot 2</option>
          </select>
        </div>
        <div>
          <label>Select Destination:</label>
          <select value={destination} onChange={(e) => setDestination(e.target.value)}>
            <option value="">--Select--</option>
            <option value="73">Marker 73</option>
            <option value="76">Marker 76</option>
            <option value="101">Marker 101</option>
            <option value="102">Marker 102</option>
          </select>
        </div>
        <button onClick={handleStart} disabled={!robot || !destination}>Start Navigation</button>
        {videoSrc && <img src={videoSrc} alt="Video Feed" />}
      </header>
    </div>
  );
}

export default App;


