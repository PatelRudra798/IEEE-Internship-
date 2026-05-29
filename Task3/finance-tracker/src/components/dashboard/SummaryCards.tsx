import { useMemo } from 'react';
import { ArrowDownRight, ArrowUpRight, DollarSign, Wallet } from 'lucide-react';
import { useTransactions } from '../../context/TransactionContext';
import { formatCurrency, formatPercent } from '../../utils/formatters';

export default function SummaryCards() {
  const { transactions } = useTransactions();

  const { income, expense, balance, savingsRate } = useMemo(() => {
    // Current month filters
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const monthlyTransactions = transactions.filter((t) => {
      const d = new Date(t.date);
      return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
    });

    let inc = 0;
    let exp = 0;

    monthlyTransactions.forEach((t) => {
      if (t.type === 'income') inc += t.amount;
      if (t.type === 'expense') exp += t.amount;
    });

    const bal = inc - exp;
    const rate = inc > 0 ? bal / inc : 0;

    return { income: inc, expense: exp, balance: bal, savingsRate: rate };
  }, [transactions]);

  const currency = localStorage.getItem('finance-tracker-currency') || 'USD';

  const cards = [
    {
      name: 'Total Balance',
      value: formatCurrency(balance, currency),
      icon: Wallet,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/50',
    },
    {
      name: 'Monthly Income',
      value: formatCurrency(income, currency),
      icon: ArrowUpRight,
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-100 dark:bg-green-900/50',
    },
    {
      name: 'Monthly Expenses',
      value: formatCurrency(expense, currency),
      icon: ArrowDownRight,
      color: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-100 dark:bg-red-900/50',
    },
    {
      name: 'Savings Rate',
      value: formatPercent(savingsRate),
      icon: DollarSign,
      color: 'text-purple-600 dark:text-purple-400',
      bg: 'bg-purple-100 dark:bg-purple-900/50',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.name}
          className="rounded-xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
        >
          <div className="flex items-center gap-4">
            <div className={`rounded-full p-3 ${card.bg}`}>
              <card.icon className={`h-6 w-6 ${card.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {card.name}
              </p>
              <p className="text-2xl font-bold text-foreground">
                {card.value}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
