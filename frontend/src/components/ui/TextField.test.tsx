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

  describe('value prop', () => {
    it('renders with controlled value', () => {
      render(<TextField value="test value" onChange={() => {}} />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('test value');
    });

    it('renders with empty value', () => {
      render(<TextField value="" onChange={() => {}} />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('');
    });
  });

  describe('name prop', () => {
    it('applies name attribute when provided', () => {
      render(<TextField name="email" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('name', 'email');
    });
  });

  describe('readOnly prop', () => {
    it('is not readOnly by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).not.toHaveAttribute('readonly');
    });

    it('is readOnly when readOnly prop is true', () => {
      render(<TextField readOnly />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('readonly');
    });
  });

  describe('maxLength prop', () => {
    it('applies maxLength attribute when provided', () => {
      render(<TextField maxLength={100} />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('maxlength', '100');
    });
  });

  describe('minLength prop', () => {
    it('applies minLength attribute when provided', () => {
      render(<TextField minLength={5} />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('minlength', '5');
    });
  });

  describe('pattern prop', () => {
    it('applies pattern attribute when provided', () => {
      render(<TextField pattern="[A-Za-z]+" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('pattern', '[A-Za-z]+');
    });
  });

  describe('autoComplete prop', () => {
    it('applies autoComplete attribute when provided', () => {
      render(<TextField autoComplete="email" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('autocomplete', 'email');
    });
  });

  describe('autoFocus prop', () => {
    it('does not have autoFocus by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).not.toHaveAttribute('autofocus');
    });
  });

  describe('normal state styles', () => {
    it('has neutral border by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('border-neutral-300');
    });

    it('does not have error border by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).not.toHaveClass('border-red-400');
    });

    it('does not set aria-invalid by default', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).not.toHaveAttribute('aria-invalid');
    });
  });

  describe('accessibility', () => {
    it('associates label with input via htmlFor', () => {
      render(<TextField label="Email" id="email-input" />);

      const label = screen.getByText('Email');
      expect(label).toHaveAttribute('for', 'email-input');
    });

    it('associates error message with input via aria-describedby', () => {
      render(<TextField id="test-input" error="Error message" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-describedby', 'test-input-error');
    });

    it('associates help text with input via aria-describedby', () => {
      render(<TextField id="test-input" helpText="Help text" />);

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-describedby', 'test-input-help');
    });

    it('does not have aria-describedby when no error or help text', () => {
      render(<TextField />);

      const input = screen.getByRole('textbox');
      expect(input).not.toHaveAttribute('aria-describedby');
    });

    it('generates unique id when not provided', () => {
      render(<TextField label="Test" />);

      const input = screen.getByLabelText('Test');
      expect(input).toHaveAttribute('id');
    });
  });

  describe('label without required', () => {
    it('renders label without required indicator when required is false', () => {
      render(<TextField label="Optional Field" required={false} />);

      expect(screen.getByText('Optional Field')).toBeInTheDocument();
      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });

    it('renders label without required indicator when required is not provided', () => {
      render(<TextField label="Optional Field" />);

      expect(screen.getByText('Optional Field')).toBeInTheDocument();
      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });
  });

  describe('props combinations', () => {
    it('renders with all props combined', () => {
      const handleChange = vi.fn();
      render(
        <TextField
          label="Email"
          placeholder="Enter email"
          helpText="We will never share your email"
          size="lg"
          fullWidth
          required
          name="email"
          type="email"
          autoComplete="email"
          value="test@example.com"
          onChange={handleChange}
          className="custom-class"
        />
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveValue('test@example.com');
      expect(input).toHaveAttribute('name', 'email');
      expect(input).toHaveAttribute('type', 'email');
      expect(input).toHaveAttribute('autocomplete', 'email');
      expect(input).toHaveClass('px-4', 'py-3', 'text-lg', 'custom-class');
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('*')).toBeInTheDocument();
      expect(screen.getByText('We will never share your email')).toBeInTheDocument();
    });

    it('renders with error state and all visual props', () => {
      render(
        <TextField
          label="Email"
          error="Invalid email format"
          size="sm"
          fullWidth
          required
          disabled
        />
      );

      const input = screen.getByRole('textbox');
      expect(input).toBeDisabled();
      expect(input).toHaveClass('border-red-400', 'px-3', 'py-1.5', 'text-sm');
      expect(input).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText('Invalid email format')).toBeInTheDocument();
    });
  });
});
