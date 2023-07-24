"use client";

import './globals.css'
import React, { useState } from 'react';
import { Container, Button } from 'react-bootstrap';
import Grid from '../components/grid';

const Home = () => {
  const [message, setMessage] = useState('');
  const dataToSend = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
  ];

  const handleClick = () => {
    // Make the POST request to Flask backend
    fetch('/api/post-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dataToSend), // Convert the 2D array to a JSON string
    })
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error('Error:', error));
  };

  return (
    <Container>
      <h1>Wildfire Evacuation</h1>
      <p>Simulating wildfires with reinforcement learning!</p>
      <Grid />
      <br />
      <Button onClick={handleClick} variant="danger">Update</Button>
      <p>Response from Flask backend: {message}</p>
    </Container>
  );
};

export default Home;