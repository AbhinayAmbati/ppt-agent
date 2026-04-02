'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Clock, Settings, HelpCircle, Sparkles } from 'lucide-react';
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
    <aside className={`${isOpen ? 'w-64' : 'w-20'} bg-background/50 backdrop-blur-sm border-r border-border/40 transition-all duration-300 hidden md:flex flex-col h-full`}>
      <nav className="flex-1 px-4 py-8 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-2xl transition-all ${
                isActive
                  ? 'bg-foreground text-background shadow-md'
                  : 'text-muted-foreground hover:bg-secondary/80 hover:text-foreground'
              }`}
            >
              <Icon size={18} />
              {isOpen && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Help Section */}
      <div className="p-4 mb-4">
        <div className={`flex items-center gap-3 p-4 rounded-2xl bg-secondary/50 border border-border/40 ${isOpen ? '' : 'justify-center'}`}>
          <Sparkles size={18} className="text-orange-500 shrink-0" />
          {isOpen && (
            <div className="text-sm">
              <p className="font-medium text-foreground">Need Help?</p>
              <p className="text-muted-foreground text-xs mt-1">Read the docs</p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
