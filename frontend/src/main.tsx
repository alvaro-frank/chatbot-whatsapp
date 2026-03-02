import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { RepositoryPort } from './presentation/context/RepositoryContext'
import { UseCasePort } from './presentation/context/UseCaseContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RepositoryPort>
      <UseCasePort>
        <App />
      </UseCasePort>
    </RepositoryPort>
  </React.StrictMode >,
)