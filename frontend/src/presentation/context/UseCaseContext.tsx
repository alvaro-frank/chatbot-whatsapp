// src/presentation/context/UseCaseContext.tsx
import React, { createContext, useContext, useMemo } from 'react';
import { useRepository } from './RepositoryContext';
import { GetPendingRequestsUseCase } from '../../application/GetPendingRequestsUseCase';
import { ApproveRequestUseCase } from '../../application/ApproveRequestUseCase';
import { RejectRequestUseCase } from '../../application/RejectRequestUseCase';

const UseCaseContext = createContext<any>(null);

export const UseCasePort: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const repo = useRepository();

  const useCases = useMemo(() => ({
    getPendingRequests: new GetPendingRequestsUseCase(repo),
    approveRequest: new ApproveRequestUseCase(repo),
    rejectRequest: new RejectRequestUseCase(repo)
  }), [repo]);

  return (
    <UseCaseContext.Provider value={useCases}>
      {children}
    </UseCaseContext.Provider>
  );
};

export const useUseCases = () => useContext(UseCaseContext);