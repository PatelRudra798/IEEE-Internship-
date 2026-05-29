import React, { createContext, useContext, useMemo, useEffect } from 'react';
import type { Transaction } from '../types';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { useNotification } from './NotificationContext';
import { apiRequest } from '../utils/api';

interface TransactionContextType {
  transactions: Transaction[];
  addTransaction: (transaction: Omit<Transaction, 'id'>) => void;
  updateTransaction: (id: string, updated: Omit<Transaction, 'id'>) => void;
  deleteTransaction: (id: string) => void;
  getTransactionsByDateRange: (start: Date, end: Date) => Transaction[];
}

const TransactionContext = createContext<TransactionContextType | undefined>(undefined);

export function TransactionProvider({ children }: { children: React.ReactNode }) {
  const [transactions, setTransactions] = useLocalStorage<Transaction[]>('finance-tracker-transactions', []);
  const { addNotification } = useNotification();

  useEffect(() => {
    async function loadTransactions() {
      try {
        const backendTxs = await apiRequest<Transaction[]>('/transactions');
        setTransactions(backendTxs);
      } catch (err) {
        console.warn('Failed to load transactions from backend, falling back to local storage', err);
        // Toast warning to inform user
        addNotification('Running in local offline mode', 'warning');
      }
    }
    loadTransactions();
  }, []);

  const addTransaction = async (transactionData: Omit<Transaction, 'id'>) => {
    const newTransaction: Transaction = {
      ...transactionData,
      id: crypto.randomUUID(),
    };
    // Optimistic local update
    setTransactions((prev) => [newTransaction, ...prev]);
    
    try {
      await apiRequest<Transaction>('/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTransaction),
      });
      addNotification('Transaction added successfully', 'success');
    } catch (err) {
      console.warn('Failed to sync new transaction to backend', err);
      addNotification('Saved locally (Server offline)', 'info');
    }
  };

  const updateTransaction = async (id: string, updatedData: Omit<Transaction, 'id'>) => {
    const updatedTransaction: Transaction = {
      ...updatedData,
      id,
    };
    // Optimistic local update
    setTransactions((prev) =>
      prev.map((t) => (t.id === id ? updatedTransaction : t))
    );

    try {
      await apiRequest<Transaction>(`/transactions/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedTransaction),
      });
      addNotification('Transaction updated successfully', 'success');
    } catch (err) {
      console.warn('Failed to sync updated transaction to backend', err);
      addNotification('Updated locally (Server offline)', 'info');
    }
  };

  const deleteTransaction = async (id: string) => {
    // Optimistic local update
    setTransactions((prev) => prev.filter((t) => t.id !== id));

    try {
      await apiRequest(`/transactions/${id}`, {
        method: 'DELETE',
      });
      addNotification('Transaction deleted', 'info');
    } catch (err) {
      console.warn('Failed to sync transaction deletion to backend', err);
      addNotification('Deleted locally (Server offline)', 'info');
    }
  };

  const getTransactionsByDateRange = (start: Date, end: Date) => {
    return transactions.filter((t) => {
      const tDate = new Date(t.date);
      return tDate >= start && tDate <= end;
    });
  };

  const value = useMemo(
    () => ({
      transactions,
      addTransaction,
      updateTransaction,
      deleteTransaction,
      getTransactionsByDateRange,
    }),
    [transactions]
  );

  return (
    <TransactionContext.Provider value={value}>
      {children}
    </TransactionContext.Provider>
  );
}

export const useTransactions = () => {
  const context = useContext(TransactionContext);
  if (context === undefined) {
    throw new Error('useTransactions must be used within a TransactionProvider');
  }
  return context;
};
