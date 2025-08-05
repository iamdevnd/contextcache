'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';

export default function AdminRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, user, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth().then(() => {
      if (!isAuthenticated || user?.username !== 'admin') {
        router.push('/');
      }
    });
  }, [isAuthenticated, user, checkAuth, router]);

  if (!isAuthenticated || user?.username !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-gray-400">Admin access required</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}