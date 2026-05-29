import { useNotification } from '../../context/NotificationContext';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import clsx from 'clsx';

export default function ToastContainer() {
  const { notifications, removeNotification } = useNotification();

  if (notifications.length === 0) return null;

  const icons = {
    success: <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />,
    error: <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />,
    warning: <AlertTriangle className="h-5 w-5 text-amber-500 dark:text-amber-400" />,
    info: <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />,
  };

  const bgStyles = {
    success: 'border-l-4 border-green-500 bg-white/90 dark:bg-gray-900/90 text-green-800 dark:text-green-200',
    error: 'border-l-4 border-red-500 bg-white/90 dark:bg-gray-900/90 text-red-800 dark:text-red-200',
    warning: 'border-l-4 border-amber-500 bg-white/90 dark:bg-gray-900/90 text-amber-800 dark:text-amber-200',
    info: 'border-l-4 border-blue-500 bg-white/90 dark:bg-gray-900/90 text-blue-800 dark:text-blue-200',
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full px-4 sm:px-0">
      {notifications.map((notif) => (
        <div
          key={notif.id}
          className={clsx(
            'flex items-start gap-3 rounded-lg p-4 shadow-lg backdrop-blur-md transition-all duration-300 transform translate-y-0 animate-in fade-in slide-in-from-bottom-5',
            bgStyles[notif.type]
          )}
          role="alert"
        >
          <div className="shrink-0 pt-0.5">{icons[notif.type]}</div>
          <div className="flex-1 text-sm font-medium leading-5 text-foreground">{notif.message}</div>
          <button
            onClick={() => removeNotification(notif.id)}
            className="shrink-0 rounded-md p-0.5 text-gray-400 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-500 dark:hover:bg-gray-800 dark:hover:text-gray-100 transition-colors"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
