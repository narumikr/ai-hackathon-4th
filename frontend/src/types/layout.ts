import type { ReactNode } from 'react';

/**
 * Container Component Props
 */
export type ContainerVariant = 'standard' | 'wide' | 'full';

export interface ContainerProps {
  /** Container variant - determines max width */
  variant?: ContainerVariant;
  /** Content to display */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Navigation Item
 */
export interface NavigationItem {
  label: string;
  href: string;
}

/**
 * Navigation Props
 */
export interface NavigationProps {
  /** Current path for active state */
  currentPath?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Mobile Menu Props
 */
export interface MobileMenuProps {
  /** Whether the menu is open */
  isOpen: boolean;
  /** Handler for closing the menu */
  onClose: () => void;
  /** Current path for active state */
  currentPath?: string;
  /** Handler for sign out */
  onSignOut?: () => void;
  /** User email to display */
  userEmail?: string | null;
}

/**
 * Header Props
 */
export interface HeaderProps {
  /** Additional CSS classes */
  className?: string;
}

/**
 * Footer Props
 */
export interface FooterProps {
  /** Additional CSS classes */
  className?: string;
}
