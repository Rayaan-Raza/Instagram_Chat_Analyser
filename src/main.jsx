import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import { DataProvider } from './contexts/DataContext.jsx'
import { ThemeProvider } from './contexts/ThemeContext.jsx'
import './index.css'

// Debug logging
console.log('Main.jsx loading...');
console.log('React version:', React.version);
console.log('Environment:', import.meta.env.MODE);

try {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  
  root.render(
    <React.StrictMode>
      <BrowserRouter>
        <ThemeProvider>
          <DataProvider>
            <App />
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
          </DataProvider>
        </ThemeProvider>
      </BrowserRouter>
    </React.StrictMode>,
  );
  
  console.log('App rendered successfully');
} catch (error) {
  console.error('Failed to render app:', error);
  
  // Fallback error display
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f3f4f6;
        font-family: Arial, sans-serif;
      ">
        <div style="
          background: white;
          padding: 2rem;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          max-width: 500px;
          text-align: center;
        ">
          <h1 style="color: #dc2626; margin-bottom: 1rem;">App Failed to Load</h1>
          <p style="color: #6b7280; margin-bottom: 1rem;">
            ${error.message || 'An unexpected error occurred'}
          </p>
          <button 
            onclick="window.location.reload()"
            style="
              background: #3b82f6;
              color: white;
              padding: 0.5rem 1rem;
              border: none;
              border-radius: 4px;
              cursor: pointer;
            "
          >
            Reload Page
          </button>
        </div>
      </div>
    `;
  }
} 