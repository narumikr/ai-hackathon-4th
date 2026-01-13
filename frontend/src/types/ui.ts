import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react';

/**
 * Common Size Type
 */
export type ComponentSize = 'sm' | 'md' | 'lg';

/**
 * LoadingSpinner Component Props
 */
export type LoadingSpinnerSize = ComponentSize | 'xl';
export type LoadingSpinnerVariant = 'primary' | 'secondary';

export interface LoadingSpinnerProps {
  /** Spinner style variant */
  variant?: LoadingSpinnerVariant;
  /** Spinner size */
  size?: LoadingSpinnerSize;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Button Component Props
 */
export type ButtonVariant = 'primary' | 'secondary' | 'error' | 'ghost';
export type ButtonSize = ComponentSize;

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button style variant */
  variant?: ButtonVariant;
  /** Button size */
  size?: ButtonSize;
  /** Loading state - shows spinner and disables button */
  loading?: boolean;
  /** Full width button */
  fullWidth?: boolean;
  /** Button content */
  children: ReactNode;
}

/**
 * Checkbox Component Props
 */
export type CheckboxSize = ComponentSize;

export interface CheckboxProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** Checkbox size */
  size?: CheckboxSize;
  /** Label text */
  label?: string;
  /** Description text shown below the label */
  description?: string;
  /** Error state */
  error?: boolean;
}

/**
 * RadioButton Component Props
 */
export type RadioButtonSize = ComponentSize;

export interface RadioButtonProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** RadioButton size */
  size?: RadioButtonSize;
  /** Label text */
  label?: string;
  /** Description text shown below the label */
  description?: string;
  /** Error state */
  error?: boolean;
}
