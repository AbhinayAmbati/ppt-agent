'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { Save, LogOut } from 'lucide-react';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [hasChanges, setHasChanges] = useState(false);
  const [settings, setSettings] = useState({
    theme: (typeof window !== 'undefined' ? localStorage.getItem('theme') : 'light') || 'light',
    notifications: true,
    autoDownload: false,
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSaveSettings = () => {
    localStorage.setItem('settings', JSON.stringify(settings));
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    setHasChanges(false);
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-serif font-bold text-foreground tracking-tight mb-2">
          Settings
        </h1>
        <p className="text-muted-foreground">
          Manage your account and application preferences
        </p>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* Profile Section */}
        <div className="bg-card rounded-2xl shadow-sm p-8 border border-border/50">
          <h2 className="text-2xl font-semibold font-serif text-foreground mb-6 tracking-tight">
            Profile
          </h2>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Username
              </label>
              <div className="px-4 py-2 bg-secondary border border-border/40 rounded-xl text-foreground">
                {user?.username || 'Not set'}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Email
              </label>
              <div className="px-4 py-2 bg-secondary border border-border/40 rounded-xl text-foreground">
                {user?.email || 'Not set'}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Member Since
              </label>
              <div className="px-4 py-2 bg-secondary border border-border/40 rounded-xl text-foreground">
                {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
              </div>
            </div>
          </div>
        </div>

        {/* Preferences Section */}
        <div className="bg-card rounded-2xl shadow-sm p-8 border border-border/50">
          <h2 className="text-2xl font-semibold font-serif text-foreground mb-6 tracking-tight">
            Preferences
          </h2>

          <div className="space-y-4">
            {/* Theme Setting */}
            <div className="flex items-center justify-between p-5 bg-secondary/30 border border-border/30 rounded-xl">
              <div>
                <p className="font-medium text-foreground">Dark Mode</p>
                <p className="text-sm text-muted-foreground">Use dark theme for better visibility</p>
              </div>
              <select
                value={settings.theme}
                onChange={(e) => handleSettingChange('theme', e.target.value)}
                className="px-4 py-2 border border-border/80 rounded-lg bg-background text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-foreground/20 transition-all font-medium"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>

            {/* Notifications Setting */}
            <div className="flex items-center justify-between p-5 bg-secondary/30 border border-border/30 rounded-xl">
              <div>
                <p className="font-medium text-foreground">Notifications</p>
                <p className="text-sm text-muted-foreground">Get updates when presentations are ready</p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                className="w-5 h-5 text-foreground bg-background border-border rounded focus:ring-foreground accent-foreground"
              />
            </div>

            {/* Auto Download Setting */}
            <div className="flex items-center justify-between p-5 bg-secondary/30 border border-border/30 rounded-xl">
              <div>
                <p className="font-medium text-foreground">Auto Download</p>
                <p className="text-sm text-muted-foreground">Automatically download presentations when ready</p>
              </div>
              <input
                type="checkbox"
                checked={settings.autoDownload}
                onChange={(e) => handleSettingChange('autoDownload', e.target.checked)}
                className="w-5 h-5 text-foreground bg-background border-border rounded focus:ring-foreground accent-foreground"
              />
            </div>
          </div>

          {hasChanges && (
            <button
              onClick={handleSaveSettings}
              className="mt-6 w-full px-6 py-3 bg-foreground text-background rounded-xl hover:bg-foreground/90 transition shadow-sm font-medium flex items-center justify-center gap-2"
            >
              <Save size={20} />
              Save Changes
            </button>
          )}
        </div>

        {/* Danger Zone */}
        <div className="bg-red-500/5 rounded-2xl shadow-sm p-8 border border-red-500/20">
          <h2 className="text-2xl font-semibold font-serif text-red-500 mb-2 tracking-tight">
            Danger Zone
          </h2>
          <p className="text-red-500/70 mb-6 text-sm">
            Once you log out, you'll need to log in again to access your presentations.
          </p>
          <button
            onClick={handleLogout}
            className="w-full px-6 py-3 bg-red-50 border border-red-200 text-red-600 hover:bg-red-100 rounded-xl transition font-medium flex items-center justify-center gap-2"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
