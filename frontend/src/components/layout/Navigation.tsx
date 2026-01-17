'use client';

import { NAVIGATION_ITEMS } from '@/constants';
import type { NavigationProps } from '@/types';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * Navigation Component
 * ヘッダーナビゲーション（デスクトップ版）
 */
export function Navigation({ currentPath, className = '' }: NavigationProps) {
  const pathname = usePathname();
  const activePath = currentPath ?? pathname;

  return (
    <nav className={['hidden items-center gap-1 lg:flex', className].filter(Boolean).join(' ')}>
      {NAVIGATION_ITEMS.map(item => {
        const isActive = activePath === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={[
              'rounded-md px-4 py-2 font-medium text-sm transition-colors',
              isActive
                ? 'bg-primary-100 text-primary-800'
                : 'text-neutral-700 hover:bg-primary-50 hover:text-primary-700',
            ]
              .filter(Boolean)
              .join(' ')}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
