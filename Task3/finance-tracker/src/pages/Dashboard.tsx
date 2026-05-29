import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  Trash2, 
  TrendingUp, 
  PiggyBank, 
  Target, 
  AlertTriangle, 
  Calendar,
  DollarSign
} from 'lucide-react';
import { useTransactions } from '../context/TransactionContext';
import { useBudgets } from '../context/BudgetContext';
import { useGoals } from '../context/GoalContext';
import SummaryCards from '../components/dashboard/SummaryCards';
import { formatCurrency, formatDate, formatPercent } from '../utils/formatters';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  PieChart, 
  Pie, 
  Cell, 
  Legend 
} from 'recharts';

const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#6b7280'];

export default function Dashboard() {
  const { transactions, deleteTransaction } = useTransactions();
  const { budgets, getBudgetProgress } = useBudgets();
  const { goals } = useGoals();

  const currency = localStorage.getItem('finance-tracker-currency') || 'USD';

  // Get recent 5 transactions
  const recentTransactions = useMemo(() => {
    return transactions.slice(0, 5);
  }, [transactions]);

  // Generate daily trend data for the current month
  const monthlyTrendData = useMemo(() => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    
    return Array.from({ length: daysInMonth }, (_, i) => {
      const day = i + 1;
      const dayStr = String(day).padStart(2, '0');
      const monthStr = String(currentMonth + 1).padStart(2, '0');
      const datePrefix = `${currentYear}-${monthStr}-${dayStr}`;

      const dayTxs = transactions.filter(t => t.date.startsWith(datePrefix));
      const inc = dayTxs.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
      const exp = dayTxs.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);

      return {
        name: `${day}`,
        Income: inc,
        Expense: exp,
      };
    });
  }, [transactions]);

  // Aggregate expenses by category for pie chart
  const categoryExpenses = useMemo(() => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const monthlyExpenses = transactions.filter(t => {
      const d = new Date(t.date);
      return t.type === 'expense' && d.getMonth() === currentMonth && d.getFullYear() === currentYear;
    });

    const grouped: Record<string, number> = {};
    monthlyExpenses.forEach(t => {
      grouped[t.category] = (grouped[t.category] || 0) + t.amount;
    });

    return Object.entries(grouped)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [transactions]);

  // Budget alert notifications
  const criticalBudgets = useMemo(() => {
    const currentMonthStr = new Date().toISOString().slice(0, 7);
    return budgets
      .filter(b => b.monthYear === currentMonthStr)
      .map(b => {
        const { spent, percentage } = getBudgetProgress(b.category, b.monthYear);
        return { ...b, spent, percentage };
      })
      .filter(b => b.percentage >= 75) // Alert when 75% or more is spent
      .sort((a, b) => b.percentage - a.percentage);
  }, [budgets, getBudgetProgress]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent dark:from-primary-400 dark:to-indigo-400">
            Dashboard
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Welcome back! Here is your financial health summary for this month.
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500 bg-card border border-border px-3 py-1.5 rounded-lg shadow-sm w-fit">
          <Calendar className="h-4 w-4 text-primary-500" />
          <span>{new Date().toLocaleString('en-US', { month: 'long', year: 'numeric' })}</span>
        </div>
      </div>
      
      {/* Quick Summary Cards */}
      <SummaryCards />

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Monthly Trend Area Chart */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm lg:col-span-2 flex flex-col justify-between">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary-500" />
                Monthly Cash Flow
              </h2>
              <p className="text-xs text-gray-400">Daily income and expenses tracking</p>
            </div>
          </div>
          <div className="h-72 w-full">
            {transactions.length === 0 ? (
              <div className="flex h-full items-center justify-center rounded-lg border border-dashed border-border bg-gray-50/50 dark:bg-gray-800/20">
                <p className="text-sm text-gray-500">No transaction data to plot</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthlyTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="incomeColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="expenseColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-gray-200 dark:stroke-gray-800" />
                  <XAxis dataKey="name" fontSize={11} stroke="#6b7280" />
                  <YAxis fontSize={11} stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                      borderColor: '#e2e8f0',
                      borderRadius: '8px',
                      color: '#0f172a'
                    }} 
                    formatter={(value) => [formatCurrency(Number(value), currency), '']}
                  />
                  <Legend verticalAlign="top" height={36} iconType="circle" />
                  <Area type="monotone" dataKey="Income" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#incomeColor)" />
                  <Area type="monotone" dataKey="Expense" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#expenseColor)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Expense Category Breakdown Pie Chart */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <PiggyBank className="h-5 w-5 text-primary-500" />
              Expense Breakdown
            </h2>
            <p className="text-xs text-gray-400">Current month expenses by category</p>
          </div>
          <div className="h-64 w-full relative flex items-center justify-center my-4">
            {categoryExpenses.length === 0 ? (
              <div className="flex h-full w-full items-center justify-center rounded-lg border border-dashed border-border bg-gray-50/50 dark:bg-gray-800/20">
                <p className="text-sm text-gray-500">No monthly expenses recorded</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryExpenses}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {categoryExpenses.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                      borderColor: '#e2e8f0',
                      borderRadius: '8px',
                      color: '#0f172a'
                    }} 
                    formatter={(value) => [formatCurrency(Number(value), currency), '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          {categoryExpenses.length > 0 && (
            <div className="max-h-24 overflow-y-auto grid grid-cols-2 gap-2 text-xs">
              {categoryExpenses.slice(0, 4).map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-1.5">
                  <span 
                    className="h-2 w-2 rounded-full shrink-0" 
                    style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }} 
                  />
                  <span className="truncate max-w-[80px]" title={entry.name}>{entry.name}</span>
                  <span className="font-semibold text-gray-600 dark:text-gray-400">
                    {formatCurrency(entry.value, currency)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Transactions & Targets Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent Transactions List */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Recent Transactions</h2>
              <p className="text-xs text-gray-400">Quick list of your latest activities</p>
            </div>
            <Link 
              to="/transactions" 
              className="text-xs font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
            >
              View All →
            </Link>
          </div>
          
          {recentTransactions.length === 0 ? (
            <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-border bg-gray-50/50 dark:bg-gray-800/20">
              <p className="text-sm text-gray-500">No transactions recorded yet.</p>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-border bg-card">
              <ul className="divide-y divide-border">
                {recentTransactions.map((tx) => (
                  <li key={tx.id} className="flex items-center justify-between p-3.5 hover:bg-gray-50/50 dark:hover:bg-gray-800/20 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`rounded-full p-1.5 ${tx.type === 'income' ? 'bg-green-50 dark:bg-green-950/30 text-green-600' : 'bg-red-50 dark:bg-red-950/30 text-red-600'}`}>
                        {tx.type === 'income' ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-foreground">{tx.description}</p>
                        <div className="flex items-center gap-1.5 text-xs text-gray-400">
                          <span>{formatDate(tx.date)}</span>
                          <span>•</span>
                          <span className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-[10px]">
                            {tx.category}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-sm font-semibold ${tx.type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-foreground'}`}>
                        {tx.type === 'income' ? '+' : '-'}{formatCurrency(tx.amount, currency)}
                      </span>
                      <button 
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this transaction?')) {
                            deleteTransaction(tx.id);
                          }
                        }}
                        className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/30 dark:hover:text-red-400 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Budgets & Goals Highlights */}
        <div className="space-y-6">
          {/* Budget Warnings Panel */}
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-1">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Budget Watches
            </h2>
            <p className="text-xs text-gray-400 mb-4">Budgets over 75% utilized</p>

            {criticalBudgets.length === 0 ? (
              <div className="text-center py-6 text-sm text-gray-500 bg-gray-50/50 dark:bg-gray-800/10 rounded-lg border border-dashed border-border">
                🎉 All budgets are healthy!
              </div>
            ) : (
              <div className="space-y-3.5">
                {criticalBudgets.slice(0, 3).map(b => (
                  <div key={b.id} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium">
                      <span>{b.category}</span>
                      <span className={b.percentage >= 100 ? 'text-red-500 font-bold' : 'text-amber-500'}>
                        {formatCurrency(b.spent, currency)} / {formatCurrency(b.limit, currency)}
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-500 ${b.percentage >= 100 ? 'bg-red-500' : 'bg-amber-500'}`}
                        style={{ width: `${Math.min(b.percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Goal Overview Panel */}
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Target className="h-5 w-5 text-primary-500" />
                Savings Goals
              </h2>
              <Link 
                to="/goals" 
                className="text-xs font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              >
                Manage
              </Link>
            </div>

            {goals.length === 0 ? (
              <div className="text-center py-6 text-sm text-gray-500 bg-gray-50/50 dark:bg-gray-800/10 rounded-lg border border-dashed border-border">
                No active savings goals.
              </div>
            ) : (
              <div className="space-y-4">
                {goals.slice(0, 2).map(g => {
                  const pct = Math.min((g.currentAmount / g.targetAmount) * 100, 100);
                  return (
                    <div key={g.id} className="border border-border rounded-lg p-3 bg-gray-50/50 dark:bg-gray-800/20">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-semibold">{g.name}</span>
                        <span className="text-xs text-primary-600 dark:text-primary-400 font-bold">
                          {formatPercent(pct / 100)}
                        </span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden mb-2">
                        <div 
                          className="h-full bg-primary-600 rounded-full" 
                          style={{ width: `${pct}%` }} 
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-gray-400">
                        <span>Saved: {formatCurrency(g.currentAmount, currency)}</span>
                        <span>Target: {formatCurrency(g.targetAmount, currency)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
