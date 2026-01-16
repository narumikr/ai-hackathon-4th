'use client';

import { useId } from 'react';

import type { FormFieldProps } from '@/types/ui';

const baseStyles = ['w-full'].join(' ');

const labelStyles = ['mb-1.5 block font-medium text-neutral-700 text-sm'].join(' ');

const requiredMarkStyles = 'ml-1 text-red-500';

const errorStyles = ['mt-1.5 text-red-600 text-sm'].join(' ');

const helpTextStyles = ['mt-1.5 text-neutral-500 text-sm'].join(' ');

export function FormField({
  label,
  required = false,
  error,
  helpText,
  children,
  className = '',
  htmlFor: providedHtmlFor,
}: FormFieldProps) {
  const generatedId = useId();
  const htmlFor = providedHtmlFor ?? generatedId;
  const errorId = `${htmlFor}-error`;
  const helpTextId = `${htmlFor}-help`;

  return (
    <div className={[baseStyles, className].filter(Boolean).join(' ')}>
      <label htmlFor={htmlFor} className={labelStyles}>
        {label}
        {required && (
          <span className={requiredMarkStyles} aria-hidden="true">
            *
          </span>
        )}
      </label>
      <div
        aria-describedby={error ? errorId : helpText ? helpTextId : undefined}
        data-error={error ? 'true' : undefined}
      >
        {children}
      </div>
      {error && (
        <p id={errorId} className={errorStyles} role="alert">
          {error}
        </p>
      )}
      {helpText && !error && (
        <p id={helpTextId} className={helpTextStyles}>
          {helpText}
        </p>
      )}
    </div>
  );
}
