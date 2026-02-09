'use client';

import AuthForm from '@/components/features/auth/AuthForm';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function SignInPage() {
  const { user, loading } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (user) {
    return null;
  }

  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <AuthForm />
    </div>
  );
}
