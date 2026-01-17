import { fireEvent, render, screen } from '@testing-library/react';

import { FileUploader } from './FileUploader';

const createFile = (name: string, size: number, type: string): File => {
  const file = new File(['x'.repeat(size)], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('FileUploader', () => {
  const mockOnUpload = vi.fn();
  const mockOnError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders with default label', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      expect(screen.getByText('ファイルをドラッグ&ドロップ')).toBeInTheDocument();
    });

    it('renders with custom label', () => {
      render(<FileUploader onUpload={mockOnUpload} label="画像をアップロード" />);

      expect(screen.getByText('画像をアップロード')).toBeInTheDocument();
    });

    it('renders click instruction', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      expect(screen.getByText('またはクリックしてファイルを選択')).toBeInTheDocument();
    });

    it('renders upload icon', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('renders as a button role element', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('has hidden file input', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
      expect(input).toHaveClass('sr-only');
    });
  });

  describe('accept prop', () => {
    it('shows accepted file types hint', () => {
      render(<FileUploader onUpload={mockOnUpload} accept="image/*" />);

      expect(screen.getByText(/対応形式: image\/\*/)).toBeInTheDocument();
    });

    it('passes accept to file input', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} accept=".pdf,.doc" />);

      const input = container.querySelector('input[type="file"]');
      expect(input).toHaveAttribute('accept', '.pdf,.doc');
    });
  });

  describe('maxSize prop', () => {
    it('shows max size hint in bytes', () => {
      render(<FileUploader onUpload={mockOnUpload} maxSize={1024} />);

      expect(screen.getByText(/最大サイズ: 1 KB/)).toBeInTheDocument();
    });

    it('shows max size hint in MB', () => {
      render(<FileUploader onUpload={mockOnUpload} maxSize={5 * 1024 * 1024} />);

      expect(screen.getByText(/最大サイズ: 5 MB/)).toBeInTheDocument();
    });
  });

  describe('multiple prop', () => {
    it('allows single file by default', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]');
      expect(input).not.toHaveAttribute('multiple');
    });

    it('allows multiple files when multiple is true', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} multiple />);

      const input = container.querySelector('input[type="file"]');
      expect(input).toHaveAttribute('multiple');
    });
  });

  describe('helpText prop', () => {
    it('renders help text when provided', () => {
      render(<FileUploader onUpload={mockOnUpload} helpText="最大5ファイルまでアップロード可能" />);

      expect(screen.getByText('最大5ファイルまでアップロード可能')).toBeInTheDocument();
    });
  });

  describe('disabled state', () => {
    it('is not disabled by default', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).not.toHaveAttribute('aria-disabled', 'true');
    });

    it('is disabled when disabled prop is true', () => {
      render(<FileUploader onUpload={mockOnUpload} disabled />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveAttribute('aria-disabled', 'true');
    });

    it('has tabIndex -1 when disabled', () => {
      render(<FileUploader onUpload={mockOnUpload} disabled />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveAttribute('tabindex', '-1');
    });

    it('has tabIndex 0 when not disabled', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveAttribute('tabindex', '0');
    });

    it('applies disabled styles', () => {
      render(<FileUploader onUpload={mockOnUpload} disabled />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('cursor-not-allowed', 'opacity-50');
    });
  });

  describe('className prop', () => {
    it('applies additional className', () => {
      const { container } = render(
        <FileUploader onUpload={mockOnUpload} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('file selection via click', () => {
    it('triggers file input click when dropzone is clicked', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = screen.getByRole('button');
      fireEvent.click(dropzone);

      expect(clickSpy).toHaveBeenCalled();
    });

    it('does not trigger file input click when disabled', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} disabled />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = screen.getByRole('button');
      fireEvent.click(dropzone);

      expect(clickSpy).not.toHaveBeenCalled();
    });

    it('calls onUpload when file is selected', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const file = createFile('test.png', 1024, 'image/png');

      Object.defineProperty(input, 'files', {
        value: [file],
      });

      fireEvent.change(input);

      expect(mockOnUpload).toHaveBeenCalledWith([file]);
    });
  });

  describe('keyboard interaction', () => {
    it('triggers file input on Enter key', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = screen.getByRole('button');
      fireEvent.keyDown(dropzone, { key: 'Enter' });

      expect(clickSpy).toHaveBeenCalled();
    });

    it('triggers file input on Space key', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = screen.getByRole('button');
      fireEvent.keyDown(dropzone, { key: ' ' });

      expect(clickSpy).toHaveBeenCalled();
    });

    it('does not trigger on other keys', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = screen.getByRole('button');
      fireEvent.keyDown(dropzone, { key: 'Tab' });

      expect(clickSpy).not.toHaveBeenCalled();
    });

    it('does not trigger when disabled', () => {
      const { container } = render(<FileUploader onUpload={mockOnUpload} disabled />);

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      const clickSpy = vi.spyOn(input, 'click');

      const dropzone = screen.getByRole('button');
      fireEvent.keyDown(dropzone, { key: 'Enter' });

      expect(clickSpy).not.toHaveBeenCalled();
    });
  });

  describe('drag and drop', () => {
    it('updates styles on drag over', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      fireEvent.dragOver(dropzone);

      expect(dropzone).toHaveClass('border-primary-500', 'bg-primary-100');
    });

    it('reverts styles on drag leave', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      fireEvent.dragOver(dropzone);
      fireEvent.dragLeave(dropzone);

      expect(dropzone).not.toHaveClass('border-primary-500', 'bg-primary-100');
    });

    it('calls onUpload when file is dropped', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      const file = createFile('test.png', 1024, 'image/png');

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(mockOnUpload).toHaveBeenCalledWith([file]);
    });

    it('does not accept drop when disabled', () => {
      render(<FileUploader onUpload={mockOnUpload} disabled />);

      const dropzone = screen.getByRole('button');
      const file = createFile('test.png', 1024, 'image/png');

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(mockOnUpload).not.toHaveBeenCalled();
    });

    it('does not update styles on drag over when disabled', () => {
      render(<FileUploader onUpload={mockOnUpload} disabled />);

      const dropzone = screen.getByRole('button');
      fireEvent.dragOver(dropzone);

      expect(dropzone).not.toHaveClass('border-primary-500', 'bg-primary-100');
    });
  });

  describe('file validation', () => {
    describe('file size validation', () => {
      it('rejects files larger than maxSize', () => {
        render(
          <FileUploader onUpload={mockOnUpload} onError={mockOnError} maxSize={1024} />
        );

        const dropzone = screen.getByRole('button');
        const file = createFile('large.png', 2048, 'image/png');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnUpload).not.toHaveBeenCalled();
        expect(mockOnError).toHaveBeenCalled();
      });

      it('accepts files within maxSize', () => {
        render(
          <FileUploader onUpload={mockOnUpload} onError={mockOnError} maxSize={2048} />
        );

        const dropzone = screen.getByRole('button');
        const file = createFile('small.png', 1024, 'image/png');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnUpload).toHaveBeenCalledWith([file]);
        expect(mockOnError).not.toHaveBeenCalled();
      });

      it('shows error message for oversized files', () => {
        render(<FileUploader onUpload={mockOnUpload} maxSize={1024} />);

        const dropzone = screen.getByRole('button');
        const file = createFile('large.png', 2048, 'image/png');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(screen.getByRole('alert')).toBeInTheDocument();
        expect(screen.getByText(/ファイルサイズ上限/)).toBeInTheDocument();
      });
    });

    describe('file type validation', () => {
      it('rejects files with wrong extension', () => {
        render(
          <FileUploader onUpload={mockOnUpload} onError={mockOnError} accept=".png,.jpg" />
        );

        const dropzone = screen.getByRole('button');
        const file = createFile('document.pdf', 1024, 'application/pdf');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnUpload).not.toHaveBeenCalled();
        expect(mockOnError).toHaveBeenCalled();
      });

      it('accepts files with correct extension', () => {
        render(<FileUploader onUpload={mockOnUpload} onError={mockOnError} accept=".png" />);

        const dropzone = screen.getByRole('button');
        const file = createFile('image.png', 1024, 'image/png');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnUpload).toHaveBeenCalledWith([file]);
      });

      it('accepts files matching wildcard MIME type', () => {
        render(<FileUploader onUpload={mockOnUpload} onError={mockOnError} accept="image/*" />);

        const dropzone = screen.getByRole('button');
        const file = createFile('photo.jpg', 1024, 'image/jpeg');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnUpload).toHaveBeenCalledWith([file]);
      });

      it('rejects files not matching wildcard MIME type', () => {
        render(
          <FileUploader onUpload={mockOnUpload} onError={mockOnError} accept="image/*" />
        );

        const dropzone = screen.getByRole('button');
        const file = createFile('document.pdf', 1024, 'application/pdf');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(mockOnUpload).not.toHaveBeenCalled();
      });

      it('shows error message for invalid file type', () => {
        render(<FileUploader onUpload={mockOnUpload} accept="image/*" />);

        const dropzone = screen.getByRole('button');
        const file = createFile('document.pdf', 1024, 'application/pdf');

        fireEvent.drop(dropzone, {
          dataTransfer: {
            files: [file],
          },
        });

        expect(screen.getByRole('alert')).toBeInTheDocument();
        expect(screen.getByText(/許可されていないファイル形式/)).toBeInTheDocument();
      });
    });
  });

  describe('multiple file handling', () => {
    it('only uploads first file when multiple is false', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      const file1 = createFile('file1.png', 1024, 'image/png');
      const file2 = createFile('file2.png', 1024, 'image/png');

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file1, file2],
        },
      });

      expect(mockOnUpload).toHaveBeenCalledWith([file1]);
    });

    it('uploads all files when multiple is true', () => {
      render(<FileUploader onUpload={mockOnUpload} multiple />);

      const dropzone = screen.getByRole('button');
      const file1 = createFile('file1.png', 1024, 'image/png');
      const file2 = createFile('file2.png', 1024, 'image/png');

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file1, file2],
        },
      });

      expect(mockOnUpload).toHaveBeenCalledWith([file1, file2]);
    });
  });

  describe('error display', () => {
    it('clears error when new valid file is uploaded', () => {
      render(<FileUploader onUpload={mockOnUpload} maxSize={1024} />);

      const dropzone = screen.getByRole('button');

      // First, upload an oversized file
      const largeFile = createFile('large.png', 2048, 'image/png');
      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [largeFile],
        },
      });

      expect(screen.getByRole('alert')).toBeInTheDocument();

      // Then, upload a valid file
      const smallFile = createFile('small.png', 512, 'image/png');
      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [smallFile],
        },
      });

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('applies error styles when error exists', () => {
      render(<FileUploader onUpload={mockOnUpload} maxSize={1024} />);

      const dropzone = screen.getByRole('button');
      const file = createFile('large.png', 2048, 'image/png');

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(dropzone).toHaveClass('border-red-400', 'bg-red-50');
    });

    it('hides help text when error is shown', () => {
      render(
        <FileUploader
          onUpload={mockOnUpload}
          maxSize={1024}
          helpText="Upload your files here"
        />
      );

      const dropzone = screen.getByRole('button');
      const file = createFile('large.png', 2048, 'image/png');

      expect(screen.getByText('Upload your files here')).toBeInTheDocument();

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(screen.queryByText('Upload your files here')).not.toBeInTheDocument();
    });
  });

  describe('base styles', () => {
    it('has full width', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('w-full');
    });

    it('has dashed border', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('border-dashed', 'border-2');
    });

    it('has rounded corners', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('rounded-lg');
    });

    it('has transition styles', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('transition-all', 'duration-200');
    });

    it('has cursor pointer', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('cursor-pointer');
    });
  });

  describe('normal state styles', () => {
    it('has neutral border and background by default', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('border-neutral-300', 'bg-neutral-50');
    });

    it('has hover styles for primary color', () => {
      render(<FileUploader onUpload={mockOnUpload} />);

      const dropzone = screen.getByRole('button');
      expect(dropzone).toHaveClass('hover:border-primary-400', 'hover:bg-primary-50');
    });
  });

  describe('accessibility', () => {
    it('has aria-describedby pointing to error when error exists', () => {
      render(<FileUploader onUpload={mockOnUpload} maxSize={1024} />);

      const dropzone = screen.getByRole('button');
      const file = createFile('large.png', 2048, 'image/png');

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      expect(dropzone.getAttribute('aria-describedby')).toContain('-error');
    });

    it('has aria-describedby pointing to help text when no error', () => {
      render(<FileUploader onUpload={mockOnUpload} helpText="Help text" />);

      const dropzone = screen.getByRole('button');
      expect(dropzone.getAttribute('aria-describedby')).toContain('-help');
    });

    it('file input has aria-label', () => {
      const { container } = render(
        <FileUploader onUpload={mockOnUpload} label="Upload images" />
      );

      const input = container.querySelector('input[type="file"]');
      expect(input).toHaveAttribute('aria-label', 'Upload images');
    });
  });
});
