'use client';

import type { ButtonProps } from '@/types/ui';

const variantStyles = {
  primary: [
    'bg-white text-primary-700 border border-primary-400',
    'hover:bg-primary-50 hover:border-primary-500 hover:text-primary-800',
    'active:bg-primary-100 active:border-primary-600',
    'focus-visible:ring-primary-300',
    'disabled:bg-neutral-50 disabled:text-primary-300 disabled:border-primary-200',
  ].join(' '),
  secondary: [
    'bg-white text-neutral-700 border border-neutral-300',
    'hover:bg-neutral-50 hover:border-neutral-400 hover:text-neutral-800',
    'active:bg-neutral-100 active:border-neutral-500',
    'focus-visible:ring-neutral-300',
    'disabled:bg-neutral-50 disabled:text-neutral-300 disabled:border-neutral-200',
  ].join(' '),
  danger: [
    'bg-white text-red-600 border border-red-400',
    'hover:bg-red-50 hover:border-red-500 hover:text-red-700',
    'active:bg-red-100 active:border-red-600',
    'focus-visible:ring-red-300',
    'disabled:bg-neutral-50 disabled:text-red-300 disabled:border-red-200',
  ].join(' '),
  ghost: [
    'bg-transparent text-neutral-600 border border-transparent',
    'hover:bg-neutral-100 hover:text-neutral-800',
    'active:bg-neutral-200',
    'focus-visible:ring-neutral-300',
    'disabled:text-neutral-300 disabled:bg-transparent',
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

function LoadingSpinner({ size }: { size: 'sm' | 'md' | 'lg' }) {
  const spinnerSize = {
    sm: 'w-3.5 h-3.5',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  return (
    <svg
      className={`animate-spin ${spinnerSize[size]}`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

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
      {loading && <LoadingSpinner size={size} />}
      {children}
    </button>
  );
}
