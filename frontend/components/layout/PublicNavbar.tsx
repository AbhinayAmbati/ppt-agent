'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

export function PublicNavbar() {
  const { token } = useAuth();

  return (
    <header className="flex flex-row items-center justify-between px-8 py-6 max-w-7xl mx-auto w-full relative z-10 antialiased font-sans">
      <Link href="/" className="flex items-center gap-3 group">
        <span className="font-serif text-2xl font-medium tracking-tight">SlideForage</span>
      </Link>
      <div className="flex items-center gap-4 text-sm font-medium">
        {token ? (
          <Link
            href="/dashboard"
            className="px-5 py-2.5 rounded-full hover:bg-secondary/80 transition-colors"
          >
            Go to Dashboard
          </Link>
        ) : (
          <>
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-full text-muted-foreground hover:text-foreground transition-colors"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="px-5 py-2.5 bg-foreground text-background rounded-full hover:bg-foreground/90 transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5"
            >
              Sign up
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
