'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Clock, Settings, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/history', icon: Clock, label: 'History' },
  { href: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(true);

  return (
    <aside className={`${isOpen ? 'w-64' : 'w-20'} bg-background/50 backdrop-blur-sm border-r border-border/40 transition-all duration-300 hidden md:flex flex-col h-full relative group`}>
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-3 top-6 bg-background border border-border/40 text-muted-foreground hover:text-foreground hover:bg-secondary/80 rounded-full p-1 shadow-sm z-20 transition-all opacity-0 group-hover:opacity-100 flex items-center justify-center cursor-pointer"
        aria-label={isOpen ? 'Collapse Sidebar' : 'Expand Sidebar'}
      >
        {isOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      <nav className="flex-1 px-4 py-8 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              title={!isOpen ? item.label : undefined}
              className={`flex items-center gap-3 py-3 rounded-2xl transition-all ${
                isActive
                  ? 'bg-foreground text-background shadow-md'
                  : 'text-muted-foreground hover:bg-secondary/80 hover:text-foreground'
              } ${isOpen ? 'px-4' : 'justify-center px-0 mx-1'}`}
            >
              <Icon size={18} className="shrink-0" />
              {isOpen && <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Help Section */}
      <div className={`p-4 mb-4 transition-all ${isOpen ? '' : 'px-2'}`}>
        <div className={`flex items-center gap-3 p-4 rounded-2xl bg-secondary/50 border border-border/40 transition-all overflow-hidden ${isOpen ? '' : 'justify-center p-3'}`}>
          <Sparkles size={18} className="text-orange-500 shrink-0" />
          {isOpen && (
            <div className="text-sm whitespace-nowrap">
              <p className="font-medium text-foreground">Need Help?</p>
              <p className="text-muted-foreground text-xs mt-1">Read the docs</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
