import type { ContainerProps } from '@/types';

const variantStyles = {
  standard: 'max-w-screen-xl', // 1280px
  wide: 'max-w-screen-2xl', // 1536px
  full: 'max-w-full',
};

/**
 * Container Component
 * コンテンツエリアのラッパーコンポーネント
 */
export function Container({ variant = 'standard', children, className = '' }: ContainerProps) {
  return (
    <div
      className={['mx-auto', 'px-4 sm:px-6 lg:px-8', variantStyles[variant], className]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  );
}
