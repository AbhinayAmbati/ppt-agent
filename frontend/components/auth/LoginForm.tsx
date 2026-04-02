'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { loginSchema, LoginFormData } from '@/lib/validators';

export function LoginForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const { login, error: authError, clearError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true);
    clearError();
    try {
      await login(data);
      router.push('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {authError && (
        <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm mb-4">
          {authError}
        </div>
      )}

      <div>
        <label htmlFor="username" className="block text-sm mb-1.5 text-foreground/80">
          Username
        </label>
        <input
          id="username"
          type="text"
          autoComplete="username"
          {...register('username')}
          className="w-full px-3 py-2 border border-border/80 rounded-lg bg-background text-foreground transition-colors focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
          placeholder="Enter your username"
        />
        {errors.username && (
          <p className="mt-1.5 text-xs text-red-500">{errors.username.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm mb-1.5 text-foreground/80">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          {...register('password')}
          className="w-full px-3 py-2 border border-border/80 rounded-lg bg-background text-foreground transition-colors focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
          placeholder="Enter your password"
        />
        {errors.password && (
          <p className="mt-1.5 text-xs text-red-500">{errors.password.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full px-4 py-2 mt-2 bg-primary text-primary-foreground font-medium rounded-lg disabled:opacity-50 transition-colors hover:bg-primary/90"
      >
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
}
