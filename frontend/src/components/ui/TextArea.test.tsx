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

  describe('value prop', () => {
    it('renders with controlled value', () => {
      render(<TextArea value="test value" onChange={() => {}} />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveValue('test value');
    });

    it('renders with empty value', () => {
      render(<TextArea value="" onChange={() => {}} />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveValue('');
    });

    it('renders with multiline value', () => {
      render(<TextArea value={'line1\nline2\nline3'} onChange={() => {}} />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveValue('line1\nline2\nline3');
    });
  });

  describe('name prop', () => {
    it('applies name attribute when provided', () => {
      render(<TextArea name="description" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('name', 'description');
    });
  });

  describe('readOnly prop', () => {
    it('is not readOnly by default', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveAttribute('readonly');
    });

    it('is readOnly when readOnly prop is true', () => {
      render(<TextArea readOnly />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('readonly');
    });
  });

  describe('maxLength prop', () => {
    it('applies maxLength attribute when provided', () => {
      render(<TextArea maxLength={500} />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('maxlength', '500');
    });

    it('works with maxLength but without showCount', () => {
      render(<TextArea maxLength={100} value="test" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('maxlength', '100');
      expect(screen.queryByText('4/100')).not.toBeInTheDocument();
    });
  });

  describe('autoComplete prop', () => {
    it('applies autoComplete attribute when provided', () => {
      render(<TextArea autoComplete="off" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('autocomplete', 'off');
    });
  });

  describe('autoFocus prop', () => {
    it('does not have autoFocus by default', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveAttribute('autofocus');
    });
  });

  describe('normal state styles', () => {
    it('has neutral border by default', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('border-neutral-300');
    });

    it('does not have error border by default', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveClass('border-red-400');
    });

    it('does not set aria-invalid by default', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveAttribute('aria-invalid');
    });
  });

  describe('accessibility', () => {
    it('associates label with textarea via htmlFor', () => {
      render(<TextArea label="Description" id="desc-input" />);

      const label = screen.getByText('Description');
      expect(label).toHaveAttribute('for', 'desc-input');
    });

    it('associates error message with textarea via aria-describedby', () => {
      render(<TextArea id="test-textarea" error="Error message" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('aria-describedby', 'test-textarea-error');
    });

    it('associates help text with textarea via aria-describedby', () => {
      render(<TextArea id="test-textarea" helpText="Help text" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('aria-describedby', 'test-textarea-help');
    });

    it('does not have aria-describedby when no error or help text', () => {
      render(<TextArea />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveAttribute('aria-describedby');
    });

    it('generates unique id when not provided', () => {
      render(<TextArea label="Test" />);

      const textarea = screen.getByLabelText('Test');
      expect(textarea).toHaveAttribute('id');
    });
  });

  describe('label without required', () => {
    it('renders label without required indicator when required is false', () => {
      render(<TextArea label="Optional Field" required={false} />);

      expect(screen.getByText('Optional Field')).toBeInTheDocument();
      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });

    it('renders label without required indicator when required is not provided', () => {
      render(<TextArea label="Optional Field" />);

      expect(screen.getByText('Optional Field')).toBeInTheDocument();
      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });
  });

  describe('showCount prop', () => {
    it('does not show count when showCount is false', () => {
      render(<TextArea maxLength={100} value="test" showCount={false} />);

      expect(screen.queryByText('4/100')).not.toBeInTheDocument();
    });

    it('shows count only when both showCount and maxLength are provided', () => {
      render(<TextArea value="test" showCount />);

      expect(screen.queryByText(/\/\d+/)).not.toBeInTheDocument();
    });

    it('updates count when value changes', () => {
      const { rerender } = render(<TextArea maxLength={100} value="test" showCount />);

      expect(screen.getByText('4/100')).toBeInTheDocument();

      rerender(<TextArea maxLength={100} value="longer text" showCount />);

      expect(screen.getByText('11/100')).toBeInTheDocument();
    });
  });

  describe('over limit state', () => {
    it('applies error styles when value exceeds maxLength', () => {
      render(<TextArea maxLength={5} value="toolong" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveClass('border-red-400');
    });

    it('sets aria-invalid when value exceeds maxLength', () => {
      render(<TextArea maxLength={5} value="toolong" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveAttribute('aria-invalid', 'true');
    });

    it('does not apply error styles when value is within maxLength', () => {
      render(<TextArea maxLength={100} value="short" />);

      const textarea = screen.getByRole('textbox');
      expect(textarea).not.toHaveClass('border-red-400');
    });
  });

  describe('props combinations', () => {
    it('renders with all props combined', () => {
      const handleChange = vi.fn();
      render(
        <TextArea
          label="Description"
          placeholder="Enter description"
          helpText="Maximum 500 characters"
          rows={6}
          maxLength={500}
          showCount
          fullWidth
          required
          name="description"
          value="This is a test description"
          onChange={handleChange}
          className="custom-class"
        />
      );

      const textarea = screen.getByRole('textbox');
      expect(textarea).toHaveValue('This is a test description');
      expect(textarea).toHaveAttribute('name', 'description');
      expect(textarea).toHaveAttribute('rows', '6');
      expect(textarea).toHaveAttribute('maxlength', '500');
      expect(textarea).toHaveClass('custom-class');
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('*')).toBeInTheDocument();
      expect(screen.getByText('Maximum 500 characters')).toBeInTheDocument();
      expect(screen.getByText('26/500')).toBeInTheDocument();
    });

    it('renders with error state and all visual props', () => {
      render(
        <TextArea
          label="Description"
          error="Description is required"
          rows={8}
          maxLength={200}
          showCount
          fullWidth
          required
          disabled
          value=""
        />
      );

      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeDisabled();
      expect(textarea).toHaveClass('border-red-400');
      expect(textarea).toHaveAttribute('aria-invalid', 'true');
      expect(textarea).toHaveAttribute('rows', '8');
      expect(screen.getByText('Description is required')).toBeInTheDocument();
      expect(screen.getByText('0/200')).toBeInTheDocument();
    });

    it('renders with help text and character count together', () => {
      render(<TextArea helpText="Enter your message" maxLength={100} showCount value="Hello" />);

      expect(screen.getByText('Enter your message')).toBeInTheDocument();
      expect(screen.getByText('5/100')).toBeInTheDocument();
    });

    it('error takes priority over help text', () => {
      render(
        <TextArea
          helpText="Help text"
          error="Error message"
          maxLength={100}
          showCount
          value="test"
        />
      );

      expect(screen.queryByText('Help text')).not.toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
      expect(screen.getByText('4/100')).toBeInTheDocument();
    });
  });
});
