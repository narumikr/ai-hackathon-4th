import { fireEvent, render, screen } from '@testing-library/react';

import { BUTTON_LABELS, FORM_LABELS, HELP_TEXTS, PLACEHOLDERS, STATUS_LABELS } from '@/constants';
import type { ReflectionSpot } from '@/types/reflection';
import { SpotReflectionForm } from './SpotReflectionForm';

describe('SpotReflectionForm', () => {
  const mockOnUpdate = vi.fn();
  const mockOnRemove = vi.fn();

  const createMockSpot = (overrides?: Partial<ReflectionSpot>): ReflectionSpot => ({
    id: 'spot-1',
    name: '浅草寺',
    photos: [],
    photoPreviews: [],
    comment: '',
    isAdded: false,
    ...overrides,
  });

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();
  });

  describe('rendering', () => {
    it('renders spot name', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(spot.name)).toBeInTheDocument();
    });

    it('renders photos label', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(FORM_LABELS.PHOTOS)).toBeInTheDocument();
    });

    it('renders comment label', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(FORM_LABELS.COMMENT)).toBeInTheDocument();
    });

    it('renders ImageUploader component', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      // ImageUploader has upload instruction text
      expect(screen.getByText(PLACEHOLDERS.UPLOAD_INSTRUCTION)).toBeInTheDocument();
    });

    it('renders TextArea component', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_COMMENT(spot.name));
      expect(textarea).toBeInTheDocument();
    });

    it('renders with existing comment', () => {
      const spot = createMockSpot({ comment: '素晴らしい体験でした' });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByDisplayValue(spot.comment);
      expect(textarea).toBeInTheDocument();
    });
  });

  describe('added spot indicator', () => {
    it('shows added spot badge when isAdded is true', () => {
      const spot = createMockSpot({ isAdded: true });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(STATUS_LABELS.ADDED_SPOT)).toBeInTheDocument();
    });

    it('shows help text for added spot', () => {
      const spot = createMockSpot({ isAdded: true });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(HELP_TEXTS.ADDED_SPOT)).toBeInTheDocument();
    });

    it('does not show badge when isAdded is false', () => {
      const spot = createMockSpot({ isAdded: false });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.queryByText(STATUS_LABELS.ADDED_SPOT)).not.toBeInTheDocument();
    });

    it('does not show help text when isAdded is false', () => {
      const spot = createMockSpot({ isAdded: false });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.queryByText(HELP_TEXTS.ADDED_SPOT)).not.toBeInTheDocument();
    });
  });

  describe('remove button', () => {
    it('renders remove button when isAdded is true and onRemove is provided', () => {
      const spot = createMockSpot({ isAdded: true });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} onRemove={mockOnRemove} />);

      expect(screen.getByText(BUTTON_LABELS.REMOVE)).toBeInTheDocument();
    });

    it('does not render remove button when isAdded is false', () => {
      const spot = createMockSpot({ isAdded: false });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} onRemove={mockOnRemove} />);

      expect(screen.queryByText(BUTTON_LABELS.REMOVE)).not.toBeInTheDocument();
    });

    it('does not render remove button when onRemove is not provided', () => {
      const spot = createMockSpot({ isAdded: true });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.queryByText(BUTTON_LABELS.REMOVE)).not.toBeInTheDocument();
    });

    it('calls onRemove with spot id when clicked', () => {
      const spot = createMockSpot({ isAdded: true, id: 'test-spot-id' });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} onRemove={mockOnRemove} />);

      const removeButton = screen.getByText(BUTTON_LABELS.REMOVE);
      fireEvent.click(removeButton);

      expect(mockOnRemove).toHaveBeenCalledWith('test-spot-id');
    });
  });

  describe('image upload handling', () => {
    it('calls onUpdate with new images when images are added', () => {
      const spot = createMockSpot();
      const { container } = render(
        <SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />
      );

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const file = new File(['content'], 'test.png', { type: 'image/png' });

      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });

      fireEvent.change(input);

      expect(mockOnUpdate).toHaveBeenCalledWith(spot.id, {
        photos: [file],
        photoPreviews: ['blob:mock-url'],
      });
    });

    it('appends new images to existing ones', () => {
      const existingFile = new File(['existing'], 'existing.png', { type: 'image/png' });
      const spot = createMockSpot({
        photos: [existingFile],
        photoPreviews: ['blob:existing-url'],
      });

      const { container } = render(
        <SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />
      );

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const newFile = new File(['new'], 'new.png', { type: 'image/png' });

      Object.defineProperty(input, 'files', {
        value: [newFile],
        writable: false,
      });

      fireEvent.change(input);

      expect(mockOnUpdate).toHaveBeenCalledWith(spot.id, {
        photos: [existingFile, newFile],
        photoPreviews: ['blob:existing-url', 'blob:mock-url'],
      });
    });

    it('displays image previews', () => {
      const spot = createMockSpot({
        photoPreviews: ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
      });

      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      // Query specifically for img tags (not emoji spans with role="img")
      const images = screen.getAllByAltText(/Uploaded \d+/);
      expect(images).toHaveLength(2);
    });
  });

  describe('comment handling', () => {
    it('calls onUpdate when comment changes', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_COMMENT(spot.name));
      fireEvent.change(textarea, { target: { value: '新しいコメント' } });

      expect(mockOnUpdate).toHaveBeenCalledWith(spot.id, { comment: '新しいコメント' });
    });

    it('updates comment value in real-time', () => {
      const spot = createMockSpot({ comment: '初期コメント' });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByDisplayValue('初期コメント') as HTMLTextAreaElement;
      expect(textarea.value).toBe('初期コメント');
    });

    it('has proper placeholder text', () => {
      const spot = createMockSpot({ name: '金閣寺' });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByPlaceholderText(PLACEHOLDERS.SPOT_COMMENT('金閣寺'));
      expect(textarea).toBeInTheDocument();
    });

    it('TextArea has correct rows', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const textarea = screen.getByPlaceholderText(
        PLACEHOLDERS.SPOT_COMMENT(spot.name)
      ) as HTMLTextAreaElement;
      expect(textarea.rows).toBe(3);
    });
  });

  describe('base styles', () => {
    it('has proper container styles', () => {
      const spot = createMockSpot();
      const { container } = render(
        <SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />
      );

      const formContainer = container.firstChild;
      expect(formContainer).toHaveClass('rounded-lg', 'border', 'border-neutral-200', 'bg-white');
    });

    it('has proper heading styles', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const heading = screen.getByText(spot.name);
      expect(heading.tagName).toBe('H3');
      expect(heading).toHaveClass('font-bold', 'text-lg');
    });
  });

  describe('multiple spots with different states', () => {
    it('handles regular spot correctly', () => {
      const spot = createMockSpot({ isAdded: false });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(spot.name)).toBeInTheDocument();
      expect(screen.queryByText(STATUS_LABELS.ADDED_SPOT)).not.toBeInTheDocument();
      expect(screen.queryByText(BUTTON_LABELS.REMOVE)).not.toBeInTheDocument();
    });

    it('handles added spot correctly', () => {
      const spot = createMockSpot({ isAdded: true });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} onRemove={mockOnRemove} />);

      expect(screen.getByText(spot.name)).toBeInTheDocument();
      expect(screen.getByText(STATUS_LABELS.ADDED_SPOT)).toBeInTheDocument();
      expect(screen.getByText(BUTTON_LABELS.REMOVE)).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has proper label for photos section', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const label = screen.getByText(FORM_LABELS.PHOTOS);
      expect(label).toHaveClass('font-semibold');
    });

    it('has proper label for comment section', () => {
      const spot = createMockSpot();
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const label = screen.getByText(FORM_LABELS.COMMENT);
      expect(label).toHaveClass('font-semibold');
    });

    it('remove button has proper styling for visibility', () => {
      const spot = createMockSpot({ isAdded: true });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} onRemove={mockOnRemove} />);

      const removeButton = screen.getByText(BUTTON_LABELS.REMOVE);
      expect(removeButton).toHaveClass('text-danger', 'hover:underline');
    });
  });

  describe('edge cases', () => {
    it('handles empty spot name', () => {
      const spot = createMockSpot({ name: '' });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      const heading = screen.getByRole('heading', { level: 3 });
      expect(heading).toHaveTextContent('');
    });

    it('handles long spot name', () => {
      const longName = 'とても長い観光地の名前でテキストの折り返しをテストします';
      const spot = createMockSpot({ name: longName });
      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      expect(screen.getByText(longName)).toBeInTheDocument();
    });

    it('handles multiple image previews', () => {
      const spot = createMockSpot({
        photoPreviews: ['url1', 'url2', 'url3', 'url4', 'url5'],
      });

      render(<SpotReflectionForm spot={spot} onUpdate={mockOnUpdate} />);

      // Query specifically for img tags (not emoji spans with role="img")
      const images = screen.getAllByAltText(/Uploaded \d+/);
      expect(images).toHaveLength(5);
    });
  });
});
