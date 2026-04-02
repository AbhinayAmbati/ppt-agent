'use client';

import Link from 'next/link';
import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="flex-1 flex flex-col pt-12 md:pt-16 pb-20 items-center px-4">
      <div className="w-full max-w-[400px]">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-2xl font-semibold mb-2 tracking-tight">Welcome back</h1>
          <p className="text-muted-foreground text-sm">Sign in to your account</p>
        </div>

        {/* Form Card */}
        <div className="bg-card rounded-2xl shadow-sm border border-border px-8 py-10">
          <LoginForm />
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground/60 mt-10">
          <Link href="/register" className="hover:text-foreground transition-colors">
            Don't have an account? Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
