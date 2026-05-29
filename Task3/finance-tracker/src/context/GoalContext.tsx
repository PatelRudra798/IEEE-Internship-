import React, { createContext, useContext, useEffect } from 'react';
import type { Goal } from '../types';
import { useLocalStorage } from '../hooks/useLocalStorage';
import { useNotification } from './NotificationContext';
import { apiRequest } from '../utils/api';

interface GoalContextType {
  goals: Goal[];
  addGoal: (goal: Omit<Goal, 'id' | 'currentAmount'>) => void;
  updateGoal: (id: string, updated: Partial<Omit<Goal, 'id'>>) => void;
  deleteGoal: (id: string) => void;
  addFundsToGoal: (id: string, amount: number) => void;
}

const GoalContext = createContext<GoalContextType | undefined>(undefined);

export function GoalProvider({ children }: { children: React.ReactNode }) {
  const [goals, setGoals] = useLocalStorage<Goal[]>('finance-tracker-goals', []);
  const { addNotification } = useNotification();

  useEffect(() => {
    async function loadGoals() {
      try {
        const backendGoals = await apiRequest<Goal[]>('/goals');
        setGoals(backendGoals);
      } catch (err) {
        console.warn('Failed to load goals from backend, falling back to local storage', err);
      }
    }
    loadGoals();
  }, []);

  const addGoal = async (goalData: Omit<Goal, 'id' | 'currentAmount'>) => {
    const newGoal: Goal = {
      ...goalData,
      id: crypto.randomUUID(),
      currentAmount: 0,
    };
    // Optimistic local update
    setGoals((prev) => [...prev, newGoal]);

    try {
      await apiRequest<Goal>('/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newGoal),
      });
      addNotification('Savings goal created', 'success');
    } catch (err) {
      console.warn('Failed to sync new goal to backend', err);
      addNotification('Goal saved locally (Server offline)', 'info');
    }
  };

  const updateGoal = async (id: string, updatedData: Partial<Omit<Goal, 'id'>>) => {
    const targetGoal = goals.find((g) => g.id === id);
    if (!targetGoal) return;
    const updatedGoal = { ...targetGoal, ...updatedData };

    // Optimistic local update
    setGoals((prev) =>
      prev.map((g) => (g.id === id ? updatedGoal : g))
    );

    try {
      await apiRequest<Goal>(`/goals/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedGoal),
      });
      addNotification('Goal updated', 'success');
    } catch (err) {
      console.warn('Failed to sync updated goal to backend', err);
      addNotification('Updated locally (Server offline)', 'info');
    }
  };

  const deleteGoal = async (id: string) => {
    // Optimistic local update
    setGoals((prev) => prev.filter((g) => g.id !== id));

    try {
      await apiRequest(`/goals/${id}`, {
        method: 'DELETE',
      });
      addNotification('Goal deleted', 'info');
    } catch (err) {
      console.warn('Failed to sync goal deletion to backend', err);
      addNotification('Deleted locally (Server offline)', 'info');
    }
  };

  const addFundsToGoal = async (id: string, amount: number) => {
    let updatedGoal: Goal | null = null;
    
    setGoals((prev) =>
      prev.map((g) => {
        if (g.id === id) {
          const newAmount = g.currentAmount + amount;
          if (newAmount >= g.targetAmount && g.currentAmount < g.targetAmount) {
            addNotification(`🎉 Congratulations! You reached your goal: ${g.name}`, 'success');
          }
          updatedGoal = { ...g, currentAmount: newAmount };
          return updatedGoal;
        }
        return g;
      })
    );

    if (updatedGoal) {
      try {
        await apiRequest<Goal>(`/goals/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedGoal),
        });
      } catch (err) {
        console.warn('Failed to sync goal funds to backend', err);
        addNotification('Funds saved locally (Server offline)', 'info');
      }
    }
  };

  return (
    <GoalContext.Provider value={{
      goals,
      addGoal,
      updateGoal,
      deleteGoal,
      addFundsToGoal
    }}>
      {children}
    </GoalContext.Provider>
  );
}

export const useGoals = () => {
  const context = useContext(GoalContext);
  if (context === undefined) {
    throw new Error('useGoals must be used within a GoalProvider');
  }
  return context;
};
