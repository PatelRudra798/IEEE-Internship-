import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import type { Budget } from '../../types';

const CATEGORIES = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Health', 'Education', 'Shopping', 'Other'];

const budgetSchema = z.object({
  category: z.string().min(1, 'Category is required'),
  monthYear: z.string().min(1, 'Month is required'),
  limit: z.number().min(1, 'Budget limit must be greater than 0'),
  alerts: z.boolean(),
});

type BudgetFormData = z.infer<typeof budgetSchema>;

interface BudgetFormProps {
  initialData?: Budget;
  onSubmit: (data: Omit<Budget, 'id' | 'spent'>) => void;
  onCancel: () => void;
}

export default function BudgetForm({ initialData, onSubmit, onCancel }: BudgetFormProps) {
  const currentMonthYear = new Date().toISOString().slice(0, 7); // YYYY-MM format

  const { register, handleSubmit, formState: { errors } } = useForm<BudgetFormData>({
    resolver: zodResolver(budgetSchema),
    defaultValues: initialData ? {
      category: initialData.category,
      monthYear: initialData.monthYear,
      limit: initialData.limit,
      alerts: initialData.alerts,
    } : {
      monthYear: currentMonthYear,
      alerts: true,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium">Category</label>
        <select 
          className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          {...register('category')}
          disabled={!!initialData} // Usually you don't change the category of an existing budget
        >
          <option value="">Select category...</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        {errors.category && <p className="mt-1 text-sm text-red-500">{errors.category.message}</p>}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Month</label>
        <input 
          type="month" 
          className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          {...register('monthYear')}
          disabled={!!initialData}
        />
        {errors.monthYear && <p className="mt-1 text-sm text-red-500">{errors.monthYear.message}</p>}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Budget Limit</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
          <input 
            type="number" 
            step="1"
            className="w-full rounded-lg border border-border bg-transparent p-2 pl-8 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
            placeholder="0.00"
            {...register('limit', { valueAsNumber: true })} 
          />
        </div>
        {errors.limit && <p className="mt-1 text-sm text-red-500">{errors.limit.message}</p>}
      </div>

      <div className="flex items-center gap-2 pt-2">
        <input 
          type="checkbox" 
          id="alerts"
          className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          {...register('alerts')}
        />
        <label htmlFor="alerts" className="text-sm font-medium">
          Enable overspending alerts
        </label>
      </div>

      <div className="mt-6 flex justify-end gap-3 pt-4">
        <button type="button" onClick={onCancel} className="rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800">
          Cancel
        </button>
        <button type="submit" className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          {initialData ? 'Update Budget' : 'Create Budget'}
        </button>
      </div>
    </form>
  );
}
