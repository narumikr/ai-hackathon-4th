'use client';

import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { redirect } from 'next/navigation';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuthContext();

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!user) {
    redirect('/signin');
  }

  return <>{children}</>;
}
