"use client";

import React, { useState, useEffect } from 'react';

const Home = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Fetch data from Flask backend API when the component mounts
    fetch('/api/hello')
      .then((response) => response.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error('Error:', error));
  }, []);

  return (
    <div>
      <h1>Next.js + Flask App</h1>
      <p>Message from Flask backend: {message}</p>
    </div>
  );
};

export default Home;