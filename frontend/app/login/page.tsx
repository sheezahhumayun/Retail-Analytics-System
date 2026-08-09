'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import { LOGIN_HINTS, getLoginErrorMessage } from '@/lib/api/auth';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedHint, setSelectedHint] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [loginError, setLoginError] = useState('');
  const [superadminNotice, setSuperadminNotice] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!selectedHint) return;
    setEmail(selectedHint);
  }, [selectedHint]);

  const validateEmail = (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  };

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!email || email.trim() === '') {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password || password.trim() === '') {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setSuperadminNotice('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const session = await login(email, password);
      if (session.accountType === 'superadmin') {
        setSuperadminNotice(
          'Superadmin dashboard is not yet available — coming in a later phase.',
        );
        setIsLoading(false);
        return;
      }
      router.push('/');
    } catch (error) {
      setLoginError(getLoginErrorMessage(error));
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-foreground mb-2">Retail Analytics</h1>
          <p className="text-muted-foreground">Sign in to your account</p>
        </div>

        <div className="bg-card border border-border rounded-lg shadow-sm p-6 space-y-6">
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground mb-1.5">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setSelectedHint('');
                  if (errors.email) {
                    setErrors({ ...errors, email: undefined });
                  }
                }}
                placeholder="you@example.com"
                className={`w-full px-3 py-2.5 bg-muted border rounded text-foreground text-sm transition-colors ${
                  errors.email ? 'border-red-500' : 'border-border focus:border-primary'
                }`}
              />
              {errors.email && <p className="text-xs text-red-600 dark:text-red-400 mt-1">{errors.email}</p>}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1.5">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) {
                    setErrors({ ...errors, password: undefined });
                  }
                }}
                placeholder="••••••••"
                className={`w-full px-3 py-2.5 bg-muted border rounded text-foreground text-sm transition-colors ${
                  errors.password ? 'border-red-500' : 'border-border focus:border-primary'
                }`}
              />
              {errors.password && <p className="text-xs text-red-600 dark:text-red-400 mt-1">{errors.password}</p>}
            </div>

            {loginError && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-600 dark:text-red-400">
                {loginError}
              </div>
            )}

            {superadminNotice && (
              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded text-sm text-amber-800 dark:text-amber-200">
                {superadminNotice}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-primary hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground text-primary-foreground font-medium py-2.5 rounded transition-colors"
            >
              {isLoading ? 'Signing in...' : 'Log In'}
            </button>
          </form>

          <div className="pt-4 border-t border-border space-y-3">
            <div>
              <label htmlFor="login-hint" className="block text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                Quick fill (seed accounts)
              </label>
              <select
                id="login-hint"
                value={selectedHint}
                onChange={(e) => setSelectedHint(e.target.value)}
                className="w-full px-3 py-2 bg-muted border border-border rounded text-foreground text-sm"
              >
                <option value="">Choose a seed account...</option>
                {LOGIN_HINTS.map((hint) => (
                  <option key={hint.email} value={hint.email}>
                    {hint.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground mt-1.5">
                Credentials are validated by POST /api/auth/login against the backend database.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
