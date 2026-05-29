import React, { createContext, useContext, useMemo, useEffect } from 'react';
import type { Budget } from '../types';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { useNotification } from './NotificationContext';
import { useTransactions } from './TransactionContext';
import { apiRequest } from '../utils/api';

interface BudgetContextType {
  budgets: Budget[];
  addBudget: (budget: Omit<Budget, 'id' | 'spent'>) => void;
  updateBudget: (id: string, updated: Omit<Budget, 'id' | 'spent'>) => void;
  deleteBudget: (id: string) => void;
  getBudgetProgress: (categoryId: string, monthYear: string) => { spent: number; limit: number; percentage: number };
}

const BudgetContext = createContext<BudgetContextType | undefined>(undefined);

export function BudgetProvider({ children }: { children: React.ReactNode }) {
  const [budgets, setBudgets] = useLocalStorage<Budget[]>('finance-tracker-budgets', []);
  const { addNotification } = useNotification();
  const { transactions } = useTransactions();

  useEffect(() => {
    async function loadBudgets() {
      try {
        const backendBudgets = await apiRequest<Budget[]>('/budgets');
        setBudgets(backendBudgets);
      } catch (err) {
        console.warn('Failed to load budgets from backend, falling back to local storage', err);
      }
    }
    loadBudgets();
  }, []);

  // Dynamically calculate spent amount based on actual transactions
  const calculatedBudgets = useMemo(() => {
    return budgets.map(budget => {
      // Find all expense transactions for this category in the budget's month
      const spent = transactions
        .filter(t => t.type === 'expense' && t.category === budget.category && t.date.startsWith(budget.monthYear))
        .reduce((sum, t) => sum + t.amount, 0);

      return { ...budget, spent };
    });
  }, [budgets, transactions]);

  const addBudget = async (budgetData: Omit<Budget, 'id' | 'spent'>) => {
    // Check if budget already exists for category and month
    const exists = budgets.find(b => b.category === budgetData.category && b.monthYear === budgetData.monthYear);
    if (exists) {
      addNotification(`A budget for ${budgetData.category} already exists this month.`, 'error');
      return;
    }

    const newBudget: Budget = {
      ...budgetData,
      id: crypto.randomUUID(),
      spent: 0,
    };
    // Optimistic local update
    setBudgets((prev) => [...prev, newBudget]);

    try {
      const { spent, ...body } = newBudget;
      await apiRequest<Budget>('/budgets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      addNotification('Budget created successfully', 'success');
    } catch (err) {
      console.warn('Failed to sync new budget to backend', err);
      addNotification('Budget saved locally (Server offline)', 'info');
    }
  };

  const updateBudget = async (id: string, updatedData: Omit<Budget, 'id' | 'spent'>) => {
    const newBudget: Budget = {
      ...updatedData,
      id,
      spent: 0,
    };
    // Optimistic local update
    setBudgets((prev) =>
      prev.map((b) => (b.id === id ? newBudget : b))
    );

    try {
      const { spent, ...body } = newBudget;
      await apiRequest<Budget>(`/budgets/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      addNotification('Budget updated successfully', 'success');
    } catch (err) {
      console.warn('Failed to sync updated budget to backend', err);
      addNotification('Updated locally (Server offline)', 'info');
    }
  };

  const deleteBudget = async (id: string) => {
    // Optimistic local update
    setBudgets((prev) => prev.filter((b) => b.id !== id));

    try {
      await apiRequest(`/budgets/${id}`, {
        method: 'DELETE',
      });
      addNotification('Budget deleted', 'info');
    } catch (err) {
      console.warn('Failed to sync deleted budget to backend', err);
      addNotification('Deleted locally (Server offline)', 'info');
    }
  };

  const getBudgetProgress = (category: string, monthYear: string) => {
    const budget = calculatedBudgets.find(b => b.category === category && b.monthYear === monthYear);
    if (!budget) return { spent: 0, limit: 0, percentage: 0 };
    return {
      spent: budget.spent,
      limit: budget.limit,
      percentage: Math.min((budget.spent / budget.limit) * 100, 100)
    };
  };

  return (
    <BudgetContext.Provider value={{
      budgets: calculatedBudgets,
      addBudget,
      updateBudget,
      deleteBudget,
      getBudgetProgress
    }}>
      {children}
    </BudgetContext.Provider>
  );
}

export const useBudgets = () => {
  const context = useContext(BudgetContext);
  if (context === undefined) {
    throw new Error('useBudgets must be used within a BudgetProvider');
  }
  return context;
};
