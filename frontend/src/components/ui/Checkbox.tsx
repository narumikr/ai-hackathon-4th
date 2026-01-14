'use client';

import type { CheckboxProps } from '@/types/ui';

const sizeStyles = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
};

const labelSizeStyles = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
};

export function Checkbox({
  id,
  label,
  size = 'md',
  disabled = false,
  error = false,
  description,
  errorMessage,
  className = '',
  ...props
}: CheckboxProps) {
  const checkboxId = id || `checkbox-${Math.random().toString(36).substring(7)}`;
  const descriptionId = `${checkboxId}-description`;

  // Use errorMessage if in error state, otherwise use description
  const displayDescription = error && errorMessage ? errorMessage : description;
  const hasDescription = Boolean(displayDescription);

  return (
    <div className={`flex items-start ${className}`}>
      <div className="flex h-5 items-center">
        <input
          id={checkboxId}
          type="checkbox"
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={hasDescription ? descriptionId : undefined}
          className={[
            sizeStyles[size],
            'rounded border-2',
            'transition-all duration-200 ease-out',
            'focus:outline-none focus:ring-2 focus:ring-offset-2',
            error
              ? ['border-red-500', 'accent-red-500', 'focus:ring-red-300'].join(' ')
              : [
                  'border-primary-500',
                  'accent-primary-500',
                  'focus:ring-primary-300',
                  'hover:border-primary-600',
                ].join(' '),
            disabled
              ? 'cursor-not-allowed border-neutral-300 bg-neutral-100 opacity-50'
              : 'cursor-pointer bg-white',
          ]
            .filter(Boolean)
            .join(' ')}
          {...props}
        />
      </div>
      {(label || displayDescription) && (
        <div className="ml-3">
          {label && (
            <label
              htmlFor={checkboxId}
              className={[
                labelSizeStyles[size],
                'font-medium',
                disabled
                  ? 'cursor-not-allowed text-neutral-400'
                  : 'cursor-pointer text-neutral-900',
                error ? 'text-red-700' : '',
              ]
                .filter(Boolean)
                .join(' ')}
            >
              {label}
            </label>
          )}
          {displayDescription && (
            <p
              id={descriptionId}
              className={[
                'mt-0.5 text-sm',
                disabled ? 'text-neutral-300' : 'text-neutral-600',
                error ? 'text-red-600' : '',
              ]
                .filter(Boolean)
                .join(' ')}
              role={error ? 'alert' : undefined}
            >
              {displayDescription}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
