// Main entry point for the React application
// This file renders the App component into the root DOM element
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Get the root element from index.html and render the App component
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
