'use client';

import { useCallback, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

import type { ModalProps } from '@/types/ui';

const sizeStyles = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
};

const overlayStyles = [
  'fixed inset-0 z-50',
  'flex items-center justify-center',
  'bg-black/50',
  'p-4',
].join(' ');

const contentStyles = [
  'relative w-full',
  'bg-white rounded-lg shadow-lg',
  'max-h-[90vh] overflow-auto',
  'animate-in fade-in zoom-in-95 duration-200',
].join(' ');

const headerStyles = [
  'flex items-center justify-between',
  'px-6 py-4',
  'border-b border-neutral-200',
].join(' ');

const titleStyles = ['text-lg font-semibold text-neutral-900'].join(' ');

const closeButtonStyles = [
  'p-1 rounded-md',
  'text-neutral-500',
  'hover:bg-neutral-100 hover:text-neutral-700',
  'focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2',
  'transition-colors duration-200',
].join(' ');

const bodyStyles = ['px-6 py-4'].join(' ');

export function Modal({
  isOpen,
  onClose,
  title,
  size = 'md',
  children,
  closeOnOverlayClick = true,
  closeOnEsc = true,
  className = '',
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  const handleEscKey = useCallback(
    (event: KeyboardEvent) => {
      if (closeOnEsc && event.key === 'Escape') {
        onClose();
      }
    },
    [closeOnEsc, onClose]
  );

  const handleOverlayClick = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (closeOnOverlayClick && event.target === event.currentTarget) {
        onClose();
      }
    },
    [closeOnOverlayClick, onClose]
  );

  // ESCキーのイベントリスナー
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscKey);
      return () => document.removeEventListener('keydown', handleEscKey);
    }
    return undefined;
  }, [isOpen, handleEscKey]);

  // フォーカストラップとbody scrollの制御
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      document.body.style.overflow = 'hidden';

      // モーダル内の最初のフォーカス可能な要素にフォーカス
      const focusableElements = modalRef.current?.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusableElements && focusableElements.length > 0) {
        focusableElements[0].focus();
      }

      return () => {
        document.body.style.overflow = '';
        previousActiveElement.current?.focus();
      };
    }
    return undefined;
  }, [isOpen]);

  // フォーカストラップ
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key !== 'Tab') return;

    const focusableElements = modalRef.current?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (!focusableElements || focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
    } else if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  }, []);

  if (!isOpen) return null;

  // SSR対応: サーバーサイドではportalを使わない
  if (typeof window === 'undefined') return null;

  return createPortal(
    <div
      className={overlayStyles}
      onClick={handleOverlayClick}
      onKeyDown={e => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleOverlayClick(e as unknown as React.MouseEvent<HTMLDivElement>);
        }
      }}
      // biome-ignore lint/a11y/useSemanticElements: Using div with role="dialog" for portal compatibility
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      <div
        ref={modalRef}
        className={[contentStyles, sizeStyles[size], className].join(' ')}
        onKeyDown={handleKeyDown}
      >
        {title && (
          <div className={headerStyles}>
            <h2 id="modal-title" className={titleStyles}>
              {title}
            </h2>
            <button
              type="button"
              onClick={onClose}
              className={closeButtonStyles}
              aria-label="閉じる"
            >
              <CloseIcon />
            </button>
          </div>
        )}
        <div className={bodyStyles}>{children}</div>
      </div>
    </div>,
    document.body
  );
}

function CloseIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
