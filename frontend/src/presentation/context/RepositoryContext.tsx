import React, { createContext, useContext } from 'react';
import type { IRequestRepository } from '../../domain/repositories/IRequestRepository';
import { HttpRequestRepository } from '../../infrastructure/adapters/HttpRequestRepository';

const RepositoryContext = createContext<IRequestRepository | null>(null);

export const RepositoryPort: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const repository = new HttpRequestRepository();
  
  return (
    <RepositoryContext.Provider value={repository}>
      {children}
    </RepositoryContext.Provider>
  );
};

export const useRepository = () => {
  const context = useContext(RepositoryContext);
  if (!context) {
    throw new Error("useRepository must be used within a RepositoryPort");
  }
  return context;
};