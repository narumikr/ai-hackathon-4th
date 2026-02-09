'use client';

import { ARIA_LABELS, NAVIGATION_ITEMS } from '@/constants';
import type { MobileMenuProps } from '@/types';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

/**
 * MobileMenu Component
 * モバイル用ナビゲーションメニュー
 */
export function MobileMenu({
  isOpen,
  onClose,
  currentPath,
  onSignOut,
  userEmail,
}: MobileMenuProps) {
  const pathname = usePathname();
  const activePath = currentPath ?? pathname;

  // メニューが開いたときにスクロールを無効化
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <button
        type="button"
        className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        onClick={onClose}
        aria-label={ARIA_LABELS.MENU_CLOSE}
        tabIndex={-1}
      />

      {/* Menu Panel */}
      <div className="fixed top-0 right-0 bottom-0 z-50 w-64 bg-white shadow-lg lg:hidden">
        <div className="flex h-full flex-col">
          {/* Close Button */}
          <div className="flex justify-end p-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md p-2 text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700"
              aria-label={ARIA_LABELS.MENU_CLOSE}
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Navigation Items */}
          <nav className="flex-1 px-4 py-2">
            {NAVIGATION_ITEMS.map(item => {
              const isActive = activePath === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={[
                    'mb-1 block rounded-md px-4 py-3 font-medium text-base transition-colors',
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

          {/* Sign Out */}
          {onSignOut && (
            <div className="border-neutral-200 border-t p-4">
              {userEmail && <p className="mb-2 truncate text-neutral-500 text-xs">{userEmail}</p>}
              <button
                type="button"
                onClick={onSignOut}
                className="w-full rounded-md px-4 py-2 text-left text-red-600 text-sm hover:bg-neutral-50"
              >
                サインアウト
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
