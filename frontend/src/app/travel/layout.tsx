'use client';

import { AuthGuard } from '@/components/features/auth/AuthGuard';

export default function TravelLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}
