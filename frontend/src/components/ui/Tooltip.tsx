'use client';

import { useCallback, useEffect, useId, useRef, useState } from 'react';

import type { TooltipProps } from '@/types/ui';

const positionStyles = {
  top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
  bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
  left: 'right-full top-1/2 -translate-y-1/2 mr-2',
  right: 'left-full top-1/2 -translate-y-1/2 ml-2',
};

const arrowStyles = {
  top: 'top-full left-1/2 -translate-x-1/2 border-t-primary-700 border-l-transparent border-r-transparent border-b-transparent',
  bottom:
    'bottom-full left-1/2 -translate-x-1/2 border-b-primary-700 border-l-transparent border-r-transparent border-t-transparent',
  left: 'left-full top-1/2 -translate-y-1/2 border-l-primary-700 border-t-transparent border-b-transparent border-r-transparent',
  right:
    'right-full top-1/2 -translate-y-1/2 border-r-primary-700 border-t-transparent border-b-transparent border-l-transparent',
};

const tooltipStyles = [
  'bg-primary-700 text-white',
  'px-3 py-2',
  'text-sm font-medium',
  'rounded-lg',
  'shadow-lg',
  'whitespace-nowrap',
  'z-50',
].join(' ');

const baseArrowStyles = 'absolute w-0 h-0 border-[6px] border-solid';

export function Tooltip({
  content,
  position = 'top',
  delay = 200,
  children,
  className = '',
  isOpen,
}: TooltipProps) {
  const [isHovered, setIsHovered] = useState(false);
  // If isOpen is provided (controlled), use it. Otherwise use internal hover state.
  const isControlled = isOpen !== undefined;
  const isVisible = isControlled ? isOpen : isHovered;
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tooltipId = useId();

  const showTooltip = useCallback(() => {
    if (isControlled) return; // Skip internal state update in controlled mode
    timeoutRef.current = setTimeout(() => {
      setIsHovered(true);
    }, delay);
  }, [delay, isControlled]);

  const hideTooltip = useCallback(() => {
    if (isControlled) return; // Skip internal state update in controlled mode
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setIsHovered(false);
  }, [isControlled]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <div
      data-testid="tooltip-container"
      className={['relative inline-block', className].filter(Boolean).join(' ')}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      <div aria-describedby={isVisible ? tooltipId : undefined}>{children}</div>
      {isVisible && (
        <div
          id={tooltipId}
          role="tooltip"
          className={['absolute', positionStyles[position], tooltipStyles]
            .filter(Boolean)
            .join(' ')}
        >
          {content}
          <span
            className={[baseArrowStyles, arrowStyles[position]].filter(Boolean).join(' ')}
            aria-hidden="true"
          />
        </div>
      )}
    </div>
  );
}
