'use client';

import Image from 'next/image';
import { useId } from 'react';

import type { CardProps } from '@/types/ui';

const variantStyles = {
  default: ['bg-white', 'border border-neutral-200'].join(' '),
  outlined: ['bg-white', 'border-2 border-neutral-300'].join(' '),
  elevated: ['bg-white', 'border border-neutral-100', 'shadow-lg'].join(' '),
};

const baseStyles = ['rounded-xl', 'overflow-hidden', 'transition-all duration-200 ease-out'].join(
  ' '
);

const clickableStyles = [
  'cursor-pointer',
  'hover:shadow-md hover:border-primary-300',
  'active:scale-[0.98]',
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-300 focus-visible:ring-offset-2',
].join(' ');

export function Card({
  variant = 'default',
  image,
  title,
  description,
  actions,
  clickable = false,
  className = '',
  children,
  onClick,
  ariaLabel,
  ...props
}: CardProps) {
  const isClickable = clickable || !!onClick;
  const generatedId = useId();
  const titleId = title && isClickable ? generatedId : undefined;

  // アクセシビリティ警告: クリック可能なカードにはaria-labelまたはtitleが必要
  if (isClickable && !title && !ariaLabel && process.env.NODE_ENV === 'development') {
    console.warn(
      'Card: Clickable cards should have either a "title" or "ariaLabel" prop for accessibility. ' +
        'Screen readers need to know what the button does.'
    );
  }

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    onClick?.(e);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick?.(e as unknown as React.MouseEvent<HTMLDivElement>);
    }
  };

  // aria属性の決定: titleがあればaria-labelledby、ariaLabelがあればaria-label、なければ空
  const ariaProps = isClickable
    ? titleId
      ? { 'aria-labelledby': titleId }
      : ariaLabel
        ? { 'aria-label': ariaLabel }
        : {}
    : {};

  return (
    <div
      className={[baseStyles, variantStyles[variant], isClickable ? clickableStyles : '', className]
        .filter(Boolean)
        .join(' ')}
      onClick={isClickable ? handleClick : undefined}
      onKeyDown={isClickable ? handleKeyDown : undefined}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      {...ariaProps}
      {...props}
    >
      {image && (
        <div className="relative aspect-video w-full overflow-hidden">
          <Image
            src={image.src}
            alt={image.alt}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        </div>
      )}
      <div className="p-4">
        {title && (
          <h3 id={titleId} className="mb-1 font-semibold text-lg text-neutral-900">
            {title}
          </h3>
        )}
        {description && <p className="text-neutral-600 text-sm">{description}</p>}
        {children}
        {actions && <div className="mt-4 flex gap-2">{actions}</div>}
      </div>
    </div>
  );
}
