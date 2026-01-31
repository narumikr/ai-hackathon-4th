'use client';

import { APP_NAME, ARIA_LABELS, EMOJI_LABELS } from '@/constants';
import type { HeaderProps } from '@/types';
import Link from 'next/link';
import { useState } from 'react';
import { MobileMenu } from './MobileMenu';
import { Navigation } from './Navigation';

/**
 * Header Component
 * アプリケーション共通ヘッダー
 */
export function Header({ className = '' }: HeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header
      className={['sticky top-0 z-30 border-neutral-200 border-b bg-white shadow-sm', className]
        .filter(Boolean)
        .join(' ')}
    >
      <div className="mx-auto max-w-screen-2xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 text-primary-700 transition-colors hover:text-primary-800"
          >
            <span className="text-2xl" role="img" aria-label={EMOJI_LABELS.HISTORIC_BUILDING}>
              🏛️
            </span>
            <span className="font-bold text-lg">{APP_NAME}</span>
          </Link>

          {/* Desktop Navigation */}
          <Navigation />

          {/* User Icon (placeholder) */}
          <div className="flex items-center gap-2">
            {/* Hamburger Menu Button (Mobile) */}
            <button
              type="button"
              onClick={() => setIsMobileMenuOpen(true)}
              className="rounded-md p-2 text-neutral-700 hover:bg-primary-50 hover:text-primary-700 lg:hidden"
              aria-label={ARIA_LABELS.MENU_OPEN}
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
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            {/* User Icon (Desktop) */}
            <button
              type="button"
              className="hidden h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-700 transition-colors hover:bg-primary-200 lg:flex"
              aria-label={ARIA_LABELS.USER_MENU}
            >
              <span className="text-xl" role="img" aria-label={EMOJI_LABELS.USER}>
                👤
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <MobileMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} />
    </header>
  );
}
