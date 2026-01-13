import { fireEvent, render, screen } from '@testing-library/react';

import { TextArea } from './TextArea';

describe('TextArea', () => {
  describe('rendering', () => {
    it('renders a textarea element', () => {
      render(<TextArea />);

      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('renders with label when provided', () => {
      render(<TextArea label="Description" />);

      expect(screen.getByLabelText('Description')).toBeInTheDocument();
    });

    it('renders required indicator when required', () => {
      render(<TextArea label="Description" required />);

      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('renders placeholder when provided', () => {
      render(<TextArea placeholder="Enter your description" />);

      expect(screen.getByPlaceholderText('Enter your description')).toBeInTheDocument();
    });

    it('renders with default rows of 4', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('rows', '4');
    });

    it('renders with custom rows when specified', () => {
      render(<TextArea rows={6} />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('rows', '6');
    });
  });

  describe('error state', () => {
    it('displays error message when error prop is provided', () => {
      render(<TextArea error="This field is required" />);

      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });

    it('applies error styles when error prop is provided', () => {
      render(<TextArea error="Error" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('border-red-400');
    });

    it('sets aria-invalid when error prop is provided', () => {
      render(<TextArea error="Error" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('help text', () => {
    it('displays help text when provided', () => {
      render(<TextArea helpText="Maximum 500 characters" />);

      expect(screen.getByText('Maximum 500 characters')).toBeInTheDocument();
    });

    it('hides help text when error is present', () => {
      render(<TextArea helpText="Help text" error="Error message" />);

      expect(screen.queryByText('Help text')).not.toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });
  });

  describe('character count', () => {
    it('does not show character count by default', () => {
      render(<TextArea maxLength={100} value="test" />);

      expect(screen.queryByText('4/100')).not.toBeInTheDocument();
    });

    it('shows character count when showCount is true', () => {
      render(<TextArea maxLength={100} value="test" showCount />);

      expect(screen.getByText('4/100')).toBeInTheDocument();
    });

    it('shows 0 count when value is empty', () => {
      render(<TextArea maxLength={100} value="" showCount />);

      expect(screen.getByText('0/100')).toBeInTheDocument();
    });

    it('applies error style to count when over limit', () => {
      render(<TextArea maxLength={5} value="toolong" showCount />);

      const countText = screen.getByText('7/5');
      expect(countText).toHaveClass('text-red-600');
    });
  });

  describe('disabled state', () => {
    it('is not disabled by default', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toBeDisabled();
    });

    it('is disabled when disabled prop is true', () => {
      render(<TextArea disabled />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeDisabled();
    });
  });

  describe('fullWidth prop', () => {
    it('does not have full width by default', () => {
      const { container } = render(<TextArea />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('inline-block');
    });

    it('has full width when fullWidth is true', () => {
      const { container } = render(<TextArea fullWidth />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('w-full');
    });
  });

  describe('onChange handler', () => {
    it('calls onChange with textarea value when changed', () => {
      const handleChange = vi.fn();
      render(<TextArea onChange={handleChange} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Hello World' } });

      expect(handleChange).toHaveBeenCalledWith('Hello World');
    });

    it('works without onChange handler', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(() => {
        fireEvent.change(textarea, { target: { value: 'test' } });
      }).not.toThrow();
    });
  });

  describe('HTML attributes', () => {
    it('passes through HTML textarea attributes', () => {
      render(<TextArea data-testid="test-textarea" aria-label="Test TextArea" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('data-testid', 'test-textarea');
      expect(textarea).toHaveAttribute('aria-label', 'Test TextArea');
    });

    it('allows setting custom id', () => {
      render(<TextArea id="custom-id" label="Custom" />);

      const textarea = screen.getByLabelText('Custom');
      expect(textarea).toHaveAttribute('id', 'custom-id');
    });
  });

  describe('className prop', () => {
    it('applies additional className to textarea when provided', () => {
      render(<TextArea className="custom-class" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('custom-class');
    });
  });

  describe('base styles', () => {
    it('has rounded corners', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('rounded-lg');
    });

    it('has transition styles', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('transition-all');
    });

    it('has white background', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('bg-white');
    });

    it('has resize-y class for vertical resize', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('resize-y');
    });
  });
});
