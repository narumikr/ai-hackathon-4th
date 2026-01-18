import { render, screen } from '@testing-library/react';

import { FormField } from './FormField';

describe('FormField', () => {
  describe('rendering', () => {
    it('renders label correctly', () => {
      render(
        <FormField label="Email">
          <input type="email" />
        </FormField>
      );

      expect(screen.getByText('Email')).toBeInTheDocument();
    });

    it('renders children correctly', () => {
      render(
        <FormField label="Name">
          <input type="text" data-testid="name-input" />
        </FormField>
      );

      expect(screen.getByTestId('name-input')).toBeInTheDocument();
    });

    it('renders as a div wrapper', () => {
      const { container } = render(
        <FormField label="Test">
          <input type="text" />
        </FormField>
      );

      expect(container.firstChild?.nodeName).toBe('DIV');
    });
  });

  describe('required field', () => {
    it('does not show required mark by default', () => {
      render(
        <FormField label="Optional Field">
          <input type="text" />
        </FormField>
      );

      expect(screen.queryByText('*')).not.toBeInTheDocument();
    });

    it('shows required mark when required is true', () => {
      render(
        <FormField label="Required Field" required>
          <input type="text" />
        </FormField>
      );

      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('required mark has aria-hidden attribute', () => {
      render(
        <FormField label="Required Field" required>
          <input type="text" />
        </FormField>
      );

      const requiredMark = screen.getByText('*');
      expect(requiredMark).toHaveAttribute('aria-hidden', 'true');
    });

    it('required mark has red color style', () => {
      render(
        <FormField label="Required Field" required>
          <input type="text" />
        </FormField>
      );

      const requiredMark = screen.getByText('*');
      expect(requiredMark).toHaveClass('text-red-500');
    });
  });

  describe('error state', () => {
    it('does not show error message by default', () => {
      render(
        <FormField label="Field">
          <input type="text" />
        </FormField>
      );

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('shows error message when error prop is provided', () => {
      render(
        <FormField label="Email" error="Invalid email format">
          <input type="email" />
        </FormField>
      );

      expect(screen.getByText('Invalid email format')).toBeInTheDocument();
    });

    it('error message has role="alert"', () => {
      render(
        <FormField label="Email" error="Invalid email">
          <input type="email" />
        </FormField>
      );

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('Invalid email');
    });

    it('error message has red color style', () => {
      render(
        <FormField label="Email" error="Error message">
          <input type="email" />
        </FormField>
      );

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveClass('text-red-600');
    });

    it('sets data-error attribute when error is present', () => {
      const { container } = render(
        <FormField label="Email" error="Error">
          <input type="email" />
        </FormField>
      );

      const childrenWrapper = container.querySelector('[data-error="true"]');
      expect(childrenWrapper).toBeInTheDocument();
    });
  });

  describe('help text', () => {
    it('does not show help text by default', () => {
      render(
        <FormField label="Field">
          <input type="text" />
        </FormField>
      );

      const wrapper = screen.getByText('Field').closest('div');
      const paragraphs = wrapper?.parentElement?.querySelectorAll('p');
      expect(paragraphs?.length ?? 0).toBe(0);
    });

    it('shows help text when helpText prop is provided', () => {
      render(
        <FormField label="Password" helpText="At least 8 characters">
          <input type="password" />
        </FormField>
      );

      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
    });

    it('help text has neutral color style', () => {
      render(
        <FormField label="Field" helpText="Help text">
          <input type="text" />
        </FormField>
      );

      const helpText = screen.getByText('Help text');
      expect(helpText).toHaveClass('text-neutral-500');
    });

    it('hides help text when error is present', () => {
      render(
        <FormField label="Email" helpText="Enter your email" error="Invalid email">
          <input type="email" />
        </FormField>
      );

      expect(screen.queryByText('Enter your email')).not.toBeInTheDocument();
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });
  });

  describe('label styling', () => {
    it('label has font-medium class', () => {
      render(
        <FormField label="Field Label">
          <input type="text" />
        </FormField>
      );

      const label = screen.getByText('Field Label');
      expect(label).toHaveClass('font-medium');
    });

    it('label has small text size', () => {
      render(
        <FormField label="Field Label">
          <input type="text" />
        </FormField>
      );

      const label = screen.getByText('Field Label');
      expect(label).toHaveClass('text-sm');
    });

    it('label has neutral-700 text color', () => {
      render(
        <FormField label="Field Label">
          <input type="text" />
        </FormField>
      );

      const label = screen.getByText('Field Label');
      expect(label).toHaveClass('text-neutral-700');
    });

    it('label has margin-bottom', () => {
      render(
        <FormField label="Field Label">
          <input type="text" />
        </FormField>
      );

      const label = screen.getByText('Field Label');
      expect(label).toHaveClass('mb-1.5');
    });
  });

  describe('htmlFor prop', () => {
    it('uses provided htmlFor for label', () => {
      render(
        <FormField label="Email" htmlFor="email-input">
          <input type="email" id="email-input" />
        </FormField>
      );

      const label = screen.getByText('Email');
      expect(label).toHaveAttribute('for', 'email-input');
    });

    it('generates unique id when htmlFor is not provided', () => {
      render(
        <FormField label="Field">
          <input type="text" />
        </FormField>
      );

      const label = screen.getByText('Field');
      expect(label).toHaveAttribute('for');
      expect(label.getAttribute('for')).not.toBe('');
    });
  });

  describe('className prop', () => {
    it('applies additional className when provided', () => {
      const { container } = render(
        <FormField label="Field" className="custom-class">
          <input type="text" />
        </FormField>
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('combines className with default classes', () => {
      const { container } = render(
        <FormField label="Field" className="custom-class">
          <input type="text" />
        </FormField>
      );

      expect(container.firstChild).toHaveClass('w-full', 'custom-class');
    });
  });

  describe('base styles', () => {
    it('has full width by default', () => {
      const { container } = render(
        <FormField label="Field">
          <input type="text" />
        </FormField>
      );

      expect(container.firstChild).toHaveClass('w-full');
    });
  });

  describe('accessibility', () => {
    it('has aria-describedby pointing to error when error exists', () => {
      const { container } = render(
        <FormField label="Email" error="Invalid email">
          <input type="email" />
        </FormField>
      );

      const childrenWrapper = container.querySelector('[aria-describedby]');
      expect(childrenWrapper).toBeInTheDocument();
      expect(childrenWrapper?.getAttribute('aria-describedby')).toContain('-error');
    });

    it('has aria-describedby pointing to help text when no error', () => {
      const { container } = render(
        <FormField label="Email" helpText="Help text">
          <input type="email" />
        </FormField>
      );

      const childrenWrapper = container.querySelector('[aria-describedby]');
      expect(childrenWrapper).toBeInTheDocument();
      expect(childrenWrapper?.getAttribute('aria-describedby')).toContain('-help');
    });

    it('has no aria-describedby when neither error nor helpText', () => {
      const { container } = render(
        <FormField label="Email">
          <input type="email" />
        </FormField>
      );

      const childrenWrapper = container.querySelector('[aria-describedby]');
      expect(childrenWrapper).not.toBeInTheDocument();
    });
  });

  describe('with different input types', () => {
    it('works with text input', () => {
      render(
        <FormField label="Name">
          <input type="text" placeholder="Enter name" />
        </FormField>
      );

      expect(screen.getByPlaceholderText('Enter name')).toBeInTheDocument();
    });

    it('works with select element', () => {
      render(
        <FormField label="Country">
          <select data-testid="country-select">
            <option value="jp">Japan</option>
            <option value="us">USA</option>
          </select>
        </FormField>
      );

      expect(screen.getByTestId('country-select')).toBeInTheDocument();
    });

    it('works with textarea', () => {
      render(
        <FormField label="Description">
          <textarea placeholder="Enter description" />
        </FormField>
      );

      expect(screen.getByPlaceholderText('Enter description')).toBeInTheDocument();
    });

    it('works with custom components', () => {
      const CustomInput = () => <div data-testid="custom-input">Custom Input</div>;

      render(
        <FormField label="Custom">
          <CustomInput />
        </FormField>
      );

      expect(screen.getByTestId('custom-input')).toBeInTheDocument();
    });
  });

  describe('error and help text message spacing', () => {
    it('error message has top margin', () => {
      render(
        <FormField label="Field" error="Error">
          <input type="text" />
        </FormField>
      );

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveClass('mt-1.5');
    });

    it('help text has top margin', () => {
      render(
        <FormField label="Field" helpText="Help">
          <input type="text" />
        </FormField>
      );

      const helpText = screen.getByText('Help');
      expect(helpText).toHaveClass('mt-1.5');
    });

    it('error message has small text size', () => {
      render(
        <FormField label="Field" error="Error">
          <input type="text" />
        </FormField>
      );

      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveClass('text-sm');
    });

    it('help text has small text size', () => {
      render(
        <FormField label="Field" helpText="Help">
          <input type="text" />
        </FormField>
      );

      const helpText = screen.getByText('Help');
      expect(helpText).toHaveClass('text-sm');
    });
  });

  describe('combined props', () => {
    it('renders with all props combined', () => {
      render(
        <FormField
          label="Email Address"
          required
          error="Please enter a valid email"
          helpText="We'll never share your email"
          className="my-custom-class"
          htmlFor="email-field"
        >
          <input type="email" id="email-field" />
        </FormField>
      );

      expect(screen.getByText('Email Address')).toBeInTheDocument();
      expect(screen.getByText('*')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveTextContent('Please enter a valid email');
      expect(screen.queryByText("We'll never share your email")).not.toBeInTheDocument();
    });

    it('renders required with help text when no error', () => {
      render(
        <FormField label="Password" required helpText="At least 8 characters">
          <input type="password" />
        </FormField>
      );

      expect(screen.getByText('Password')).toBeInTheDocument();
      expect(screen.getByText('*')).toBeInTheDocument();
      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
    });
  });
});
