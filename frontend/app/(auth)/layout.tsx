'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { token, isInitializing } = useAuth();
  const router = useRouter();

  // Redirect authenticated users away from auth pages
  useEffect(() => {
    if (!isInitializing && token) {
      router.push('/dashboard');
    }
  }, [token, isInitializing, router]);

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center min-h-[100dvh] bg-background">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-4"></div>
        </div>
      </div>
    );
  }

  return children;
}
