'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Sparkles } from 'lucide-react';

export default function LandingPage() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans">
      <header className="flex flex-row items-center justify-between px-6 py-6 max-w-7xl mx-auto w-full">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-serif text-2xl font-medium tracking-tight">Auto-PPT</span>
        </Link>
        <div className="flex items-center gap-2 text-sm font-medium">
          {token ? (
            <Link
              href="/dashboard"
              className="px-4 py-2.5 rounded-xl hover:bg-secondary/50 transition-colors"
            >
              Dashboard
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="px-4 py-2.5 rounded-xl text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors"
              >
                Log in
              </Link>
              <Link
                href="/register"
                className="px-4 py-2.5 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors shadow-sm"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 max-w-3xl mx-auto w-full -mt-20">
        <h1 className="text-4xl md:text-[2.75rem] font-serif font-medium tracking-tight text-center mb-10 text-foreground leading-tight">
          What do you want to
          <br />
          present today?
        </h1>
        
        <div className="w-full bg-card rounded-2xl shadow-sm border border-border/60 p-4 transition-all focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary/30">
          <div className="relative">
            <textarea
              placeholder="Enter a topic, upload your notes, or paste a rough draft..."
              className="w-full bg-transparent resize-none outline-none text-lg min-h-[140px] placeholder:text-muted-foreground/60 p-2"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  window.location.href = token ? '/dashboard' : '/register';
                }
              }}
            ></textarea>
            
            <div className="flex justify-between items-center px-2 pb-1">
              <div className="flex items-center gap-2 text-muted-foreground/60">
                <Sparkles className="w-4 h-4" />
              </div>
              <Link
                href={token ? '/dashboard' : '/register'}
                className="px-5 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium text-sm hover:bg-primary/90 transition-colors shadow-sm flex items-center gap-2"
              >
                Start presenting
              </Link>
            </div>
          </div>
        </div>
        
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-sm text-muted-foreground">
          <span className="bg-secondary/50 px-3 py-1.5 rounded-lg border border-border/40 cursor-default hover:bg-secondary transition-colors">Quarterly Review</span>
          <span className="bg-secondary/50 px-3 py-1.5 rounded-lg border border-border/40 cursor-default hover:bg-secondary transition-colors">Startup Pitch Deck</span>
          <span className="bg-secondary/50 px-3 py-1.5 rounded-lg border border-border/40 cursor-default hover:bg-secondary transition-colors">Product Launch</span>
        </div>
      </main>
      
      <footer className="py-6 text-center text-sm text-muted-foreground/60">
        &copy; {new Date().getFullYear()} Auto-PPT. Agentic AI Presentations.
      </footer>
    </div>
  );
}
