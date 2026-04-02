'use client';

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { PublicNavbar } from '@/components/layout/PublicNavbar';
import { PublicFooter } from '@/components/layout/PublicFooter';

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

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans relative overflow-hidden">
      {/* Subtle background glow for premium feel */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-orange-100/40 dark:bg-orange-900/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-100/40 dark:bg-blue-900/10 rounded-full blur-3xl pointer-events-none" />

      <PublicNavbar />
      <main className="flex-1 w-full relative z-10 flex flex-col">
        {children}
      </main>
      <PublicFooter />
    </div>
  );
}
