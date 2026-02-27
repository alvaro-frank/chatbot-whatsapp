import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { RepositoryProvider } from './presentation/context/RepositoryContext'
import { UseCaseProvider } from './presentation/context/UseCaseContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RepositoryProvider>
      <UseCaseProvider>
        <App />
      </UseCaseProvider>
    </RepositoryProvider>
  </React.StrictMode >,
)