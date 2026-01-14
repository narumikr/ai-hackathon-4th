import type {
  ButtonHTMLAttributes,
  InputHTMLAttributes,
  ReactNode,
  TextareaHTMLAttributes,
} from 'react';

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
  /** Error message for accessibility (overrides description when in error state) */
  errorMessage?: string;
  /** Indeterminate state for partial selection */
  indeterminate?: boolean;
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
  /** Error message for accessibility (overrides description when in error state) */
  errorMessage?: string;
}

/*
 * TextField Component Props
 */
export interface TextFieldProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'size'> {
  /** Input label */
  label?: string;
  /** Error message */
  error?: string;
  /** Help text */
  helpText?: string;
  /** Input size */
  size?: ComponentSize;
  /** Full width input */
  fullWidth?: boolean;
  /** Change handler */
  onChange?: (value: string) => void;
}

/**
 * TextArea Component Props
 */
export interface TextAreaProps
  extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange'> {
  /** TextArea label */
  label?: string;
  /** Error message */
  error?: string;
  /** Help text */
  helpText?: string;
  /** Maximum character length */
  maxLength?: number;
  /** Show character count */
  showCount?: boolean;
  /** Full width textarea */
  fullWidth?: boolean;
  /** Change handler */
  onChange?: (value: string) => void;
}

/**
 * Table Column Definition
 */
export interface ColumnDef<T> {
  /** Unique key for the column */
  key: string;
  /** Column header title */
  title: string;
  /** Whether the column is sortable */
  sortable?: boolean;
  /** Column width (CSS value) */
  width?: string;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
  /** Custom render function for the cell */
  render?: (value: T[keyof T], row: T, rowIndex: number) => ReactNode;
}

/**
 * Sort Direction Type
 */
export type SortDirection = 'asc' | 'desc' | null;

/**
 * Sort State
 */
export interface SortState {
  /** Column key being sorted */
  key: string | null;
  /** Sort direction */
  direction: SortDirection;
}

/**
 * Table Component Props
 */
export interface TableProps<T> {
  /** Column definitions */
  columns: ColumnDef<T>[];
  /** Data array */
  data: T[];
  /** Enable sorting (global) */
  sortable?: boolean;
  /** Enable row selection */
  selectable?: boolean;
  /** Selected row keys */
  selectedKeys?: string[];
  /** Callback when selection changes */
  onSelectionChange?: (keys: string[]) => void;
  /** Callback when row is clicked */
  onRowClick?: (row: T, rowIndex: number) => void;
  /** Function to get unique key for each row */
  rowKey?: (row: T, rowIndex: number) => string;
  /** Loading state */
  loading?: boolean;
  /** Empty state message */
  emptyMessage?: string;
  /** Enable striped rows */
  striped?: boolean;
  /** Enable hover effect on rows */
  hoverable?: boolean;
  /** Additional CSS classes */
  className?: string;
}
