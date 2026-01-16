import { LOADING_SPINNER } from '@/constants/ui';
import type { LoadingSpinnerProps } from '@/types/ui';

const sizeStyles = {
  sm: 'w-3.5 h-3.5',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
  xl: 'w-6 h-6',
};

const variantStyles = {
  primary: 'text-primary-500',
  secondary: 'text-current',
};

export function LoadingSpinner({
  variant = 'primary',
  size = 'md',
  className = '',
}: LoadingSpinnerProps) {
  return (
    <div
      className={`inline-flex ${sizeStyles[size]} ${variantStyles[variant]} ${className}`.trim()}
      // biome-ignore lint/a11y/useSemanticElements: role="status" is appropriate for loading indicator
      role="status"
      aria-label={LOADING_SPINNER.ARIA_LABEL}
    >
      <svg
        className="h-full w-full animate-spin"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}
