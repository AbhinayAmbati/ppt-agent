'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { registerSchema, RegisterFormData } from '@/lib/validators';

function PasswordStrengthIndicator({ password }: { password: string }) {
  const strength = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^a-zA-Z0-9]/.test(password),
  };

  const score = Object.values(strength).filter(Boolean).length;
  // A simple warm minimal palette for strength:
  const colors = ['bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-green-500'];

  return (
    <div className="mt-2 space-y-2">
      <div className="w-full bg-secondary rounded-full h-1">
        <div
          className={`h-1 rounded-full transition-all duration-300 ${colors[Math.min(score - 1, 3)]}`}
          style={{ width: `${(score / 4) * 100}%` }}
        ></div>
      </div>
      <div className="flex gap-2 text-[10px] text-muted-foreground uppercase tracking-wider">
         <span className={strength.length ? 'text-foreground' : ''}>8+ Chars</span> &bull; 
         <span className={strength.uppercase ? 'text-foreground' : ''}>Upper</span> &bull; 
         <span className={strength.number ? 'text-foreground' : ''}>Num</span> &bull; 
         <span className={strength.special ? 'text-foreground' : ''}>Special</span>
      </div>
    </div>
  );
}

export function RegisterForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const { register: authRegister, error: authError, clearError } = useAuth();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setIsSubmitting(true);
    clearError();
    try {
      await authRegister({
        username: data.username,
        email: data.email,
        password: data.password,
      });
      router.push('/dashboard');
    } catch (err) {
      console.error('Registration error:', err);
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
          placeholder="Choose a username"
        />
        {errors.username && (
          <p className="mt-1.5 text-xs text-red-500">{errors.username.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm mb-1.5 text-foreground/80">
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          {...register('email')}
          className="w-full px-3 py-2 border border-border/80 rounded-lg bg-background text-foreground transition-colors focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
          placeholder="Enter your email"
        />
        {errors.email && (
          <p className="mt-1.5 text-xs text-red-500">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm mb-1.5 text-foreground/80">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          {...register('password')}
          className="w-full px-3 py-2 border border-border/80 rounded-lg bg-background text-foreground transition-colors focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
          placeholder="Create a strong password"
        />
        {password && <PasswordStrengthIndicator password={password} />}
        {errors.password && (
          <p className="mt-1.5 text-xs text-red-500">{errors.password.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm mb-1.5 text-foreground/80">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          {...register('confirmPassword')}
          className="w-full px-3 py-2 border border-border/80 rounded-lg bg-background text-foreground transition-colors focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary shadow-sm"
          placeholder="Confirm your password"
        />
        {errors.confirmPassword && (
          <p className="mt-1.5 text-xs text-red-500">{errors.confirmPassword.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full px-4 py-2 mt-2 bg-primary text-primary-foreground font-medium rounded-lg disabled:opacity-50 transition-colors hover:bg-primary/90"
      >
        {isSubmitting ? 'Creating account...' : 'Create account'}
      </button>
    </form>
  );
}
