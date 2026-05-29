import { useState } from 'react';
import { Edit2, Trash2, ArrowUpRight, ArrowDownRight, Search } from 'lucide-react';
import type { Transaction } from '../../types';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface TransactionListProps {
  transactions: Transaction[];
  onEdit: (transaction: Transaction) => void;
  onDelete: (id: string) => void;
}

export default function TransactionList({ transactions, onEdit, onDelete }: TransactionListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all');

  const filteredTransactions = transactions.filter((t) => {
    const matchesSearch = t.description.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          t.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || t.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-4">
      {/* Filters and Search */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search transactions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-border bg-card p-2 pl-10 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'income', 'expense'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`rounded-lg px-4 py-2 text-sm font-medium capitalize transition-colors ${
                filterType === type
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/50 dark:text-primary-100'
                  : 'bg-card text-foreground border border-border hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        {filteredTransactions.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            No transactions found.
          </div>
        ) : (
          <ul className="divide-y divide-border">
            {filteredTransactions.map((transaction) => (
              <li key={transaction.id} className="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className={`rounded-full p-2 ${transaction.type === 'income' ? 'bg-green-100 dark:bg-green-900/30 text-green-600' : 'bg-red-100 dark:bg-red-900/30 text-red-600'}`}>
                    {transaction.type === 'income' ? <ArrowUpRight className="h-5 w-5" /> : <ArrowDownRight className="h-5 w-5" />}
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{transaction.description}</p>
                    <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                      <span>{formatDate(transaction.date)}</span>
                      <span>•</span>
                      <span className="rounded-full bg-gray-100 dark:bg-gray-800 px-2 py-0.5 text-xs">
                        {transaction.category}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <span className={`font-semibold ${transaction.type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-foreground'}`}>
                    {transaction.type === 'income' ? '+' : '-'}{formatCurrency(transaction.amount)}
                  </span>
                  
                  <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100 lg:opacity-100">
                    <button onClick={() => onEdit(transaction)} className="p-1.5 text-gray-400 hover:text-primary-600 transition-colors rounded-md hover:bg-primary-50 dark:hover:bg-primary-900/30">
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button onClick={() => {
                      if (confirm('Are you sure you want to delete this transaction?')) {
                        onDelete(transaction.id);
                      }
                    }} className="p-1.5 text-gray-400 hover:text-red-600 transition-colors rounded-md hover:bg-red-50 dark:hover:bg-red-900/30">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
