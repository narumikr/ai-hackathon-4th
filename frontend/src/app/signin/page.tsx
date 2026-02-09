'use client';

import AuthForm from '@/components/features/auth/AuthForm';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { redirect } from 'next/navigation';

export default function SignInPage() {
  const { user, loading } = useAuthContext();

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (user) {
    redirect('/');
  }

  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <AuthForm />
    </div>
  );
}
