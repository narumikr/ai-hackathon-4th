import { act, fireEvent, render, screen } from '@testing-library/react';

import { Tooltip } from './Tooltip';

describe('Tooltip', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const getContainer = () => screen.getByTestId('tooltip-container');

  describe('rendering', () => {
    it('renders children correctly', () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      expect(screen.getByRole('button', { name: 'Hover me' })).toBeInTheDocument();
    });

    it('does not show tooltip by default', () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });
  });

  describe('visibility', () => {
    it('shows tooltip on mouse enter after delay', async () => {
      render(
        <Tooltip content="Tooltip text" delay={200}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByRole('tooltip')).toBeInTheDocument();
      expect(screen.getByText('Tooltip text')).toBeInTheDocument();
    });

    it('hides tooltip on mouse leave', async () => {
      render(
        <Tooltip content="Tooltip text" delay={200}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByRole('tooltip')).toBeInTheDocument();

      fireEvent.mouseLeave(container);

      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });

    it('cancels showing tooltip if mouse leaves before delay', async () => {
      render(
        <Tooltip content="Tooltip text" delay={500}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      fireEvent.mouseLeave(container);

      await act(async () => {
        vi.advanceTimersByTime(300);
      });

      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });

    it('shows tooltip on focus', async () => {
      render(
        <Tooltip content="Tooltip text" delay={200}>
          <button type="button">Focus me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.focus(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });

    it('hides tooltip on blur', async () => {
      render(
        <Tooltip content="Tooltip text" delay={200}>
          <button type="button">Focus me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.focus(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByRole('tooltip')).toBeInTheDocument();

      fireEvent.blur(container);

      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });
  });

  describe('delay prop', () => {
    it('uses default delay of 200ms', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(199);
      });
      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(1);
      });
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });

    it('respects custom delay', async () => {
      render(
        <Tooltip content="Tooltip text" delay={500}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(499);
      });
      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();

      await act(async () => {
        vi.advanceTimersByTime(1);
      });
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });

    it('shows tooltip immediately when delay is 0', async () => {
      render(
        <Tooltip content="Tooltip text" delay={0}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(0);
      });

      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });
  });

  describe('position prop', () => {
    it('applies top position styles by default', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('bottom-full');
      expect(tooltip).toHaveClass('mb-2');
    });

    it('applies top position styles when specified', async () => {
      render(
        <Tooltip content="Tooltip text" position="top">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('bottom-full', 'mb-2');
    });

    it('applies bottom position styles when specified', async () => {
      render(
        <Tooltip content="Tooltip text" position="bottom">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('top-full', 'mt-2');
    });

    it('applies left position styles when specified', async () => {
      render(
        <Tooltip content="Tooltip text" position="left">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('right-full', 'mr-2');
    });

    it('applies right position styles when specified', async () => {
      render(
        <Tooltip content="Tooltip text" position="right">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('left-full', 'ml-2');
    });
  });

  describe('styling', () => {
    it('has primary color background', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('bg-primary-700');
    });

    it('has white text color', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('text-white');
    });

    it('has rounded corners', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('rounded-lg');
    });

    it('has shadow', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('shadow-lg');
    });

    it('has z-50 for proper layering', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('z-50');
    });
  });

  describe('className prop', () => {
    it('applies additional className to container', () => {
      render(
        <Tooltip content="Tooltip text" className="custom-class">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      expect(container).toHaveClass('custom-class');
    });

    it('combines className with default classes', () => {
      render(
        <Tooltip content="Tooltip text" className="custom-class">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      expect(container).toHaveClass('relative', 'inline-block', 'custom-class');
    });
  });

  describe('accessibility', () => {
    it('has role="tooltip" on tooltip element', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });

    it('associates tooltip with trigger via aria-describedby when visible', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      const triggerWrapper = container.firstElementChild;

      expect(triggerWrapper).not.toHaveAttribute('aria-describedby');

      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      expect(triggerWrapper).toHaveAttribute('aria-describedby', tooltip.id);
    });

    it('has unique id on tooltip', async () => {
      render(
        <>
          <Tooltip content="First tooltip">
            <button type="button">First</button>
          </Tooltip>
          <Tooltip content="Second tooltip">
            <button type="button">Second</button>
          </Tooltip>
        </>
      );

      const containers = screen.getAllByTestId('tooltip-container');
      fireEvent.mouseEnter(containers[0]);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const firstTooltip = screen.getByRole('tooltip');
      const firstId = firstTooltip.id;

      fireEvent.mouseLeave(containers[0]);
      fireEvent.mouseEnter(containers[1]);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const secondTooltip = screen.getByRole('tooltip');
      expect(secondTooltip.id).not.toBe(firstId);
    });

    it('has aria-hidden on arrow element', async () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      const arrow = tooltip.querySelector('span');
      expect(arrow).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('arrow styles', () => {
    it('renders arrow for top position', async () => {
      render(
        <Tooltip content="Tooltip text" position="top">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      const arrow = tooltip.querySelector('span');
      expect(arrow).toHaveClass('top-full', 'border-t-primary-700');
    });

    it('renders arrow for bottom position', async () => {
      render(
        <Tooltip content="Tooltip text" position="bottom">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      const arrow = tooltip.querySelector('span');
      expect(arrow).toHaveClass('bottom-full', 'border-b-primary-700');
    });

    it('renders arrow for left position', async () => {
      render(
        <Tooltip content="Tooltip text" position="left">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      const arrow = tooltip.querySelector('span');
      expect(arrow).toHaveClass('left-full', 'border-l-primary-700');
    });

    it('renders arrow for right position', async () => {
      render(
        <Tooltip content="Tooltip text" position="right">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      const tooltip = screen.getByRole('tooltip');
      const arrow = tooltip.querySelector('span');
      expect(arrow).toHaveClass('right-full', 'border-r-primary-700');
    });
  });

  describe('children prop', () => {
    it('renders string children wrapped in element', () => {
      render(
        <Tooltip content="Tooltip text">
          <span>Text child</span>
        </Tooltip>
      );

      expect(screen.getByText('Text child')).toBeInTheDocument();
    });

    it('renders element children', () => {
      render(
        <Tooltip content="Tooltip text">
          <button type="button" data-testid="child-button">
            Button child
          </button>
        </Tooltip>
      );

      expect(screen.getByTestId('child-button')).toBeInTheDocument();
    });

    it('renders complex children', () => {
      render(
        <Tooltip content="Tooltip text">
          <div>
            <span>Nested</span>
            <strong>Content</strong>
          </div>
        </Tooltip>
      );

      expect(screen.getByText('Nested')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
    });
  });

  describe('content prop', () => {
    it('displays content text in tooltip', async () => {
      render(
        <Tooltip content="Hello, World!">
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    });

    it('displays long content text', async () => {
      const longContent = 'This is a very long tooltip content text that explains something.';
      render(
        <Tooltip content={longContent}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      expect(screen.getByText(longContent)).toBeInTheDocument();
    });
  });

  describe('cleanup', () => {
    it('clears timeout on unmount', async () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');

      const { unmount } = render(
        <Tooltip content="Tooltip text" delay={500}>
          <button type="button">Hover me</button>
        </Tooltip>
      );

      const container = getContainer();
      fireEvent.mouseEnter(container);

      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();

      clearTimeoutSpy.mockRestore();
    });
  });
});
