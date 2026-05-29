import { useState } from 'react';
import { Plus, Edit2, Trash2, AlertTriangle } from 'lucide-react';
import { useBudgets } from '../context/BudgetContext';
import type { Budget } from '../types';
import Modal from '../components/common/Modal';
import BudgetForm from '../components/budgets/BudgetForm';
import { formatCurrency, formatPercent } from '../utils/formatters';

export default function Budgets() {
  const { budgets, addBudget, updateBudget, deleteBudget, getBudgetProgress } = useBudgets();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | undefined>();

  const currentMonth = new Date().toISOString().slice(0, 7);
  // Optional: filter budgets to only show current month, or add a month selector
  const activeBudgets = budgets.filter(b => b.monthYear === currentMonth);

  const handleOpenModal = (budget?: Budget) => {
    setEditingBudget(budget);
    setIsModalOpen(true);
  };

  const handleSubmit = (data: Omit<Budget, 'id' | 'spent'>) => {
    if (editingBudget) {
      updateBudget(editingBudget.id, data);
    } else {
      addBudget(data);
    }
    setIsModalOpen(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Budgets</h1>
          <p className="text-gray-500 dark:text-gray-400">Track and manage your monthly spending limits.</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2 font-medium text-white shadow-sm hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Create Budget
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {activeBudgets.length === 0 ? (
          <div className="col-span-full rounded-xl border border-dashed border-border bg-card p-12 text-center text-gray-500 dark:text-gray-400">
            No budgets set for this month. Create one to start tracking your spending!
          </div>
        ) : (
          activeBudgets.map((budget) => {
            const { spent, percentage } = getBudgetProgress(budget.category, budget.monthYear);
            const isExceeded = spent > budget.limit;
            const isNearLimit = percentage >= 80 && !isExceeded;

            return (
              <div key={budget.id} className="flex flex-col rounded-xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-lg">{budget.category}</h3>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100 lg:opacity-100">
                    <button onClick={() => handleOpenModal(budget)} className="p-1.5 text-gray-400 hover:text-primary-600">
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button onClick={() => deleteBudget(budget.id)} className="p-1.5 text-gray-400 hover:text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="mb-2 flex items-end justify-between">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Spent</p>
                    <p className={`text-2xl font-bold ${isExceeded ? 'text-red-600 dark:text-red-400' : 'text-foreground'}`}>
                      {formatCurrency(spent)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500 dark:text-gray-400">Limit</p>
                    <p className="font-medium text-foreground">{formatCurrency(budget.limit)}</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-auto pt-4">
                  <div className="mb-1 flex justify-between text-xs font-medium">
                    <span className={isExceeded ? 'text-red-500' : isNearLimit ? 'text-yellow-500' : 'text-green-500'}>
                      {formatPercent(percentage / 100)} used
                    </span>
                    <span className="text-gray-500">
                      {formatCurrency(Math.max(0, budget.limit - spent))} left
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                    <div 
                      className={`h-full transition-all duration-500 ${
                        isExceeded ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>

                {budget.alerts && isExceeded && (
                  <div className="mt-4 flex items-center gap-2 rounded-lg bg-red-50 dark:bg-red-900/30 p-2 text-sm text-red-600 dark:text-red-400">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    <p>Budget limit exceeded!</p>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingBudget ? 'Edit Budget' : 'Create Budget'}>
        <BudgetForm initialData={editingBudget} onSubmit={handleSubmit} onCancel={() => setIsModalOpen(false)} />
      </Modal>
    </div>
  );
}
