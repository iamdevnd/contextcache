'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FiSettings, FiActivity, FiDatabase, FiShield, FiArrowLeft } from 'react-icons/fi';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const pathname = usePathname();

  const menuItems = [
    { href: '/admin', label: 'Overview', icon: <FiActivity /> },
    { href: '/admin/config', label: 'Configuration', icon: <FiSettings /> },
    { href: '/admin/database', label: 'Database', icon: <FiDatabase /> },
    { href: '/admin/security', label: 'Security', icon: <FiShield /> },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-gray-800 min-h-screen">
          <div className="p-6">
            <h2 className="text-xl font-bold mb-6">Admin Panel</h2>
            <nav className="space-y-2">
              {menuItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-3 px-4 py-2 rounded-md transition ${
                    pathname === item.href
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>
            <div className="mt-8 pt-8 border-t border-gray-700">
              <Link
                href="/"
                className="flex items-center space-x-3 px-4 py-2 text-gray-400 hover:text-white transition"
              >
                <FiArrowLeft />
                <span>Back to App</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
