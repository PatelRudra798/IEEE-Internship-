import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import type { Goal } from '../../types';

const goalSchema = z.object({
  name: z.string().min(1, 'Goal name is required'),
  targetAmount: z.number().min(1, 'Target amount must be greater than 0'),
  targetDate: z.string().min(1, 'Target date is required'),
  category: z.string().min(1, 'Category is required'),
  priority: z.enum(['low', 'medium', 'high']),
});

type GoalFormData = z.infer<typeof goalSchema>;

interface GoalFormProps {
  initialData?: Goal;
  onSubmit: (data: Omit<Goal, 'id' | 'currentAmount'>) => void;
  onCancel: () => void;
}

export default function GoalForm({ initialData, onSubmit, onCancel }: GoalFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<GoalFormData>({
    resolver: zodResolver(goalSchema),
    defaultValues: initialData ? {
      name: initialData.name,
      targetAmount: initialData.targetAmount,
      targetDate: initialData.targetDate.split('T')[0],
      category: initialData.category,
      priority: initialData.priority,
    } : {
      priority: 'medium',
      targetDate: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
    },
  });

  const handleFormSubmit = (data: GoalFormData) => {
    onSubmit({
      ...data,
      targetDate: new Date(data.targetDate).toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium">Goal Name</label>
        <input 
          type="text" 
          className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
          placeholder="New Car"
          {...register('name')} 
        />
        {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Target Amount</label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
            <input 
              type="number" 
              step="1"
              className="w-full rounded-lg border border-border bg-transparent p-2 pl-8 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
              placeholder="0.00"
              {...register('targetAmount', { valueAsNumber: true })} 
            />
          </div>
          {errors.targetAmount && <p className="mt-1 text-sm text-red-500">{errors.targetAmount.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Target Date</label>
          <input 
            type="date" 
            className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" 
            {...register('targetDate')} 
          />
          {errors.targetDate && <p className="mt-1 text-sm text-red-500">{errors.targetDate.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Category</label>
          <select 
            className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            {...register('category')}
          >
            <option value="">Select...</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Housing">Housing</option>
            <option value="Emergency Fund">Emergency Fund</option>
            <option value="Travel">Travel</option>
            <option value="Retirement">Retirement</option>
            <option value="Other">Other</option>
          </select>
          {errors.category && <p className="mt-1 text-sm text-red-500">{errors.category.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Priority</label>
          <select 
            className="w-full rounded-lg border border-border bg-transparent p-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            {...register('priority')}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </div>

      <div className="mt-6 flex justify-end gap-3 pt-4">
        <button type="button" onClick={onCancel} className="rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800">
          Cancel
        </button>
        <button type="submit" className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
          {initialData ? 'Update Goal' : 'Create Goal'}
        </button>
      </div>
    </form>
  );
}
