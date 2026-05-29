import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { useNotification } from '../context/NotificationContext';
import { BASE_URL } from '../utils/api';
import { 
  Sun, 
  Moon, 
  Monitor, 
  DollarSign, 
  Database, 
  Activity, 
  AlertTriangle,
  Info,
  Trash2,
  Download
} from 'lucide-react';

const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
];

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const { addNotification } = useNotification();
  const [currency, setCurrencyState] = useState(() => localStorage.getItem('finance-tracker-currency') || 'INR');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [backendProvider, setBackendProvider] = useState<string>('');

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(`${BASE_URL}/health`);
        if (res.ok) {
          const data = await res.json();
          setBackendStatus('online');
          setBackendProvider(data.provider || 'gemini');
        } else {
          setBackendStatus('offline');
        }
      } catch (err) {
        setBackendStatus('offline');
      }
    }
    checkHealth();
  }, []);

  const handleCurrencyChange = (code: string) => {
    localStorage.setItem('finance-tracker-currency', code);
    setCurrencyState(code);
    addNotification(`Currency preference updated to ${code}`, 'success');
    
    // Dispatch storage event to trigger update in other components
    window.dispatchEvent(new Event('local-storage'));
  };

  const handleResetData = () => {
    if (confirm('Are you sure you want to clear ALL local database data? This action is permanent.')) {
      localStorage.removeItem('finance-tracker-transactions');
      localStorage.removeItem('finance-tracker-budgets');
      localStorage.removeItem('finance-tracker-goals');
      addNotification('All local data cleared. Reloading...', 'warning');
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    }
  };

  const handleExportData = () => {
    try {
      const data = {
        transactions: JSON.parse(localStorage.getItem('finance-tracker-transactions') || '[]'),
        budgets: JSON.parse(localStorage.getItem('finance-tracker-budgets') || '[]'),
        goals: JSON.parse(localStorage.getItem('finance-tracker-goals') || '[]'),
        currency,
        theme,
      };
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `finance_tracker_backup_${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      addNotification('Backup file downloaded successfully', 'success');
    } catch (err) {
      addNotification('Failed to export data', 'error');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent dark:from-primary-400 dark:to-indigo-400">
          Settings
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Configure visual settings, system parameters, and backup utilities.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Theme Settings Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold flex items-center gap-2 mb-1">
              <Sun className="h-4 w-4 text-primary-500" />
              Theme Mode
            </h3>
            <p className="text-xs text-gray-400 mb-4">Adjust the layout and appearance of your workstation.</p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'light', label: 'Light', icon: Sun },
              { id: 'dark', label: 'Dark', icon: Moon },
              { id: 'system', label: 'System', icon: Monitor },
            ].map((opt) => {
              const Icon = opt.icon;
              const isActive = theme === opt.id;
              return (
                <button
                  key={opt.id}
                  onClick={() => setTheme(opt.id as any)}
                  className={`flex flex-col items-center gap-2 rounded-lg border p-3.5 transition-all text-xs font-medium cursor-pointer ${
                    isActive 
                      ? 'border-primary-500 bg-primary-50/50 dark:bg-primary-950/20 text-primary-600 dark:text-primary-400 font-semibold ring-1 ring-primary-500' 
                      : 'border-border bg-transparent hover:bg-gray-50 dark:hover:bg-gray-800/50 text-foreground'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Currency Settings Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-semibold flex items-center gap-2 mb-1">
              <DollarSign className="h-4 w-4 text-primary-500" />
              Base Currency
            </h3>
            <p className="text-xs text-gray-400 mb-4">Select the standard currency to format figures and graphs.</p>
          </div>

          <div className="relative">
            <select
              value={currency}
              onChange={(e) => handleCurrencyChange(e.target.value)}
              className="w-full rounded-lg border border-border bg-transparent p-2.5 text-sm font-medium focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {CURRENCIES.map(curr => (
                <option key={curr.code} value={curr.code}>
                  {curr.code} ({curr.symbol}) — {curr.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Backend Health Check Status Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm md:col-span-2">
          <h3 className="text-base font-semibold flex items-center gap-2 mb-1">
            <Activity className="h-4 w-4 text-primary-500" />
            Backend Connection Status
          </h3>
          <p className="text-xs text-gray-400 mb-4">Check synchronization link between web client and FastAPI server.</p>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-border rounded-lg p-4 bg-gray-50/50 dark:bg-gray-800/10">
            <div className="flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${
                backendStatus === 'online' 
                  ? 'bg-green-500 animate-pulse' 
                  : backendStatus === 'offline' 
                  ? 'bg-red-500' 
                  : 'bg-gray-400 animate-pulse'
              }`} />
              <div>
                <p className="text-sm font-semibold capitalize text-foreground">
                  {backendStatus === 'online' ? 'Server Connected' : backendStatus === 'offline' ? 'Server Offline' : 'Querying Server...'}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {backendStatus === 'online' 
                    ? `Host: http://localhost:8000 (Provider: ${backendProvider})` 
                    : 'FastAPI client is operating in robust offline fallback mode.'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs font-medium text-gray-500">
              {backendStatus === 'online' ? (
                <span className="bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-400 px-2.5 py-1 rounded-full border border-green-200 dark:border-green-800 flex items-center gap-1">
                  <Info className="h-3.5 w-3.5" /> Fully Synced
                </span>
              ) : (
                <span className="bg-amber-50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400 px-2.5 py-1 rounded-full border border-amber-200 dark:border-amber-800 flex items-center gap-1">
                  <AlertTriangle className="h-3.5 w-3.5" /> Local Database
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Data Utilities Panel */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm md:col-span-2">
          <h3 className="text-base font-semibold flex items-center gap-2 mb-1">
            <Database className="h-4 w-4 text-primary-500" />
            Database Utilities & Safety
          </h3>
          <p className="text-xs text-gray-400 mb-4">Export backup snapshots of your financials or purge application cache.</p>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleExportData}
              className="flex items-center justify-center gap-2 rounded-lg border border-border bg-transparent px-4 py-2 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer text-foreground"
            >
              <Download className="h-4 w-4 text-primary-500" />
              Download JSON Backup
            </button>
            
            <button
              onClick={handleResetData}
              className="flex items-center justify-center gap-2 rounded-lg border border-red-200 hover:border-red-300 dark:border-red-900 bg-red-50 hover:bg-red-100 dark:bg-red-950/20 dark:hover:bg-red-900/10 px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 cursor-pointer"
            >
              <Trash2 className="h-4 w-4 text-red-500" />
              Reset All Database Tables
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
