import { Menu, Moon, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

interface NavbarProps {
  onMenuClick: () => void;
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-card px-4 sm:px-6">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 -ml-2 text-foreground hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          aria-label="Toggle Menu"
        >
          <Menu className="h-6 w-6" />
        </button>
        <span className="text-xl font-bold text-primary-600 hidden lg:block">FinanceTracker</span>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="p-2 text-foreground hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          aria-label="Toggle Dark Mode"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>
      </div>
    </header>
  );
}
