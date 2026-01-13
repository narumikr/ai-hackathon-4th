import { render } from '@testing-library/react';

import { LoadingSpinner } from './LoadingSpinner';

describe('LoadingSpinner', () => {
  const getSpinner = (container: HTMLElement) => container.querySelector('svg');

  describe('rendering', () => {
    it('renders a spinner', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toBeInTheDocument();
    });

    it('has aria-hidden attribute for accessibility', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('variants', () => {
    it('applies primary variant styles by default', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('text-primary-500');
    });

    it('applies primary variant styles when specified', () => {
      const { container } = render(<LoadingSpinner variant="primary" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('text-primary-500');
    });

    it('applies secondary variant styles when specified', () => {
      const { container } = render(<LoadingSpinner variant="secondary" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('text-current');
    });
  });

  describe('sizes', () => {
    it('applies medium size by default', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('w-4', 'h-4');
    });

    it('applies small size when specified', () => {
      const { container } = render(<LoadingSpinner size="sm" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('w-3.5', 'h-3.5');
    });

    it('applies medium size when specified', () => {
      const { container } = render(<LoadingSpinner size="md" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('w-4', 'h-4');
    });

    it('applies large size when specified', () => {
      const { container } = render(<LoadingSpinner size="lg" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('w-5', 'h-5');
    });

    it('applies extra large size when specified', () => {
      const { container } = render(<LoadingSpinner size="xl" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('w-6', 'h-6');
    });
  });

  describe('className prop', () => {
    it('applies additional className when provided', () => {
      const { container } = render(<LoadingSpinner className="custom-class" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('custom-class');
    });

    it('combines className with default classes', () => {
      const { container } = render(<LoadingSpinner size="lg" className="custom-class" />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('animate-spin', 'w-5', 'h-5', 'custom-class');
    });
  });

  describe('animation', () => {
    it('has spin animation class', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('animate-spin');
    });
  });
});
