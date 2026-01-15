'use client';

import type { RadioButtonProps } from '@/types/ui';
import { useId } from 'react';

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

export function RadioButton({
  id,
  label,
  size = 'md',
  disabled = false,
  error = false,
  description,
  className = '',
  ...props
}: RadioButtonProps) {
  const generatedId = useId();
  const radioId = id || `radio-${generatedId}`;

  return (
    <div className={`flex items-start ${className}`}>
      <div className="flex h-5 items-center">
        <input
          id={radioId}
          type="radio"
          disabled={disabled}
          className={[
            sizeStyles[size],
            'border-2',
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
      {(label || description) && (
        <div className="ml-3">
          {label && (
            <label
              htmlFor={radioId}
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
          {description && (
            <p
              className={[
                'mt-0.5 text-sm',
                disabled ? 'text-neutral-300' : 'text-neutral-600',
                error ? 'text-red-600' : '',
              ]
                .filter(Boolean)
                .join(' ')}
            >
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
