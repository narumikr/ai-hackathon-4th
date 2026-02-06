import { act, fireEvent, render, screen } from '@testing-library/react';

import { InactivityPrompt } from './InactivityPrompt';

describe('InactivityPrompt', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    sessionStorage.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
    sessionStorage.clear();
  });

  describe('rendering', () => {
    it('does not show prompt by default', () => {
      render(<InactivityPrompt />);

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });

    it('shows prompt after inactivity delay', async () => {
      render(<InactivityPrompt />);

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      await act(async () => {
        vi.advanceTimersByTime(50);
      });

      expect(screen.getByTestId('inactivity-prompt')).toBeInTheDocument();
    });

    it('shows prompt after custom inactivity delay', async () => {
      render(<InactivityPrompt inactivityDelay={3000} />);

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(3000);
      });

      await act(async () => {
        vi.advanceTimersByTime(50);
      });

      expect(screen.getByTestId('inactivity-prompt')).toBeInTheDocument();
    });

    it('displays correct message text', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.getByText('旅行計画を立ててみよう')).toBeInTheDocument();
    });
  });

  describe('user interactions', () => {
    it('hides prompt when close button is clicked', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.getByTestId('inactivity-prompt')).toBeInTheDocument();

      const closeButton = screen.getByLabelText('閉じる');
      fireEvent.click(closeButton);

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });

    it('hides prompt when link is clicked', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.getByTestId('inactivity-prompt')).toBeInTheDocument();

      const link = screen.getByText('旅行計画を立ててみよう');
      fireEvent.click(link);

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });

    it('saves dismissed state to sessionStorage when closed', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      const closeButton = screen.getByLabelText('閉じる');
      fireEvent.click(closeButton);

      expect(sessionStorage.getItem('inactivity-prompt-dismissed')).toBe('true');
    });

    it('does not show prompt again after being dismissed', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      const closeButton = screen.getByLabelText('閉じる');
      fireEvent.click(closeButton);

      // Wait for another delay period
      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });
  });

  describe('timer reset', () => {
    it('resets timer on mousedown event', async () => {
      render(<InactivityPrompt />);

      // Advance timer partially
      await act(async () => {
        vi.advanceTimersByTime(4000);
      });

      // Trigger mousedown event
      fireEvent.mouseDown(document);

      // Advance timer again
      await act(async () => {
        vi.advanceTimersByTime(4000);
      });

      // Should not be visible yet (timer was reset)
      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();

      // Complete the delay after reset
      await act(async () => {
        vi.advanceTimersByTime(1050);
      });

      // Now it should be visible
      expect(screen.getByTestId('inactivity-prompt')).toBeInTheDocument();
    });

    it('resets timer on keydown event', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(4000);
      });

      fireEvent.keyDown(document);

      await act(async () => {
        vi.advanceTimersByTime(4000);
      });

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });

    it('resets timer on touchstart event', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(4000);
      });

      fireEvent.touchStart(document);

      await act(async () => {
        vi.advanceTimersByTime(4000);
      });

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });
  });

  describe('sessionStorage integration', () => {
    it('does not show prompt if already dismissed in sessionStorage', async () => {
      sessionStorage.setItem('inactivity-prompt-dismissed', 'true');

      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();
    });

    it('shows prompt if sessionStorage is cleared', async () => {
      sessionStorage.setItem('inactivity-prompt-dismissed', 'true');

      const { unmount } = render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.queryByTestId('inactivity-prompt')).not.toBeInTheDocument();

      unmount();
      sessionStorage.clear();

      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      expect(screen.getByTestId('inactivity-prompt')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has role="status" attribute', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      const prompt = screen.getByTestId('inactivity-prompt');
      expect(prompt).toHaveAttribute('role', 'status');
    });

    it('has aria-live="polite" attribute', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      const prompt = screen.getByTestId('inactivity-prompt');
      expect(prompt).toHaveAttribute('aria-live', 'polite');
    });

    it('close button has aria-label', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      const closeButton = screen.getByLabelText('閉じる');
      expect(closeButton).toBeInTheDocument();
    });

    it('link points to correct href', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5050);
      });

      const link = screen.getByText('旅行計画を立ててみよう');
      expect(link).toHaveAttribute('href', '/travel/new');
    });
  });

  describe('animation', () => {
    it('applies fade-in class after delay', async () => {
      render(<InactivityPrompt />);

      await act(async () => {
        vi.advanceTimersByTime(5000);
      });

      const prompt = screen.getByTestId('inactivity-prompt');
      expect(prompt).toHaveClass('opacity-0');

      await act(async () => {
        vi.advanceTimersByTime(50);
      });

      expect(prompt).toHaveClass('opacity-100');
    });
  });
});
