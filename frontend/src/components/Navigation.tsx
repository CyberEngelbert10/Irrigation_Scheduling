import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

interface NavigationProps {
  currentPage?: string;
}

export default function Navigation({ currentPage }: NavigationProps) {
  const { user, logout } = useAuth();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/fields', label: 'Fields', icon: '🌾' },
    { href: '/history', label: 'History', icon: '📚' },
    { href: '/weather', label: 'Weather', icon: '🌤️' },
    { href: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/dashboard" className="text-2xl font-bold text-primary-700 hover:text-primary-800">
            🌱 Smart Irrigation
          </Link>

          <nav className="hidden md:flex items-center space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  currentPage === item.href.slice(1)
                    ? 'bg-primary-100 text-primary-700 font-medium'
                    : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            <Link href="/profile" className="text-gray-700 hover:text-primary-600">
              {user?.name}
            </Link>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <nav className="md:hidden mt-4 pt-4 border-t border-gray-200">
          <div className="flex justify-around">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center space-y-1 px-3 py-2 rounded-lg transition-colors ${
                  currentPage === item.href.slice(1)
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:text-primary-600'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            ))}
          </div>
        </nav>
      </div>
    </header>
  );
}