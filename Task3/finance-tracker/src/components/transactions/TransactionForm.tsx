import { useForm as useRHForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import type { Transaction } from '../../types';

const transactionSchema = z.object({
  type: z.enum(['income', 'expense']),
  amount: z.number().min(0.01, 'Amount must be greater than 0'),
  category: z.string().min(1, 'Category is required'),
  description: z.string().min(1, 'Description is required'),
  date: z.string().min(1, 'Date is required'),
});

type TransactionFormData = z.infer<typeof transactionSchema>;

interface TransactionFormProps {
  initialData?: Transaction;
  onSubmit: (data: Omit<Transaction, 'id' | 'recurring'>) => void;
  onCancel: () => void;
}

const CATEGORIES = {
  income: ['Salary', 'Freelance', 'Investments', 'Gift', 'Other'],
  expense: ['Food', 'Transport', 'Entertainment', 'Utilities', 'Health', 'Education', 'Shopping', 'Other'],
};

export default function TransactionForm({ initialData, onSubmit, onCancel }: TransactionFormProps) {
  const { register, handleSubmit, watch, formState: { errors } } = useRHForm<TransactionFormData>({
    resolver: zodResolver(transactionSchema),
    defaultValues: initialData ? {
      type: initialData.type,
      amount: initialData.amount,
      category: initialData.category,
      description: initialData.description,
      date: initialData.date.split('T')[0],
    } : {
      type: 'expense',
      date: new Date().toISOString().split('T')[0],
    },
  });

  const type = watch('type');
  const availableCategories = CATEGORIES[type] || [];

  const handleFormSubmit = (data: TransactionFormData) => {
    onSubmit({
      ...data,
      date: new Date(data.date).toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {/* Type Toggle */}
      <div className="grid grid-cols-2 gap-4">
        <label className={`flex cursor-pointer items-center justify-center rounded-lg border p-3 font-medium transition-colors ${type === 'expense' ? 'border-red-500 bg-red-50 text-red-700 dark:bg-red-900/30' : 'border-border bg-card'}`}>
          <input type="radio" value="expense" className="sr-only" {...register('type')} />
          Expense
        </label>
        <label className={`flex cursor-pointer items-center justify-center rounded-lg border p-3 font-medium transition-colors ${type === 'income' ? 'border-green-500 bg-green-50 text-green-700 dark:bg-green-900/30' : 'border-border bg-card'}`}>
          <input type="radio" value="income" className="sr-only" {...register('type')} />
          Income
        </label>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Amount</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
          <input 
            type="number" 
            step="0.01"
            className="w-full rounded-lg border border-border bg-transparent p-2 pl-8 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
            placeholder="0.00"
            {...register('amount', { valueAsNumber: true })} 
          />
        </div>
        {errors.amount && <p className="mt-1 text-sm text-red-500">{errors.amount.message}</p>}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <input 
          type="text" 
          className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
          placeholder="Grocery shopping"
          {...register('description')} 
        />
        {errors.description && <p className="mt-1 text-sm text-red-500">{errors.description.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Category</label>
          <select 
            className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            {...register('category')}
          >
            <option value="">Select...</option>
            {availableCategories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          {errors.category && <p className="mt-1 text-sm text-red-500">{errors.category.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Date</label>
          <input 
            type="date" 
            className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
            {...register('date')} 
          />
          {errors.date && <p className="mt-1 text-sm text-red-500">{errors.date.message}</p>}
        </div>
      </div>

      <div className="mt-6 flex justify-end gap-3 pt-4">
        <button type="button" onClick={onCancel} className="rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800">
          Cancel
        </button>
        <button type="submit" className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          {initialData ? 'Update Transaction' : 'Add Transaction'}
        </button>
      </div>
    </form>
  );
}
