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

    it('has role status for accessibility', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveAttribute('role', 'status');
    });

    it('has aria-label for accessibility', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveAttribute('aria-label', '読み込み中');
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

  describe('SVG structure', () => {
    it('contains a circle element', () => {
      const { container } = render(<LoadingSpinner />);

      const circle = container.querySelector('circle');
      expect(circle).toBeInTheDocument();
    });

    it('circle has correct attributes', () => {
      const { container } = render(<LoadingSpinner />);

      const circle = container.querySelector('circle');
      expect(circle).toHaveAttribute('cx', '12');
      expect(circle).toHaveAttribute('cy', '12');
      expect(circle).toHaveAttribute('r', '10');
      expect(circle).toHaveAttribute('stroke', 'currentColor');
      expect(circle).toHaveAttribute('stroke-width', '4');
    });

    it('circle has opacity class', () => {
      const { container } = render(<LoadingSpinner />);

      const circle = container.querySelector('circle');
      expect(circle).toHaveClass('opacity-25');
    });

    it('contains a path element', () => {
      const { container } = render(<LoadingSpinner />);

      const path = container.querySelector('path');
      expect(path).toBeInTheDocument();
    });

    it('path has correct attributes', () => {
      const { container } = render(<LoadingSpinner />);

      const path = container.querySelector('path');
      expect(path).toHaveAttribute('fill', 'currentColor');
      expect(path).toHaveAttribute(
        'd',
        'M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
      );
    });

    it('path has opacity class', () => {
      const { container } = render(<LoadingSpinner />);

      const path = container.querySelector('path');
      expect(path).toHaveClass('opacity-75');
    });

    it('SVG has correct viewBox', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveAttribute('viewBox', '0 0 24 24');
    });

    it('SVG has no fill by default', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveAttribute('fill', 'none');
    });

    it('SVG has correct xmlns', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = getSpinner(container);
      expect(spinner).toHaveAttribute('xmlns', 'http://www.w3.org/2000/svg');
    });
  });

  describe('props combinations', () => {
    it('renders with all props combined', () => {
      const { container } = render(
        <LoadingSpinner variant="secondary" size="xl" className="custom-class" />
      );

      const spinner = getSpinner(container);
      expect(spinner).toHaveClass('animate-spin', 'w-6', 'h-6', 'text-current', 'custom-class');
      expect(spinner).toHaveAttribute('role', 'status');
      expect(spinner).toHaveAttribute('aria-label', '読み込み中');
    });

    it('maintains structure with custom props', () => {
      const { container } = render(<LoadingSpinner variant="primary" size="lg" className="mx-2" />);

      const spinner = getSpinner(container);
      const circle = container.querySelector('circle');
      const path = container.querySelector('path');

      expect(spinner).toBeInTheDocument();
      expect(circle).toBeInTheDocument();
      expect(path).toBeInTheDocument();
      expect(spinner).toHaveClass('text-primary-500', 'w-5', 'h-5', 'mx-2');
    });
  });
});
