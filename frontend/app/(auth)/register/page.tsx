'use client';

import Link from 'next/link';
import { RegisterForm } from '@/components/auth/RegisterForm';

export default function RegisterPage() {
  return (
    <div className="flex-1 flex flex-col pt-[15vh] pb-20 items-center px-4">
      <div className="w-full max-w-[400px]">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-2xl font-semibold mb-2 tracking-tight">Create an account</h1>
          <p className="text-muted-foreground text-sm">Join us and start generating</p>
        </div>

        {/* Form Card */}
        <div className="bg-card rounded-2xl shadow-sm border border-border px-8 py-10">
          <RegisterForm />
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground/60 mt-10">
          <Link href="/login" className="hover:text-foreground transition-colors">
            Already have an account? Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
