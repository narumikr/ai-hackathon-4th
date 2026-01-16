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
