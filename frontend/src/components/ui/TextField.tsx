'use client';

import { useId } from 'react';

import type { TextFieldProps } from '@/types/ui';

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-4 py-3 text-lg',
};

const baseInputStyles = [
  'w-full',
  'bg-white',
  'border rounded-lg',
  'transition-all duration-200 ease-out',
  'placeholder:text-neutral-400',
  'focus:outline-none focus:ring-2 focus:ring-offset-0',
  'disabled:bg-neutral-100 disabled:text-neutral-400 disabled:cursor-not-allowed',
].join(' ');

const normalInputStyles = [
  'border-neutral-300',
  'hover:border-primary-400',
  'focus:border-primary-500 focus:ring-primary-200',
].join(' ');

const errorInputStyles = [
  'border-red-400',
  'hover:border-red-500',
  'focus:border-red-500 focus:ring-red-200',
].join(' ');

export function TextField({
  label,
  error,
  helpText,
  size = 'md',
  fullWidth = false,
  required,
  disabled,
  className = '',
  id: providedId,
  onChange,
  ...props
}: TextFieldProps) {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  const errorId = `${id}-error`;
  const helpTextId = `${id}-help`;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(e.target.value);
  };

  return (
    <div className={fullWidth ? 'w-full' : 'inline-block'}>
      {label && (
        <label htmlFor={id} className="mb-1.5 block font-medium text-neutral-700 text-sm">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </label>
      )}
      <input
        id={id}
        type="text"
        disabled={disabled}
        required={required}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? errorId : helpText ? helpTextId : undefined}
        className={[
          baseInputStyles,
          error ? errorInputStyles : normalInputStyles,
          sizeStyles[size],
          className,
        ].join(' ')}
        onChange={handleChange}
        {...props}
      />
      {error && (
        <p id={errorId} className="mt-1.5 text-red-600 text-sm">
          {error}
        </p>
      )}
      {helpText && !error && (
        <p id={helpTextId} className="mt-1.5 text-neutral-500 text-sm">
          {helpText}
        </p>
      )}
    </div>
  );
}
