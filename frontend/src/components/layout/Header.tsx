'use client';

import { Icon } from '@/components/ui';
import { APP_NAME, ARIA_LABELS, BUTTON_LABELS, EMOJI_LABELS } from '@/constants';
import { useAuthContext } from '@/contexts/AuthContext';
import type { HeaderProps } from '@/types';
import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { MobileMenu } from './MobileMenu';
import { Navigation } from './Navigation';

/**
 * Header Component
 * アプリケーション共通ヘッダー
 */
export function Header({ className = '' }: HeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const { user, signOut } = useAuthContext();

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignOut = async () => {
    setIsUserMenuOpen(false);
    await signOut();
  };

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
            <Icon name="museum" size="lg" label={EMOJI_LABELS.HISTORIC_BUILDING} />
            <span className="font-bold text-lg">{APP_NAME}</span>
          </Link>

          {/* Desktop Navigation */}
          <Navigation />

          {/* User Icon */}
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

            {/* User Menu (Desktop) */}
            {user && (
              <div ref={userMenuRef} className="relative hidden lg:block">
                <button
                  type="button"
                  onClick={() => setIsUserMenuOpen(prev => !prev)}
                  className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-700 transition-colors hover:bg-primary-200"
                  aria-label={ARIA_LABELS.USER_MENU}
                >
                  <Icon name="user" size="md" label={EMOJI_LABELS.USER} />
                </button>

                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 rounded-md border border-neutral-200 bg-white py-1 shadow-lg">
                    <div className="border-neutral-200 border-b px-4 py-2">
                      <p className="truncate text-neutral-500 text-sm">
                        {user.email || user.displayName || user.uid}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={handleSignOut}
                      className="w-full px-4 py-2 text-left text-red-600 text-sm hover:bg-neutral-50"
                    >
                      {BUTTON_LABELS.SIGN_OUT}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        onSignOut={user ? handleSignOut : undefined}
        userEmail={user?.email || user?.displayName || undefined}
      />
    </header>
  );
}
