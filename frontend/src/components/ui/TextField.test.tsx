import { fireEvent, render, screen } from '@testing-library/react';

import { TextField } from './TextField';

describe('TextField', () => {
  describe('rendering', () => {
    it('renders an input element', () => {
      render(<TextField />);

      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('renders with label when provided', () => {
      render(<TextField label="Email" />);

      expect(screen.getByLabelText('Email')).toBeInTheDocument();
    });

    it('renders required indicator when required', () => {
      render(<TextField label="Email" required />);

      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders placeholder when provided', () => {
      render(<TextField placeholder="Enter your email" />);

      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
    });
  });

  describe('sizes', () => {
    it('applies medium size by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('px-4', 'py-2', 'text-base');
    });

    it('applies small size when specified', () => {
      render(<TextField size="sm" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('px-3', 'py-1.5', 'text-sm');
    });

    it('applies large size when specified', () => {
      render(<TextField size="lg" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('px-4', 'py-3', 'text-lg');
    });
  });

  describe('error state', () => {
    it('displays error message when error prop is provided', () => {
      render(<TextField error="This field is required" />);

      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('applies error styles when error prop is provided', () => {
      render(<TextField error="Error" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('border-red-400');
    });

    it('sets aria-invalid when error prop is provided', () => {
      render(<TextField error="Error" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('help text', () => {
    it('displays help text when provided', () => {
      render(<TextField helpText="Enter a valid email address" />);

      expect(screen.getByText('Enter a valid email address')).toBeInTheDocument();
    });

    it('hides help text when error is present', () => {
      render(<TextField helpText="Help text" error="Error message" />);

      expect(screen.queryByText('Help text')).not.toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });
  });

  describe('disabled state', () => {
    it('is not disabled by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
    });

    it('is disabled when disabled prop is true', () => {
      render(<TextField disabled />);

      const input = screen.getByRole('textbox');
      expect(input).toBeDisabled();
    });
  });

  describe('fullWidth prop', () => {
    it('does not have full width by default', () => {
      const { container } = render(<TextField />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('inline-block');
    });

    it('has full width when fullWidth is true', () => {
      const { container } = render(<TextField fullWidth />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('w-full');
    });
  });

  describe('onChange handler', () => {
    it('calls onChange with input value when changed', () => {
      const handleChange = vi.fn();
      render(<TextField onChange={handleChange} />);

      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'test@example.com' } });

      expect(handleChange).toHaveBeenCalledWith('test@example.com');
    });

    it('works without onChange handler', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(() => {
        fireEvent.change(input, { target: { value: 'test' } });
      }).not.toThrow();
    });
  });

  describe('HTML attributes', () => {
    it('passes through HTML input attributes', () => {
      render(<TextField data-testid="test-input" aria-label="Test Input" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('data-testid', 'test-input');
      expect(input).toHaveAttribute('aria-label', 'Test Input');
    });

    it('allows setting custom id', () => {
      render(<TextField id="custom-id" label="Custom" />);

      const input = screen.getByLabelText('Custom');
      expect(input).toHaveAttribute('id', 'custom-id');
    });

    it('allows setting input type', () => {
      render(<TextField type="email" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('type', 'email');
    });
  });

  describe('className prop', () => {
    it('applies additional className to input when provided', () => {
      render(<TextField className="custom-class" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('custom-class');
    });
  });

  describe('base styles', () => {
    it('has rounded corners', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('rounded-lg');
    });

    it('has transition styles', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('transition-all');
    });

    it('has white background', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('bg-white');
    });
  });
});
