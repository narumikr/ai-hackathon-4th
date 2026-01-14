'use client';

import { useId } from 'react';

import type { TextAreaProps } from '@/types/ui';

const baseTextAreaStyles = [
  'w-full',
  'bg-white',
  'border rounded-lg',
  'px-4 py-3 text-base',
  'transition-all duration-200 ease-out',
  'placeholder:text-neutral-400',
  'focus:outline-none focus:ring-2 focus:ring-offset-0',
  'disabled:bg-neutral-100 disabled:text-neutral-400 disabled:cursor-not-allowed',
  'resize-y',
].join(' ');

const normalTextAreaStyles = [
  'border-neutral-300',
  'hover:border-primary-400',
  'focus:border-primary-500 focus:ring-primary-200',
].join(' ');

const errorTextAreaStyles = [
  'border-red-400',
  'hover:border-red-500',
  'focus:border-red-500 focus:ring-red-200',
].join(' ');

export function TextArea({
  label,
  error,
  helpText,
  maxLength,
  showCount = false,
  fullWidth = false,
  required,
  disabled,
  rows = 4,
  value,
  className = '',
  id: providedId,
  onChange,
  ...props
}: TextAreaProps) {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  const errorId = `${id}-error`;
  const helpTextId = `${id}-help`;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange?.(e.target.value);
  };

  const currentLength = typeof value === 'string' ? value.length : 0;
  const isOverLimit = maxLength !== undefined && currentLength > maxLength;

  return (
    <div className={fullWidth ? 'w-full' : 'inline-block'}>
      {label && (
        <label htmlFor={id} className="mb-1.5 block font-medium text-neutral-700 text-sm">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </label>
      )}
      <textarea
        id={id}
        rows={rows}
        disabled={disabled}
        required={required}
        maxLength={maxLength}
        value={value}
        aria-invalid={error || isOverLimit ? 'true' : undefined}
        aria-describedby={error ? errorId : helpText ? helpTextId : undefined}
        className={[
          baseTextAreaStyles,
          error || isOverLimit ? errorTextAreaStyles : normalTextAreaStyles,
          className,
        ].join(' ')}
        onChange={handleChange}
        {...props}
      />
      <div className="mt-1.5 flex items-start justify-between gap-2">
        <div className="flex-1">
          {error && (
            <p id={errorId} className="text-red-600 text-sm">
              {error}
            </p>
          )}
          {helpText && !error && (
            <p id={helpTextId} className="text-neutral-500 text-sm">
              {helpText}
            </p>
          )}
        </div>
        {showCount && maxLength !== undefined && (
          <p className={`text-sm ${isOverLimit ? 'text-red-600' : 'text-neutral-500'}`}>
            {currentLength}/{maxLength}
          </p>
        )}
      </div>
    </div>
  );
}
