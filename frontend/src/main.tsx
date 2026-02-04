import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { RepositoryProvider } from './infrastructure/context/RepositoryContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RepositoryProvider>
      <App />
    </RepositoryProvider>
  </React.StrictMode>,
)