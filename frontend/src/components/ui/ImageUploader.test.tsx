import { fireEvent, render, screen } from '@testing-library/react';

import { ERROR_MESSAGES, HELP_TEXTS, LABELS, PLACEHOLDERS } from '@/constants';
import type { PhotoData } from '@/types/reflection';
import { ImageUploader } from './ImageUploader';

const createFile = (name: string, size: number, type: string): File => {
  const file = new File(['x'.repeat(size)], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('ImageUploader', () => {
  const mockOnPhotosChange = vi.fn();
  const mockOnRemovePhoto = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock URL.createObjectURL and URL.revokeObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();
  });

  describe('rendering', () => {
    it('renders upload zone with instruction text', () => {
      render(<ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />);

      expect(screen.getByText(PLACEHOLDERS.UPLOAD_INSTRUCTION)).toBeInTheDocument();
    });

    it('renders help text about file format', () => {
      render(<ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />);

      expect(screen.getByText(HELP_TEXTS.UPLOAD_FORMAT)).toBeInTheDocument();
    });

    it('renders upload icon', () => {
      render(<ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />);

      expect(screen.getByRole('img', { name: 'アップロード' })).toBeInTheDocument();
    });

    it('has hidden file input', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
      expect(input).toHaveClass('hidden');
    });

    it('accepts multiple files', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]');
      expect(input).toHaveAttribute('multiple');
    });

    it('accepts only images', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]');
      expect(input).toHaveAttribute(
        'accept',
        '.jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp'
      );
    });
  });

  describe('drag and drop interaction', () => {
    it('updates styles on drag over', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      if (dropzone) {
        fireEvent.dragOver(dropzone);
        expect(dropzone).toHaveClass('border-primary-500', 'bg-primary-50');
      }
    });

    it('reverts styles on drag leave', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      if (dropzone) {
        fireEvent.dragOver(dropzone);
        fireEvent.dragLeave(dropzone);
        expect(dropzone).not.toHaveClass('border-primary-500', 'bg-primary-50');
      }
    });

    it('calls onPhotosChange when valid images are dropped', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      const file = createFile('test.png', 1024, 'image/png');

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnPhotosChange).toHaveBeenCalledWith([{ url: 'blob:mock-url', file }]);
      }
    });

    it('filters out non-image files', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      const pdfFile = createFile('doc.pdf', 1024, 'application/pdf');

      // Mock alert
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [pdfFile],
          },
        });

        expect(mockOnPhotosChange).not.toHaveBeenCalled();
        expect(alertSpy).toHaveBeenCalledWith(ERROR_MESSAGES.INVALID_FILE_TYPE);
      }

      alertSpy.mockRestore();
    });
  });

  describe('file selection via click', () => {
    it('triggers file input when dropzone is clicked', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = container.querySelector('button');
      if (dropzone) {
        fireEvent.click(dropzone);
        expect(clickSpy).toHaveBeenCalled();
      }
    });

    it('triggers file input on Enter key', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = container.querySelector('button');
      if (dropzone) {
        fireEvent.keyDown(dropzone, { key: 'Enter' });
        expect(clickSpy).toHaveBeenCalled();
      }
    });

    it('triggers file input on Space key', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = container.querySelector('button');
      if (dropzone) {
        fireEvent.keyDown(dropzone, { key: ' ' });
        expect(clickSpy).toHaveBeenCalled();
      }
    });

    it('calls onPhotosChange when files are selected', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const file = createFile('test.png', 1024, 'image/png');

      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });

      fireEvent.change(input);

      expect(mockOnPhotosChange).toHaveBeenCalledWith([{ url: 'blob:mock-url', file }]);
    });
  });

  describe('image preview', () => {
    it('displays preview images', () => {
      const photos: PhotoData[] = [
        { url: 'https://example.com/image1.jpg', id: '1' },
        { url: 'https://example.com/image2.jpg', id: '2' },
      ];
      render(<ImageUploader photos={photos} onPhotosChange={mockOnPhotosChange} />);

      // Query specifically for img tags (not emoji spans with role="img")
      const imageElements = screen.getAllByAltText(/Uploaded \d+/);
      expect(imageElements).toHaveLength(2);
      expect(imageElements[0]).toHaveAttribute('src', photos[0].url);
      expect(imageElements[1]).toHaveAttribute('src', photos[1].url);
    });

    it('displays remove button for each image when onRemovePhoto is provided', () => {
      const photos: PhotoData[] = [{ url: 'https://example.com/image1.jpg', id: '1' }];
      render(
        <ImageUploader
          photos={photos}
          onPhotosChange={mockOnPhotosChange}
          onRemovePhoto={mockOnRemovePhoto}
        />
      );

      const removeButton = screen.getByLabelText(LABELS.REMOVE_IMAGE);
      expect(removeButton).toBeInTheDocument();
    });

    it('does not display remove button when onRemovePhoto is not provided', () => {
      const photos: PhotoData[] = [{ url: 'https://example.com/image1.jpg', id: '1' }];
      render(<ImageUploader photos={photos} onPhotosChange={mockOnPhotosChange} />);

      const removeButton = screen.queryByLabelText(LABELS.REMOVE_IMAGE);
      expect(removeButton).not.toBeInTheDocument();
    });

    it('calls onRemovePhoto when remove button is clicked', () => {
      const photos: PhotoData[] = [
        { url: 'https://example.com/image1.jpg', id: '1' },
        { url: 'https://example.com/image2.jpg', id: '2' },
      ];
      render(
        <ImageUploader
          photos={photos}
          onPhotosChange={mockOnPhotosChange}
          onRemovePhoto={mockOnRemovePhoto}
        />
      );

      const removeButtons = screen.getAllByLabelText(LABELS.REMOVE_IMAGE);
      fireEvent.click(removeButtons[0]);

      expect(mockOnRemovePhoto).toHaveBeenCalledWith(0);
    });

    it('does not display preview area when no images', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const previewArea = container.querySelector('.grid');
      expect(previewArea).not.toBeInTheDocument();
    });
  });

  describe('validation', () => {
    it('shows alert when exceeding max images', () => {
      const photos: PhotoData[] = [
        { url: 'url1', id: '1' },
        { url: 'url2', id: '2' },
        { url: 'url3', id: '3' },
        { url: 'url4', id: '4' },
        { url: 'url5', id: '5' },
      ];
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      const { container } = render(
        <ImageUploader photos={photos} onPhotosChange={mockOnPhotosChange} maxImages={5} />
      );

      const dropzone = container.querySelector('button');
      const file = createFile('test.png', 1024, 'image/png');

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnPhotosChange).not.toHaveBeenCalled();
        expect(alertSpy).toHaveBeenCalledWith(ERROR_MESSAGES.MAX_IMAGES_EXCEEDED(5));
      }

      alertSpy.mockRestore();
    });

    it('shows alert when file size exceeds limit', () => {
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} maxSizeMB={5} />
      );

      const dropzone = container.querySelector('button');
      const file = createFile('large.png', 6 * 1024 * 1024, 'image/png'); // 6MB

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnPhotosChange).not.toHaveBeenCalled();
        expect(alertSpy).toHaveBeenCalledWith(ERROR_MESSAGES.FILE_SIZE_EXCEEDED('large.png', 5));
      }

      alertSpy.mockRestore();
    });

    it('accepts files within size limit', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} maxSizeMB={10} />
      );

      const dropzone = container.querySelector('button');
      const file = createFile('small.png', 5 * 1024 * 1024, 'image/png'); // 5MB

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnPhotosChange).toHaveBeenCalledWith([{ url: 'blob:mock-url', file }]);
      }
    });
  });

  describe('props', () => {
    it('uses default maxImages of 5', () => {
      const photos: PhotoData[] = [
        { url: 'url1', id: '1' },
        { url: 'url2', id: '2' },
        { url: 'url3', id: '3' },
        { url: 'url4', id: '4' },
        { url: 'url5', id: '5' },
      ];
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      const { container } = render(
        <ImageUploader photos={photos} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      const file = createFile('test.png', 1024, 'image/png');

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(alertSpy).toHaveBeenCalledWith(ERROR_MESSAGES.MAX_IMAGES_EXCEEDED(5));
      }

      alertSpy.mockRestore();
    });

    it('uses default maxSizeMB of 10', () => {
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      const file = createFile('large.png', 11 * 1024 * 1024, 'image/png'); // 11MB

      if (dropzone) {
        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(alertSpy).toHaveBeenCalledWith(ERROR_MESSAGES.FILE_SIZE_EXCEEDED('large.png', 10));
      }

      alertSpy.mockRestore();
    });
  });

  describe('memory management', () => {
    it('revokes object URL when removing image', () => {
      const blobUrl = 'blob:mock-blob-url';
      const photos: PhotoData[] = [{ url: blobUrl, id: '1' }];
      render(
        <ImageUploader
          photos={photos}
          onPhotosChange={mockOnPhotosChange}
          onRemovePhoto={mockOnRemovePhoto}
        />
      );

      const removeButton = screen.getByLabelText(LABELS.REMOVE_IMAGE);
      fireEvent.click(removeButton);

      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith(blobUrl);
      expect(mockOnRemovePhoto).toHaveBeenCalledWith(0);
    });

    it('does not revoke non-blob URLs', () => {
      const httpUrl = 'https://example.com/image.jpg';
      const photos: PhotoData[] = [{ url: httpUrl, id: '1' }];
      render(
        <ImageUploader
          photos={photos}
          onPhotosChange={mockOnPhotosChange}
          onRemovePhoto={mockOnRemovePhoto}
        />
      );

      const removeButton = screen.getByLabelText(LABELS.REMOVE_IMAGE);
      fireEvent.click(removeButton);

      expect(global.URL.revokeObjectURL).not.toHaveBeenCalled();
      expect(mockOnRemovePhoto).toHaveBeenCalledWith(0);
    });
  });

  describe('base styles', () => {
    it('has proper dropzone base styles', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      expect(dropzone).toHaveClass('w-full', 'border-2', 'border-dashed', 'rounded-lg');
    });

    it('has neutral colors by default', () => {
      const { container } = render(
        <ImageUploader photos={[]} onPhotosChange={mockOnPhotosChange} />
      );

      const dropzone = container.querySelector('button');
      expect(dropzone).toHaveClass('border-neutral-300', 'bg-neutral-50');
    });
  });
});
