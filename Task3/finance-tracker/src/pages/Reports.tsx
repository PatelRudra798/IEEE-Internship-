import { useState, useMemo } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Percent, 
  Award,
  Filter,
  Calendar,
  Layers
} from 'lucide-react';
import { useTransactions } from '../context/TransactionContext';
import { formatCurrency, formatPercent } from '../utils/formatters';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';

const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#6b7280'];

export default function Reports() {
  const { transactions } = useTransactions();
  const [timeframe, setTimeframe] = useState<'3m' | '6m' | '12m' | 'ytd'>('6m');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const currency = localStorage.getItem('finance-tracker-currency') || 'USD';

  // Get list of unique categories for the filters dropdown
  const uniqueCategories = useMemo(() => {
    const cats = new Set(transactions.map(t => t.category));
    return Array.from(cats);
  }, [transactions]);

  // Dynamic start date based on selected timeframe
  const timeframeStartDate = useMemo(() => {
    const now = new Date();
    let startDate = new Date();
    
    if (timeframe === '3m') startDate.setMonth(now.getMonth() - 2);
    else if (timeframe === '6m') startDate.setMonth(now.getMonth() - 5);
    else if (timeframe === '12m') startDate.setMonth(now.getMonth() - 11);
    else if (timeframe === 'ytd') startDate = new Date(now.getFullYear(), 0, 1);
    
    startDate.setDate(1);
    startDate.setHours(0, 0, 0, 0);
    return startDate;
  }, [timeframe]);

  // Aggregate stats over timeframe
  const summary = useMemo(() => {
    const start = timeframeStartDate;
    const periodTxs = transactions.filter(t => new Date(t.date) >= start);

    let totalIncome = 0;
    let totalExpense = 0;
    const expenseGrouped: Record<string, number> = {};

    periodTxs.forEach(t => {
      if (t.type === 'income') {
        totalIncome += t.amount;
      } else {
        totalExpense += t.amount;
        expenseGrouped[t.category] = (expenseGrouped[t.category] || 0) + t.amount;
      }
    });

    const netSavings = totalIncome - totalExpense;
    const savingsRate = totalIncome > 0 ? netSavings / totalIncome : 0;

    // Find highest expense category
    const highestExpense = Object.entries(expenseGrouped).reduce(
      (max, curr) => (curr[1] > max.value ? { name: curr[0], value: curr[1] } : max),
      { name: 'N/A', value: 0 }
    );

    return {
      totalIncome,
      totalExpense,
      netSavings,
      savingsRate,
      highestExpenseCategory: highestExpense,
    };
  }, [transactions, timeframeStartDate]);

  // Group historical data by month for the bar chart
  const monthlyBarData = useMemo(() => {
    const result = [];
    const now = new Date();
    
    let monthsCount = 6;
    if (timeframe === '3m') monthsCount = 3;
    if (timeframe === '12m') monthsCount = 12;
    if (timeframe === 'ytd') monthsCount = now.getMonth() + 1;

    for (let i = monthsCount - 1; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const year = d.getFullYear();
      const month = d.getMonth();
      const monthStr = String(month + 1).padStart(2, '0');
      const yearMonthPrefix = `${year}-${monthStr}`;

      const filtered = transactions.filter(t => t.date.startsWith(yearMonthPrefix));
      
      const inc = filtered.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
      const exp = filtered.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
      const label = d.toLocaleString('default', { month: 'short', year: '2-digit' });

      result.push({
        name: label,
        Income: inc,
        Expense: exp,
        Savings: inc - exp,
      });
    }
    return result;
  }, [transactions, timeframe]);

  // Group expenses by category for the pie chart
  const categoryChartData = useMemo(() => {
    const start = timeframeStartDate;
    const periodExpenses = transactions.filter(t => t.type === 'expense' && new Date(t.date) >= start);

    const grouped: Record<string, number> = {};
    periodExpenses.forEach(t => {
      if (categoryFilter === 'all' || t.category === categoryFilter) {
        grouped[t.category] = (grouped[t.category] || 0) + t.amount;
      }
    });

    return Object.entries(grouped)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [transactions, timeframeStartDate, categoryFilter]);

  // Generate dynamic insights
  const insights = useMemo(() => {
    const list = [];
    if (summary.savingsRate > 0.2) {
      list.push(`Great job! Your savings rate of ${formatPercent(summary.savingsRate)} is well above the recommended 20% benchmark.`);
    } else if (summary.savingsRate > 0) {
      list.push(`You are saving money, but a savings rate of ${formatPercent(summary.savingsRate)} leaves room for improvement. Try to trim non-essential expenses.`);
    } else if (summary.totalIncome > 0) {
      list.push(`Alert: Your net cash flow is negative. You spent ${formatCurrency(Math.abs(summary.netSavings), currency)} more than you earned in this period.`);
    }

    if (summary.highestExpenseCategory.value > 0) {
      const pctOfExpenses = summary.totalExpense > 0 ? summary.highestExpenseCategory.value / summary.totalExpense : 0;
      list.push(`Your top spending category is "${summary.highestExpenseCategory.name}", accounting for ${formatPercent(pctOfExpenses)} of total expenses.`);
    }

    if (list.length === 0) {
      list.push("Add more transaction records to unlock custom financial insights.");
    }
    return list;
  }, [summary, currency]);

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent dark:from-primary-400 dark:to-indigo-400">
            Reports & Analytics
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Deep dive analysis of your earnings and spending behavior.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 bg-card border border-border p-2 rounded-xl shadow-sm">
          <div className="flex items-center gap-1 text-xs font-semibold text-gray-500 px-1">
            <Filter className="h-3.5 w-3.5" />
            <span>Filters:</span>
          </div>

          {/* Timeframe selector */}
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5 text-xs">
            {([
              { id: '3m', label: '3M' },
              { id: '6m', label: '6M' },
              { id: '12m', label: '12M' },
              { id: 'ytd', label: 'YTD' }
            ] as const).map(opt => (
              <button
                key={opt.id}
                onClick={() => setTimeframe(opt.id)}
                className={`px-3 py-1 rounded-md font-medium transition-colors ${timeframe === opt.id ? 'bg-white dark:bg-gray-700 text-foreground shadow-sm' : 'text-gray-400 hover:text-foreground'}`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          {/* Category Dropdown */}
          <div className="relative">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="rounded-lg border border-border bg-transparent py-1 pl-2 pr-8 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="all">All Categories</option>
              {uniqueCategories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Net Savings */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-gray-500">Net Cash Flow</span>
            <div className={`p-1.5 rounded-lg ${summary.netSavings >= 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
              <DollarSign className="h-4 w-4" />
            </div>
          </div>
          <h3 className={`text-2xl font-bold ${summary.netSavings >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-500'}`}>
            {formatCurrency(summary.netSavings, currency)}
          </h3>
          <p className="text-[10px] text-gray-400 mt-1">Total surplus in selected timeframe</p>
        </div>

        {/* Savings Rate */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-gray-500">Savings Rate</span>
            <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
              <Percent className="h-4 w-4" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-foreground">
            {formatPercent(summary.savingsRate)}
          </h3>
          <p className="text-[10px] text-gray-400 mt-1">Percent of net income saved</p>
        </div>

        {/* Top Expenses */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-gray-500">Total Expenses</span>
            <div className="p-1.5 rounded-lg bg-red-50 text-red-600">
              <TrendingDown className="h-4 w-4" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-foreground">
            {formatCurrency(summary.totalExpense, currency)}
          </h3>
          <p className="text-[10px] text-gray-400 mt-1">Sum of all period expenses</p>
        </div>

        {/* Highest Expense Category */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-gray-500">Top Spend Area</span>
            <div className="p-1.5 rounded-lg bg-purple-50 text-purple-600">
              <Award className="h-4 w-4" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-foreground truncate" title={summary.highestExpenseCategory.name}>
            {summary.highestExpenseCategory.name}
          </h3>
          <p className="text-[10px] text-gray-400 mt-1">
            Total: {formatCurrency(summary.highestExpenseCategory.value, currency)}
          </p>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Income vs Expenses Bar Chart */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm lg:col-span-2 flex flex-col justify-between">
          <div className="mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary-500" />
              Cash Flow History
            </h2>
            <p className="text-xs text-gray-400">Monthly comparison of earnings vs spending</p>
          </div>
          <div className="h-80 w-full">
            {transactions.length === 0 ? (
              <div className="flex h-full items-center justify-center rounded-lg border border-dashed border-border bg-gray-50/50 dark:bg-gray-800/20">
                <p className="text-sm text-gray-500">No chart data available</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                  <Bar dataKey="Income" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Expense" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Expense Category Breakdown Chart */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Layers className="h-5 w-5 text-primary-500" />
              Category Breakdown
            </h2>
            <p className="text-xs text-gray-400">Expense distributions in selected timeframe</p>
          </div>
          <div className="h-64 w-full relative flex items-center justify-center my-4">
            {categoryChartData.length === 0 ? (
              <div className="flex h-full w-full items-center justify-center rounded-lg border border-dashed border-border bg-gray-50/50 dark:bg-gray-800/20">
                <p className="text-sm text-gray-500">No matching expense categories</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {categoryChartData.map((_, index) => (
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
          {categoryChartData.length > 0 && (
            <div className="max-h-24 overflow-y-auto grid grid-cols-2 gap-2 text-xs">
              {categoryChartData.slice(0, 4).map((entry, index) => (
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

      {/* Dynamic Insights Board */}
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
          <Calendar className="h-5 w-5 text-primary-500" />
          Financial Insights
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {insights.map((insight, i) => (
            <div key={i} className="flex items-start gap-3 rounded-lg border border-border p-4 bg-gray-50/50 dark:bg-gray-800/10 hover:shadow-sm transition-shadow">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-100 dark:bg-primary-950 text-xs font-bold text-primary-600 dark:text-primary-400">
                {i + 1}
              </span>
              <p className="text-sm leading-relaxed text-foreground">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
