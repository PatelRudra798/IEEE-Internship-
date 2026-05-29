import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ArrowRightLeft, 
  PiggyBank, 
  Target, 
  BarChart3, 
  Settings 
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Transactions', path: '/transactions', icon: ArrowRightLeft },
  { name: 'Budgets', path: '/budgets', icon: PiggyBank },
  { name: 'Goals', path: '/goals', icon: Target },
  { name: 'Reports', path: '/reports', icon: BarChart3 },
  { name: 'Settings', path: '/settings', icon: Settings },
];

interface SidebarProps {
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

export default function Sidebar({ mobileOpen, setMobileOpen }: SidebarProps) {
  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Content */}
      <aside
        className={clsx(
          "fixed top-0 left-0 z-50 h-screen w-64 border-r border-border bg-card transition-transform lg:translate-x-0 lg:static lg:h-[calc(100vh-4rem)] lg:w-64",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 items-center px-6 lg:hidden border-b border-border">
          <span className="text-xl font-bold text-primary-600">FinanceTracker</span>
        </div>
        
        <nav className="space-y-1 p-4">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive 
                    ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-100' 
                    : 'text-foreground hover:bg-gray-100 dark:hover:bg-gray-800'
                )
              }
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
