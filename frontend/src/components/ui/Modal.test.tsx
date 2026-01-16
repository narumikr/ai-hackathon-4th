import { fireEvent, render, screen } from '@testing-library/react';

import { Modal } from './Modal';

describe('Modal', () => {
  describe('rendering', () => {
    it('does not render when isOpen is false', () => {
      render(
        <Modal isOpen={false} onClose={vi.fn()}>
          Modal content
        </Modal>
      );

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('renders when isOpen is true', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Modal content
        </Modal>
      );

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('renders children content', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          <p>Test content</p>
        </Modal>
      );

      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('renders title when provided', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test Title">
          Content
        </Modal>
      );

      expect(screen.getByText('Test Title')).toBeInTheDocument();
    });

    it('does not render title section when title is not provided', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    });

    it('renders close button when title is provided', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test">
          Content
        </Modal>
      );

      expect(screen.getByLabelText('閉じる')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has role="dialog"', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('has aria-modal="true"', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
    });

    it('has aria-labelledby when title is provided', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test Title">
          Content
        </Modal>
      );

      expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby', 'modal-title');
    });

    it('does not have aria-labelledby when title is not provided', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      expect(screen.getByRole('dialog')).not.toHaveAttribute('aria-labelledby');
    });
  });

  describe('close behavior', () => {
    it('calls onClose when close button is clicked', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose} title="Test">
          Content
        </Modal>
      );

      fireEvent.click(screen.getByLabelText('閉じる'));

      expect(handleClose).toHaveBeenCalledTimes(1);
    });

    it('calls onClose when overlay is clicked', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose}>
          Content
        </Modal>
      );

      fireEvent.click(screen.getByRole('dialog'));

      expect(handleClose).toHaveBeenCalledTimes(1);
    });

    it('does not call onClose when content is clicked', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose}>
          <div data-testid="content">Content</div>
        </Modal>
      );

      fireEvent.click(screen.getByTestId('content'));

      expect(handleClose).not.toHaveBeenCalled();
    });

    it('does not close on overlay click when closeOnOverlayClick is false', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose} closeOnOverlayClick={false}>
          Content
        </Modal>
      );

      fireEvent.click(screen.getByRole('dialog'));

      expect(handleClose).not.toHaveBeenCalled();
    });

    it('calls onClose when ESC key is pressed', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose}>
          Content
        </Modal>
      );

      fireEvent.keyDown(document, { key: 'Escape' });

      expect(handleClose).toHaveBeenCalledTimes(1);
    });

    it('does not close on ESC when closeOnEsc is false', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose} closeOnEsc={false}>
          Content
        </Modal>
      );

      fireEvent.keyDown(document, { key: 'Escape' });

      expect(handleClose).not.toHaveBeenCalled();
    });
  });

  describe('sizes', () => {
    it('applies sm size class', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} size="sm">
          Content
        </Modal>
      );

      const modalContent = document.body.querySelector('.max-w-sm');
      expect(modalContent).toBeInTheDocument();
    });

    it('applies md size class by default', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const modalContent = document.body.querySelector('.max-w-md');
      expect(modalContent).toBeInTheDocument();
    });

    it('applies lg size class', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} size="lg">
          Content
        </Modal>
      );

      const modalContent = document.body.querySelector('.max-w-lg');
      expect(modalContent).toBeInTheDocument();
    });

    it('applies xl size class', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} size="xl">
          Content
        </Modal>
      );

      const modalContent = document.body.querySelector('.max-w-xl');
      expect(modalContent).toBeInTheDocument();
    });
  });

  describe('className prop', () => {
    it('applies additional className to modal content', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} className="custom-class">
          Content
        </Modal>
      );

      const modalContent = document.body.querySelector('.custom-class');
      expect(modalContent).toBeInTheDocument();
    });
  });

  describe('body scroll lock', () => {
    it('locks body scroll when opened', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('unlocks body scroll when closed', () => {
      const { unmount } = render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      unmount();

      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('base styles', () => {
    it('has overlay with fixed positioning', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const overlay = screen.getByRole('dialog');
      expect(overlay).toHaveClass('fixed', 'inset-0');
    });

    it('has overlay with z-index', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const overlay = screen.getByRole('dialog');
      expect(overlay).toHaveClass('z-50');
    });

    it('has overlay with flex centering', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const overlay = screen.getByRole('dialog');
      expect(overlay).toHaveClass('flex', 'items-center', 'justify-center');
    });

    it('has overlay with backdrop', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const overlay = screen.getByRole('dialog');
      expect(overlay).toHaveClass('bg-black/50');
    });
  });

  describe('content styles', () => {
    it('has white background', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const content = document.body.querySelector('.bg-white');
      expect(content).toBeInTheDocument();
    });

    it('has rounded corners', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const content = document.body.querySelector('.rounded-lg');
      expect(content).toBeInTheDocument();
    });

    it('has shadow', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()}>
          Content
        </Modal>
      );

      const content = document.body.querySelector('.shadow-lg');
      expect(content).toBeInTheDocument();
    });
  });

  describe('header styles', () => {
    it('has border bottom on header', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test">
          Content
        </Modal>
      );

      const header = document.body.querySelector('.border-b');
      expect(header).toBeInTheDocument();
    });

    it('has proper padding on header', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test">
          Content
        </Modal>
      );

      const header = document.body.querySelector('.px-6.py-4');
      expect(header).toBeInTheDocument();
    });
  });

  describe('title styles', () => {
    it('has proper typography for title', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test Title">
          Content
        </Modal>
      );

      const title = screen.getByRole('heading', { name: 'Test Title' });
      expect(title).toHaveClass('text-lg', 'font-semibold');
    });

    it('has correct id for accessibility', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test Title">
          Content
        </Modal>
      );

      const title = screen.getByRole('heading', { name: 'Test Title' });
      expect(title).toHaveAttribute('id', 'modal-title');
    });
  });

  describe('close button styles', () => {
    it('has focus ring styles', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test">
          Content
        </Modal>
      );

      const closeButton = screen.getByLabelText('閉じる');
      expect(closeButton).toHaveClass('focus:ring-2', 'focus:ring-primary-300');
    });

    it('has hover styles', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test">
          Content
        </Modal>
      );

      const closeButton = screen.getByLabelText('閉じる');
      expect(closeButton).toHaveClass('hover:bg-neutral-100');
    });
  });
});
