import { useState } from 'react';
import { Plus, Edit2, Trash2, Target, PlusCircle, Trophy } from 'lucide-react';
import { useGoals } from '../context/GoalContext';
import type { Goal } from '../types';
import Modal from '../components/common/Modal';
import GoalForm from '../components/goals/GoalForm';
import { formatCurrency, formatPercent, formatDate } from '../utils/formatters';

export default function Goals() {
  const { goals, addGoal, updateGoal, deleteGoal, addFundsToGoal } = useGoals();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | undefined>();
  const [addFundsGoal, setAddFundsGoal] = useState<string | null>(null);
  const [fundsAmount, setFundsAmount] = useState('');

  const handleOpenModal = (goal?: Goal) => {
    setEditingGoal(goal);
    setIsModalOpen(true);
  };

  const handleSubmit = (data: Omit<Goal, 'id' | 'currentAmount'>) => {
    if (editingGoal) {
      updateGoal(editingGoal.id, data);
    } else {
      addGoal(data);
    }
    setIsModalOpen(false);
  };

  const handleAddFunds = (e: React.FormEvent) => {
    e.preventDefault();
    if (addFundsGoal && fundsAmount && !isNaN(Number(fundsAmount))) {
      addFundsToGoal(addFundsGoal, Number(fundsAmount));
      setAddFundsGoal(null);
      setFundsAmount('');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Savings Goals</h1>
          <p className="text-gray-500 dark:text-gray-400">Track progress toward your financial targets.</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2 font-medium text-white shadow-sm hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Create Goal
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {goals.length === 0 ? (
          <div className="col-span-full rounded-xl border border-dashed border-border bg-card p-12 text-center text-gray-500 dark:text-gray-400">
            No active savings goals. Create one to start saving!
          </div>
        ) : (
          goals.map((goal) => {
            const percentage = Math.min((goal.currentAmount / goal.targetAmount) * 100, 100);
            const isCompleted = percentage >= 100;

            return (
              <div key={goal.id} className={`relative flex flex-col rounded-xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md ${isCompleted ? 'border-green-500 shadow-green-100 dark:shadow-none' : ''}`}>
                {isCompleted && (
                  <div className="absolute -top-3 -right-3 rounded-full bg-green-500 p-2 text-white shadow-lg">
                    <Trophy className="h-5 w-5" />
                  </div>
                )}
                
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-primary-100 p-2 text-primary-600 dark:bg-primary-900/50">
                      <Target className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{goal.name}</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Target: {formatDate(goal.targetDate)}</p>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100 lg:opacity-100">
                    <button onClick={() => setAddFundsGoal(goal.id)} className="p-1.5 text-gray-400 hover:text-green-600" title="Add Funds">
                      <PlusCircle className="h-4 w-4" />
                    </button>
                    <button onClick={() => handleOpenModal(goal)} className="p-1.5 text-gray-400 hover:text-primary-600" title="Edit">
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button onClick={() => deleteGoal(goal.id)} className="p-1.5 text-gray-400 hover:text-red-600" title="Delete">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="mb-2 flex items-end justify-between mt-4">
                  <div>
                    <p className="text-2xl font-bold text-foreground">
                      {formatCurrency(goal.currentAmount)}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Saved</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-foreground">{formatCurrency(goal.targetAmount)}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Goal</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-auto pt-4">
                  <div className="mb-1 flex justify-between text-xs font-medium">
                    <span className={isCompleted ? 'text-green-500' : 'text-primary-600'}>
                      {formatPercent(percentage / 100)} completed
                    </span>
                    <span className="text-gray-500">
                      {formatCurrency(Math.max(0, goal.targetAmount - goal.currentAmount))} to go
                    </span>
                  </div>
                  <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                    <div 
                      className={`h-full transition-all duration-1000 ease-out ${isCompleted ? 'bg-green-500' : 'bg-primary-600'}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Add Funds Modal */}
      <Modal isOpen={!!addFundsGoal} onClose={() => { setAddFundsGoal(null); setFundsAmount(''); }} title="Add Funds to Goal">
        <form onSubmit={handleAddFunds} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Amount to Add</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
              <input 
                type="number" 
                step="0.01"
                required
                min="0.01"
                value={fundsAmount}
                onChange={(e) => setFundsAmount(e.target.value)}
                className="w-full rounded-lg border border-border bg-transparent p-2 pl-8 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
                placeholder="100.00"
              />
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-3 pt-4">
            <button type="button" onClick={() => { setAddFundsGoal(null); setFundsAmount(''); }} className="rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800">
              Cancel
            </button>
            <button type="submit" className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">
              Add Funds
            </button>
          </div>
        </form>
      </Modal>

      {/* Create/Edit Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title={editingGoal ? 'Edit Goal' : 'Create Goal'}>
        <GoalForm initialData={editingGoal} onSubmit={handleSubmit} onCancel={() => setIsModalOpen(false)} />
      </Modal>
    </div>
  );
}
