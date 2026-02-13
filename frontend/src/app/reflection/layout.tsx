'use client';

import { AuthGuard } from '@/components/features/auth/AuthGuard';

export default function ReflectionLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}
