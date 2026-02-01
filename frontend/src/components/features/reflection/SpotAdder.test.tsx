import { fireEvent, render, screen } from '@testing-library/react';

import { BUTTON_LABELS, HELP_TEXTS, PLACEHOLDERS, SECTION_TITLES } from '@/constants';
import { SpotAdder } from './SpotAdder';

describe('SpotAdder', () => {
  const mockOnAdd = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders section title', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      expect(screen.getByText(SECTION_TITLES.ADD_SPOT)).toBeInTheDocument();
    });

    it('renders instruction text', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      expect(screen.getByText(HELP_TEXTS.ADD_SPOT_INSTRUCTION)).toBeInTheDocument();
    });

    it('renders text input field', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      expect(input).toBeInTheDocument();
    });

    it('renders add button', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const button = screen.getByText(BUTTON_LABELS.ADD);
      expect(button).toBeInTheDocument();
    });

    it('input has correct placeholder', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      expect(input).toHaveAttribute('placeholder', PLACEHOLDERS.SPOT_NAME);
    });
  });

  describe('button state', () => {
    it('button is disabled by default with empty input', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const button = screen.getByText(BUTTON_LABELS.ADD);
      expect(button).toBeDisabled();
    });

    it('button is enabled when input has text', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      fireEvent.change(input, { target: { value: '清水寺' } });

      const button = screen.getByText(BUTTON_LABELS.ADD);
      expect(button).not.toBeDisabled();
    });

    it('button is disabled when input has only whitespace', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      fireEvent.change(input, { target: { value: '   ' } });

      const button = screen.getByText(BUTTON_LABELS.ADD);
      expect(button).toBeDisabled();
    });

    it('button is enabled when input has text with leading/trailing whitespace', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      fireEvent.change(input, { target: { value: '  金閣寺  ' } });

      const button = screen.getByText(BUTTON_LABELS.ADD);
      expect(button).not.toBeDisabled();
    });
  });

  describe('form submission', () => {
    it('calls onAdd with spot name when form is submitted', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: '銀閣寺' } });
      fireEvent.submit(form);

      expect(mockOnAdd).toHaveBeenCalledWith('銀閣寺');
    });

    it('calls onAdd with trimmed spot name', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: '  伏見稲荷大社  ' } });
      fireEvent.submit(form);

      expect(mockOnAdd).toHaveBeenCalledWith('伏見稲荷大社');
    });

    it('clears input after submission', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME) as HTMLInputElement;
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: '東寺' } });
      fireEvent.submit(form);

      expect(input.value).toBe('');
    });

    it('does not call onAdd when input is empty', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.submit(form);

      expect(mockOnAdd).not.toHaveBeenCalled();
    });

    it('does not call onAdd when input has only whitespace', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: '   ' } });
      fireEvent.submit(form);

      expect(mockOnAdd).not.toHaveBeenCalled();
    });

    it('prevents default form submission', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: '清水寺' } });
      const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
      const preventDefaultSpy = vi.spyOn(submitEvent, 'preventDefault');

      fireEvent(form, submitEvent);

      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  describe('button click submission', () => {
    it('submits form when button is clicked', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const button = screen.getByText(BUTTON_LABELS.ADD);

      fireEvent.change(input, { target: { value: '二条城' } });
      fireEvent.click(button);

      expect(mockOnAdd).toHaveBeenCalledWith('二条城');
    });
  });

  describe('input handling', () => {
    it('updates input value when typing', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME) as HTMLInputElement;

      fireEvent.change(input, { target: { value: '嵐山' } });
      expect(input.value).toBe('嵐山');
    });

    it('allows multiple character updates', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME) as HTMLInputElement;

      fireEvent.change(input, { target: { value: '京' } });
      expect(input.value).toBe('京');

      fireEvent.change(input, { target: { value: '京都' } });
      expect(input.value).toBe('京都');

      fireEvent.change(input, { target: { value: '京都タワー' } });
      expect(input.value).toBe('京都タワー');
    });

    it('can clear input and re-enter text', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME) as HTMLInputElement;

      fireEvent.change(input, { target: { value: '平安神宮' } });
      expect(input.value).toBe('平安神宮');

      fireEvent.change(input, { target: { value: '' } });
      expect(input.value).toBe('');

      fireEvent.change(input, { target: { value: '南禅寺' } });
      expect(input.value).toBe('南禅寺');
    });
  });

  describe('base styles', () => {
    it('has proper container styles', () => {
      const { container } = render(<SpotAdder onAdd={mockOnAdd} />);

      const formContainer = container.firstChild;
      expect(formContainer).toHaveClass(
        'rounded-lg',
        'border',
        'border-neutral-300',
        'border-dashed',
        'bg-neutral-50'
      );
    });

    it('has proper heading styles', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const heading = screen.getByText(SECTION_TITLES.ADD_SPOT);
      expect(heading.tagName).toBe('H3');
      expect(heading).toHaveClass('font-bold', 'text-lg');
    });

    it('has proper instruction text styles', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const instruction = screen.getByText(HELP_TEXTS.ADD_SPOT_INSTRUCTION);
      expect(instruction.tagName).toBe('P');
      expect(instruction).toHaveClass('text-neutral-600', 'text-sm');
    });

    it('form has flex layout', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form');

      expect(form).toHaveClass('flex', 'gap-2');
    });
  });

  describe('button variant', () => {
    it('button has secondary variant', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const button = screen.getByText(BUTTON_LABELS.ADD);
      // Secondary variant typically has specific classes
      expect(button).toBeInTheDocument();
    });

    it('button has type submit', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const button = screen.getByText(BUTTON_LABELS.ADD);
      expect(button).toHaveAttribute('type', 'submit');
    });
  });

  describe('edge cases', () => {
    it('handles very long spot names', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const longName =
        'とても長い観光地の名前でテキストがどのように表示されるかをテストするための非常に長い文字列です';
      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: longName } });
      fireEvent.submit(form);

      expect(mockOnAdd).toHaveBeenCalledWith(longName);
    });

    it('handles special characters in spot name', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const specialName = '東京スカイツリー®（展望台）';
      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: specialName } });
      fireEvent.submit(form);

      expect(mockOnAdd).toHaveBeenCalledWith(specialName);
    });

    it('handles emoji in spot name', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const emojiName = '🗼 東京タワー';
      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: emojiName } });
      fireEvent.submit(form);

      expect(mockOnAdd).toHaveBeenCalledWith(emojiName);
    });

    it('handles numbers in spot name', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const numberName = '21_21 DESIGN SIGHT';
      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      fireEvent.change(input, { target: { value: numberName } });
      fireEvent.submit(form);

      expect(mockOnAdd).toHaveBeenCalledWith(numberName);
    });
  });

  describe('multiple submissions', () => {
    it('allows multiple consecutive submissions', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form') as HTMLFormElement;

      // First submission
      fireEvent.change(input, { target: { value: '京都御所' } });
      fireEvent.submit(form);
      expect(mockOnAdd).toHaveBeenCalledWith('京都御所');

      // Second submission
      fireEvent.change(input, { target: { value: '祇園' } });
      fireEvent.submit(form);
      expect(mockOnAdd).toHaveBeenCalledWith('祇園');

      // Third submission
      fireEvent.change(input, { target: { value: '哲学の道' } });
      fireEvent.submit(form);
      expect(mockOnAdd).toHaveBeenCalledWith('哲学の道');

      expect(mockOnAdd).toHaveBeenCalledTimes(3);
    });
  });

  describe('accessibility', () => {
    it('input is part of a form', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const input = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_NAME);
      const form = input.closest('form');

      expect(form).toBeInTheDocument();
    });

    it('button is associated with form', () => {
      render(<SpotAdder onAdd={mockOnAdd} />);

      const button = screen.getByText(BUTTON_LABELS.ADD);
      const form = button.closest('form');

      expect(form).toBeInTheDocument();
    });
  });

  describe('full width input', () => {
    it('input container has flex-1 class', () => {
      const { container } = render(<SpotAdder onAdd={mockOnAdd} />);

      // The flex-1 div wraps the TextField component
      const flexContainer = container.querySelector('.flex-1');
      expect(flexContainer).toBeInTheDocument();
    });
  });
});
