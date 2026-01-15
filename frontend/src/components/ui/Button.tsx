'use client';

import type { ButtonProps } from '@/types/ui';
import { LoadingSpinner } from './LoadingSpinner';

const variantStyles = {
  primary: [
    'bg-primary-400 text-primary-950 border border-primary-600',
    'hover:bg-primary-500 hover:border-primary-700 hover:shadow-md',
    'active:bg-primary-600 active:border-primary-800',
    'focus-visible:ring-primary-300',
    'disabled:bg-primary-200 disabled:text-primary-600 disabled:border-primary-300',
  ].join(' '),
  secondary: [
    'bg-white text-primary-700 border border-primary-400',
    'hover:bg-primary-50 hover:border-primary-500 hover:text-primary-800',
    'active:bg-primary-100 active:border-primary-600',
    'focus-visible:ring-primary-300',
    'disabled:bg-neutral-50 disabled:text-primary-300 disabled:border-primary-200',
  ].join(' '),
  error: [
    'bg-danger text-white border border-red-600',
    'hover:bg-red-600 hover:border-red-700 hover:shadow-md',
    'active:bg-red-700 active:border-red-800',
    'focus-visible:ring-red-300',
    'disabled:bg-red-200 disabled:text-red-400 disabled:border-red-300',
  ].join(' '),
  ghost: [
    'bg-transparent text-neutral-700 border border-neutral-300',
    'hover:bg-neutral-100 hover:text-neutral-900 hover:border-neutral-400',
    'active:bg-neutral-200 active:border-neutral-500',
    'focus-visible:ring-neutral-300',
    'disabled:text-neutral-300 disabled:bg-transparent disabled:border-neutral-200',
  ].join(' '),
};

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm gap-1.5',
  md: 'px-4 py-2 text-base gap-2',
  lg: 'px-6 py-3 text-lg gap-2.5',
};

const baseStyles = [
  'inline-flex items-center justify-center',
  'font-medium',
  'rounded-lg',
  'transition-all duration-200 ease-out',
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
  'disabled:cursor-not-allowed',
  'select-none',
].join(' ');

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled,
  className = '',
  children,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      type="button"
      disabled={isDisabled}
      className={[
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        fullWidth ? 'w-full' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {loading && <LoadingSpinner variant="secondary" size={size} />}
      {children}
    </button>
  );
}
