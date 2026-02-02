import { fireEvent, render, screen } from '@testing-library/react';

import { BUTTON_LABELS } from '@/constants';
import { ErrorDialog } from './ErrorDialog';

describe('ErrorDialog', () => {
  const mockOnClose = vi.fn();
  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    title: 'エラー',
    message: 'エラーが発生しました。',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('does not render when isOpen is false', () => {
      render(<ErrorDialog {...defaultProps} isOpen={false} />);

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('renders when isOpen is true', () => {
      render(<ErrorDialog {...defaultProps} />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('renders title', () => {
      render(<ErrorDialog {...defaultProps} title="テストエラー" />);

      expect(screen.getByText('テストエラー')).toBeInTheDocument();
    });

    it('renders error message', () => {
      render(<ErrorDialog {...defaultProps} message="テストメッセージ" />);

      expect(screen.getByText('テストメッセージ')).toBeInTheDocument();
    });

    it('renders default button label', () => {
      render(<ErrorDialog {...defaultProps} />);

      expect(screen.getByText(BUTTON_LABELS.CLOSE)).toBeInTheDocument();
    });

    it('renders custom button label', () => {
      render(<ErrorDialog {...defaultProps} buttonLabel="了解" />);

      expect(screen.getByText('了解')).toBeInTheDocument();
    });
  });

  describe('close behavior', () => {
    it('calls onClose when button is clicked', () => {
      render(<ErrorDialog {...defaultProps} />);

      const button = screen.getByText(BUTTON_LABELS.CLOSE);
      fireEvent.click(button);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('calls onClose only once per click', () => {
      render(<ErrorDialog {...defaultProps} />);

      const button = screen.getByText(BUTTON_LABELS.CLOSE);
      fireEvent.click(button);
      fireEvent.click(button);

      expect(mockOnClose).toHaveBeenCalledTimes(2);
    });

    it('calls onClose with custom button', () => {
      render(<ErrorDialog {...defaultProps} buttonLabel="OK" />);

      const button = screen.getByText('OK');
      fireEvent.click(button);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('message display', () => {
    it('has correct text color for message', () => {
      render(<ErrorDialog {...defaultProps} />);

      const message = screen.getByText(defaultProps.message);
      expect(message).toHaveClass('text-neutral-600');
    });

    it('renders long error message', () => {
      const longMessage =
        'これは非常に長いエラーメッセージです。システムエラーが発生しました。もう一度お試しいただくか、問題が解決しない場合は管理者にお問い合わせください。';
      render(<ErrorDialog {...defaultProps} message={longMessage} />);

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('renders multiline error message', () => {
      const multilineMessage = '以下のエラーが発生しました:\n1. 接続エラー\n2. タイムアウト';
      render(<ErrorDialog {...defaultProps} message={multilineMessage} />);

      expect(screen.getByText(/以下のエラーが発生しました:/)).toBeInTheDocument();
    });

    it('renders message with special characters', () => {
      const specialMessage = '認証エラー！ログインし直してください。';
      render(<ErrorDialog {...defaultProps} message={specialMessage} />);

      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });
  });

  describe('modal size', () => {
    it('uses small size for modal', () => {
      render(<ErrorDialog {...defaultProps} />);

      const modalContent = document.body.querySelector('.max-w-sm');
      expect(modalContent).toBeInTheDocument();
    });
  });

  describe('layout structure', () => {
    it('has space-y-6 for content sections', () => {
      render(<ErrorDialog {...defaultProps} />);

      const contentContainer = document.body.querySelector('.space-y-6');
      expect(contentContainer).toBeInTheDocument();
    });

    it('has button aligned to the right', () => {
      render(<ErrorDialog {...defaultProps} />);

      const buttonContainer = document.body.querySelector('.flex.justify-end');
      expect(buttonContainer).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has role="dialog"', () => {
      render(<ErrorDialog {...defaultProps} />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('has aria-modal="true"', () => {
      render(<ErrorDialog {...defaultProps} />);

      expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
    });

    it('has aria-labelledby for title', () => {
      render(<ErrorDialog {...defaultProps} />);

      expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby', 'modal-title');
    });

    it('button is clickable and not disabled', () => {
      render(<ErrorDialog {...defaultProps} />);

      const button = screen.getByText(BUTTON_LABELS.CLOSE);
      expect(button).not.toBeDisabled();
    });
  });

  describe('button variant', () => {
    it('button uses primary variant', () => {
      render(<ErrorDialog {...defaultProps} />);

      const button = screen.getByText(BUTTON_LABELS.CLOSE);
      expect(button).toBeInTheDocument();
    });

    it('button has type button', () => {
      render(<ErrorDialog {...defaultProps} />);

      const button = screen.getByText(BUTTON_LABELS.CLOSE);
      expect(button).toHaveAttribute('type', 'button');
    });
  });

  describe('edge cases', () => {
    it('handles empty title', () => {
      render(<ErrorDialog {...defaultProps} title="" />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('handles empty message', () => {
      render(<ErrorDialog {...defaultProps} message="" />);

      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('handles very long title', () => {
      const longTitle = 'とても長いエラータイトルでシステムの表示を確認するためのテスト用文字列';
      render(<ErrorDialog {...defaultProps} title={longTitle} />);

      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('handles very long button label', () => {
      const longLabel = 'このダイアログを閉じる';
      render(<ErrorDialog {...defaultProps} buttonLabel={longLabel} />);

      expect(screen.getByText(longLabel)).toBeInTheDocument();
    });
  });

  describe('multiple state changes', () => {
    it('can be opened and closed multiple times', () => {
      const { rerender } = render(<ErrorDialog {...defaultProps} isOpen={false} />);
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

      rerender(<ErrorDialog {...defaultProps} isOpen={true} />);
      expect(screen.getByRole('dialog')).toBeInTheDocument();

      rerender(<ErrorDialog {...defaultProps} isOpen={false} />);
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

      rerender(<ErrorDialog {...defaultProps} isOpen={true} />);
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('updates message when props change', () => {
      const { rerender } = render(<ErrorDialog {...defaultProps} message="メッセージ1" />);
      expect(screen.getByText('メッセージ1')).toBeInTheDocument();

      rerender(<ErrorDialog {...defaultProps} message="メッセージ2" />);
      expect(screen.getByText('メッセージ2')).toBeInTheDocument();
    });
  });

  describe('integration with Modal component', () => {
    it('calls onClose when ESC key is pressed', () => {
      render(<ErrorDialog {...defaultProps} />);

      fireEvent.keyDown(document, { key: 'Escape' });

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('calls onClose when overlay is clicked', () => {
      render(<ErrorDialog {...defaultProps} />);

      fireEvent.click(screen.getByRole('dialog'));

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('does not call onClose when content is clicked', () => {
      render(<ErrorDialog {...defaultProps} />);

      const message = screen.getByText(defaultProps.message);
      fireEvent.click(message);

      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });
});
