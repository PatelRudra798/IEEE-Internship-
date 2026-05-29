// Data Models for the Finance Tracker Application

export type TransactionType = 'income' | 'expense';
export type PriorityLevel = 'low' | 'medium' | 'high';
export type RecurringPattern = 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  category: string;
  description: string;
  date: string; // ISO string
  recurring: boolean;
  recurringPattern?: RecurringPattern;
}

export interface Budget {
  id: string;
  category: string;
  monthYear: string; // "YYYY-MM"
  limit: number;
  spent: number;
  alerts: boolean;
}

export interface Goal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  targetDate: string; // ISO string
  category: string;
  priority: PriorityLevel;
}

export interface UserPreferences {
  currency: string;
  theme: 'light' | 'dark' | 'system';
  language: string;
}

export interface User {
  preferences: UserPreferences;
}
