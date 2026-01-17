'use client';

import { NAVIGATION_ITEMS } from '@/constants';
import type { MobileMenuProps } from '@/types';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

/**
 * MobileMenu Component
 * モバイル用ナビゲーションメニュー
 */
export function MobileMenu({ isOpen, onClose, currentPath }: MobileMenuProps) {
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
      <div
        className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        onClick={onClose}
        onKeyDown={e => {
          if (e.key === 'Escape') onClose();
        }}
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
              aria-label="メニューを閉じる"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                role="img"
                aria-hidden="true"
              >
                <title>閉じるアイコン</title>
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
        </div>
      </div>
    </>
  );
}
