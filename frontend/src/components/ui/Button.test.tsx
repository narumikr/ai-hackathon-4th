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

    it('has font-medium class', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('font-medium');
    });

    it('has select-none class', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('select-none');
    });

    it('has focus-visible ring styles', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus-visible:ring-2', 'focus-visible:ring-offset-2');
    });
  });

  describe('name prop', () => {
    it('applies name attribute when provided', () => {
      render(<Button name="submit-btn">Submit</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('name', 'submit-btn');
    });
  });

  describe('form prop', () => {
    it('applies form attribute when provided', () => {
      render(<Button form="my-form">Submit</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('form', 'my-form');
    });
  });

  describe('formAction prop', () => {
    it('applies formAction attribute when provided', () => {
      render(
        <Button type="submit" formAction="/api/submit">
          Submit
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('formaction', '/api/submit');
    });
  });

  describe('id prop', () => {
    it('applies id attribute when provided', () => {
      render(<Button id="my-button">Click</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('id', 'my-button');
    });
  });

  describe('aria props', () => {
    it('applies aria-pressed when provided', () => {
      render(<Button aria-pressed="true">Toggle</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-pressed', 'true');
    });

    it('applies aria-expanded when provided', () => {
      render(<Button aria-expanded="false">Expand</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'false');
    });

    it('applies aria-haspopup when provided', () => {
      render(<Button aria-haspopup="menu">Menu</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-haspopup', 'menu');
    });

    it('applies aria-describedby when provided', () => {
      render(<Button aria-describedby="help-text">Help</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-describedby', 'help-text');
    });
  });

  describe('focus and blur handling', () => {
    it('calls onFocus when focused', () => {
      const handleFocus = vi.fn();
      render(<Button onFocus={handleFocus}>Focus me</Button>);

      const button = screen.getByRole('button');
      fireEvent.focus(button);

      expect(handleFocus).toHaveBeenCalledTimes(1);
    });

    it('calls onBlur when blurred', () => {
      const handleBlur = vi.fn();
      render(<Button onBlur={handleBlur}>Blur me</Button>);

      const button = screen.getByRole('button');
      fireEvent.focus(button);
      fireEvent.blur(button);

      expect(handleBlur).toHaveBeenCalledTimes(1);
    });
  });

  describe('mouse events', () => {
    it('calls onMouseEnter when mouse enters', () => {
      const handleMouseEnter = vi.fn();
      render(<Button onMouseEnter={handleMouseEnter}>Hover me</Button>);

      const button = screen.getByRole('button');
      fireEvent.mouseEnter(button);

      expect(handleMouseEnter).toHaveBeenCalledTimes(1);
    });

    it('calls onMouseLeave when mouse leaves', () => {
      const handleMouseLeave = vi.fn();
      render(<Button onMouseLeave={handleMouseLeave}>Hover me</Button>);

      const button = screen.getByRole('button');
      fireEvent.mouseEnter(button);
      fireEvent.mouseLeave(button);

      expect(handleMouseLeave).toHaveBeenCalledTimes(1);
    });
  });

  describe('disabled styles per variant', () => {
    it('applies disabled styles for primary variant', () => {
      render(
        <Button variant="primary" disabled>
          Primary Disabled
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:bg-primary-200', 'disabled:border-primary-300');
    });

    it('applies disabled styles for secondary variant', () => {
      render(
        <Button variant="secondary" disabled>
          Secondary Disabled
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:bg-neutral-50', 'disabled:text-primary-300');
    });

    it('applies disabled styles for error variant', () => {
      render(
        <Button variant="error" disabled>
          Error Disabled
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:bg-red-200', 'disabled:text-red-400');
    });

    it('applies disabled styles for ghost variant', () => {
      render(
        <Button variant="ghost" disabled>
          Ghost Disabled
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:text-neutral-300', 'disabled:bg-transparent');
    });
  });

  describe('loading spinner', () => {
    it('uses secondary variant for spinner to inherit button text color', () => {
      const { container } = render(<Button loading>Loading</Button>);

      const spinner = container.querySelector('svg');
      expect(spinner).toHaveClass('text-current');
    });

    it('spinner size matches small button size', () => {
      const { container } = render(
        <Button size="sm" loading>
          Loading
        </Button>
      );

      const spinner = container.querySelector('svg');
      expect(spinner).toHaveClass('w-3.5', 'h-3.5');
    });

    it('spinner size matches medium button size', () => {
      const { container } = render(
        <Button size="md" loading>
          Loading
        </Button>
      );

      const spinner = container.querySelector('svg');
      expect(spinner).toHaveClass('w-4', 'h-4');
    });

    it('spinner size matches large button size', () => {
      const { container } = render(
        <Button size="lg" loading>
          Loading
        </Button>
      );

      const spinner = container.querySelector('svg');
      expect(spinner).toHaveClass('w-5', 'h-5');
    });
  });

  describe('fullWidth with different variants', () => {
    it('fullWidth works with primary variant', () => {
      render(
        <Button variant="primary" fullWidth>
          Full Width Primary
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full', 'bg-primary-400');
    });

    it('fullWidth works with secondary variant', () => {
      render(
        <Button variant="secondary" fullWidth>
          Full Width Secondary
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-full', 'bg-white');
    });
  });

  describe('props combinations', () => {
    it('renders with all props combined', () => {
      const handleClick = vi.fn();
      render(
        <Button
          variant="primary"
          size="lg"
          fullWidth
          name="submit"
          type="submit"
          form="my-form"
          id="submit-button"
          className="custom-class"
          aria-label="Submit form"
          onClick={handleClick}
        >
          Submit
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('name', 'submit');
      expect(button).toHaveAttribute('type', 'submit');
      expect(button).toHaveAttribute('form', 'my-form');
      expect(button).toHaveAttribute('id', 'submit-button');
      expect(button).toHaveAttribute('aria-label', 'Submit form');
      expect(button).toHaveClass('bg-primary-400', 'px-6', 'py-3', 'w-full', 'custom-class');

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('renders loading state with all visual props', () => {
      const { container } = render(
        <Button variant="secondary" size="sm" fullWidth loading className="custom-class">
          Loading...
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('bg-white', 'px-3', 'py-1.5', 'w-full', 'custom-class');

      const spinner = container.querySelector('svg');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('w-3.5', 'h-3.5');
    });

    it('disabled takes precedence over loading for click events', () => {
      const handleClick = vi.fn();
      render(
        <Button disabled loading onClick={handleClick}>
          Disabled Loading
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();

      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('children prop', () => {
    it('renders string children', () => {
      render(<Button>Click me</Button>);

      expect(screen.getByText('Click me')).toBeInTheDocument();
    });

    it('renders element children', () => {
      render(
        <Button>
          <span data-testid="child-element">Icon</span>
        </Button>
      );

      expect(screen.getByTestId('child-element')).toBeInTheDocument();
    });

    it('renders multiple children', () => {
      render(
        <Button>
          <span>Icon</span>
          <span>Text</span>
        </Button>
      );

      expect(screen.getByText('Icon')).toBeInTheDocument();
      expect(screen.getByText('Text')).toBeInTheDocument();
    });
  });

  describe('gap styles for loading state', () => {
    it('has gap-1.5 for small size', () => {
      render(
        <Button size="sm" loading>
          Loading
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('gap-1.5');
    });

    it('has gap-2 for medium size', () => {
      render(
        <Button size="md" loading>
          Loading
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('gap-2');
    });

    it('has gap-2.5 for large size', () => {
      render(
        <Button size="lg" loading>
          Loading
        </Button>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('gap-2.5');
    });
  });

  describe('interaction styles', () => {
    describe('primary variant hover styles', () => {
      it('has hover background color', () => {
        render(<Button variant="primary">Primary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:bg-primary-500');
      });

      it('has hover border color', () => {
        render(<Button variant="primary">Primary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:border-primary-700');
      });

      it('has hover shadow', () => {
        render(<Button variant="primary">Primary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:shadow-md');
      });
    });

    describe('secondary variant hover styles', () => {
      it('has hover background color', () => {
        render(<Button variant="secondary">Secondary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:bg-primary-50');
      });

      it('has hover border color', () => {
        render(<Button variant="secondary">Secondary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:border-primary-500');
      });

      it('has hover text color', () => {
        render(<Button variant="secondary">Secondary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:text-primary-800');
      });
    });

    describe('error variant hover styles', () => {
      it('has hover background color', () => {
        render(<Button variant="error">Error</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:bg-red-600');
      });

      it('has hover border color', () => {
        render(<Button variant="error">Error</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:border-red-700');
      });

      it('has hover shadow', () => {
        render(<Button variant="error">Error</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:shadow-md');
      });
    });

    describe('ghost variant hover styles', () => {
      it('has hover background color', () => {
        render(<Button variant="ghost">Ghost</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:bg-neutral-100');
      });

      it('has hover text color', () => {
        render(<Button variant="ghost">Ghost</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:text-neutral-900');
      });

      it('has hover border color', () => {
        render(<Button variant="ghost">Ghost</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('hover:border-neutral-400');
      });
    });

    describe('active styles', () => {
      it('has active styles for primary variant', () => {
        render(<Button variant="primary">Primary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('active:bg-primary-600', 'active:border-primary-800');
      });

      it('has active styles for secondary variant', () => {
        render(<Button variant="secondary">Secondary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('active:bg-primary-100', 'active:border-primary-600');
      });

      it('has active styles for error variant', () => {
        render(<Button variant="error">Error</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('active:bg-red-700', 'active:border-red-800');
      });

      it('has active styles for ghost variant', () => {
        render(<Button variant="ghost">Ghost</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('active:bg-neutral-200', 'active:border-neutral-500');
      });
    });

    describe('focus-visible ring styles', () => {
      it('has focus-visible ring for primary variant', () => {
        render(<Button variant="primary">Primary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('focus-visible:ring-primary-300');
      });

      it('has focus-visible ring for secondary variant', () => {
        render(<Button variant="secondary">Secondary</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('focus-visible:ring-primary-300');
      });

      it('has focus-visible ring for error variant', () => {
        render(<Button variant="error">Error</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('focus-visible:ring-red-300');
      });

      it('has focus-visible ring for ghost variant', () => {
        render(<Button variant="ghost">Ghost</Button>);

        const button = screen.getByRole('button');
        expect(button).toHaveClass('focus-visible:ring-neutral-300');
      });
    });
  });

  describe('transition styles', () => {
    it('has transition-all class', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('transition-all');
    });

    it('has duration-200 class', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('duration-200');
    });

    it('has ease-out class', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('ease-out');
    });
  });

  describe('focus styles', () => {
    it('has focus:outline-none class', () => {
      render(<Button>Test</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus:outline-none');
    });
  });

  describe('border styles', () => {
    it('has border class for primary variant', () => {
      render(<Button variant="primary">Primary</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border');
    });

    it('has border class for secondary variant', () => {
      render(<Button variant="secondary">Secondary</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border');
    });

    it('has border class for error variant', () => {
      render(<Button variant="error">Error</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border');
    });

    it('has border class for ghost variant', () => {
      render(<Button variant="ghost">Ghost</Button>);

      const button = screen.getByRole('button');
      expect(button).toHaveClass('border');
    });
  });
});
