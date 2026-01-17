import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
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
 * FormField Component Props
 */
export interface FormFieldProps {
  /** Field label */
  label: string;
  /** Whether the field is required */
  required?: boolean;
  /** Error message */
  error?: string;
  /** Help text displayed below the input */
  helpText?: string;
  /** Children (form input) */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** HTML for attribute - links label to input */
  htmlFor?: string;
}

/**
 * List Component Props
 */
export interface ListProps<T> {
  /** Array of items to render */
  items: T[];
  /** Function to render each item */
  renderItem: (item: T, index: number) => ReactNode;
  /** Loading state */
  loading?: boolean;
  /** Message to display when list is empty */
  emptyMessage?: string;
  /** Additional CSS classes */
  className?: string;
  /** Key extractor function */
  keyExtractor?: (item: T, index: number) => string | number;
}

/**
 * Card Component Props
 */
export type CardVariant = 'default' | 'outlined' | 'elevated';

export interface CardImageProps {
  /** Image source URL */
  src: string;
  /** Image alt text */
  alt: string;
}

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Card style variant */
  variant?: CardVariant;
  /** Image to display at the top of the card */
  image?: CardImageProps;
  /** Card title */
  title?: string;
  /** Card description text */
  description?: string;
  /** Action buttons or other elements */
  actions?: ReactNode;
  /** Whether the card is clickable */
  clickable?: boolean;
  /** Accessible label for clickable cards (required when clickable and no title) */
  ariaLabel?: string;
  /** Card content */
  children?: ReactNode;
}

/**
 * Table Column Definition
 */
export interface ColumnDef<T, K extends keyof T = keyof T> {
  /** Unique key for the column */
  key: K;
  /** Column header title */
  title: string;
  /** Whether the column is sortable */
  sortable?: boolean;
  /** Column width (CSS value) */
  width?: string;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
  /** Custom render function for the cell */
  render?: (value: T[K], row: T, rowIndex: number) => ReactNode;
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
}

/*
 * Tooltip Component Props
 */
export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';

export interface TooltipProps {
  /** Tooltip content text */
  content: string;
  /** Tooltip position relative to trigger element */
  position?: TooltipPosition;
  /** Delay in milliseconds before showing tooltip */
  delay?: number;
  /** Trigger element */
  children: ReactNode;
  /** Additional CSS classes for tooltip container */
  className?: string;
}

/**
 * Modal Component Props
 */
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl';

export interface ModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when the modal should close */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal size */
  size?: ModalSize;
  /** Modal content */
  children: ReactNode;
  /** Whether to close when clicking overlay */
  closeOnOverlayClick?: boolean;
  /** Whether to close when pressing ESC key */
  closeOnEsc?: boolean;
  /** Additional CSS classes for the modal content */
  className?: string;
}

/**
 * Accordion Component Props
 */
export interface AccordionItem {
  /** Unique identifier for the accordion item */
  id: string;
  /** Title text displayed in the accordion header */
  title: string;
  /** Content to display when accordion item is expanded */
  content: ReactNode;
}

export interface AccordionProps {
  /** Array of accordion items */
  items: AccordionItem[];
  /** Allow multiple items to be open simultaneously (default: true) */
  multiple?: boolean;
  /** Array of item IDs that should be open by default */
  defaultOpen?: string[];
  /** Additional CSS classes */
  className?: string;
}
