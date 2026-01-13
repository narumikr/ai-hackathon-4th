import { fireEvent, render, screen } from '@testing-library/react';

import { Button } from './Button';

describe('Button', () => {
  describe('rendering', () => {
    it('renders children correctly', () => {
      render(<Button>Click me</Button>);

      expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
    });

    it('renders as a button element', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button.tagName).toBe('BUTTON');
    });

    it('has type="button" by default', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'button');
    });
  });

  describe('variants', () => {
    it('applies primary variant styles by default', () => {
      render(<Button>Primary</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-400');
    });

    it('applies primary variant styles when specified', () => {
      render(<Button variant="primary">Primary</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-400', 'text-primary-950', 'border-primary-600');
    });

    it('applies secondary variant styles when specified', () => {
      render(<Button variant="secondary">Secondary</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-white', 'text-primary-700', 'border-primary-400');
    });

    it('applies error variant styles when specified', () => {
      render(<Button variant="error">Error</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-danger', 'text-white', 'border-red-600');
    });

    it('applies ghost variant styles when specified', () => {
      render(<Button variant="ghost">Ghost</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-transparent', 'text-neutral-700', 'border-neutral-300');
    });
  });

  describe('sizes', () => {
    it('applies medium size by default', () => {
      render(<Button>Medium</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-base');
    });

    it('applies small size when specified', () => {
      render(<Button size="sm">Small</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm');
    });

    it('applies medium size when specified', () => {
      render(<Button size="md">Medium</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-base');
    });

    it('applies large size when specified', () => {
      render(<Button size="lg">Large</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('px-6', 'py-3', 'text-lg');
    });
  });

  describe('disabled state', () => {
    it('is not disabled by default', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).not.toBeDisabled();
    });

    it('is disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled</Button>);

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('has disabled cursor style when disabled', () => {
      render(<Button disabled>Disabled</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:cursor-not-allowed');
    });
  });

  describe('loading state', () => {
    it('shows loading spinner when loading is true', () => {
      const { container } = render(<Button loading>Loading</Button>);

      const spinner = container.querySelector('svg');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('animate-spin');
    });

    it('is disabled when loading is true', () => {
      render(<Button loading>Loading</Button>);

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('does not show spinner when loading is false', () => {
      const { container } = render(<Button loading={false}>Not Loading</Button>);

      const spinner = container.querySelector('svg');
      expect(spinner).not.toBeInTheDocument();
    });

    it('still renders children when loading', () => {
      render(<Button loading>Loading Text</Button>);

      expect(screen.getByText('Loading Text')).toBeInTheDocument();
    });
  });

  describe('fullWidth prop', () => {
    it('does not have full width by default', () => {
      render(<Button>Normal</Button>);

      const button = screen.getByRole('button');
      expect(button).not.toHaveClass('w-full');
    });

    it('has full width when fullWidth is true', () => {
      render(<Button fullWidth>Full Width</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full');
    });
  });

  describe('className prop', () => {
    it('applies additional className when provided', () => {
      render(<Button className="custom-class">Custom</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('custom-class');
    });

    it('combines className with default classes', () => {
      render(
        <Button variant="primary" className="custom-class">
          Custom
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-400', 'custom-class');
    });
  });

  describe('click handling', () => {
    it('calls onClick when clicked', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click me</Button>);

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const handleClick = vi.fn();
      render(
        <Button disabled onClick={handleClick}>
          Disabled
        </Button>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(handleClick).not.toHaveBeenCalled();
    });

    it('does not call onClick when loading', () => {
      const handleClick = vi.fn();
      render(
        <Button loading onClick={handleClick}>
          Loading
        </Button>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('HTML attributes', () => {
    it('passes through HTML button attributes', () => {
      render(
        <Button data-testid="test-button" aria-label="Test Button">
          Test
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('data-testid', 'test-button');
      expect(button).toHaveAttribute('aria-label', 'Test Button');
    });

    it('allows overriding type attribute', () => {
      render(<Button type="submit">Submit</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });
  });

  describe('base styles', () => {
    it('has inline-flex display', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('inline-flex');
    });

    it('has centered content', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('items-center', 'justify-center');
    });

    it('has rounded corners', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('rounded-lg');
    });

    it('has transition styles', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('transition-all');
    });
  });
});
