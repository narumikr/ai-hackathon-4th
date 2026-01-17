'use client';

import { LIST } from '@/constants/ui';
import type { ListProps } from '@/types/ui';
import { LoadingSpinner } from './LoadingSpinner';

const baseStyles = ['w-full'].join(' ');

const listStyles = ['divide-y divide-neutral-200'].join(' ');

const itemStyles = ['py-3 first:pt-0 last:pb-0'].join(' ');

const emptyStyles = [
  'py-8 text-center text-neutral-500',
  'border border-dashed border-neutral-300 rounded-lg',
  'bg-neutral-50',
].join(' ');

const loadingContainerStyles = [
  'flex flex-col items-center justify-center py-8 gap-2',
  'border border-dashed border-primary-300 rounded-lg',
  'bg-primary-50',
].join(' ');

const loadingTextStyles = ['text-sm text-primary-600'].join(' ');

export function List<T>({
  items,
  renderItem,
  loading = false,
  emptyMessage = LIST.EMPTY_MESSAGE,
  className = '',
  keyExtractor,
}: ListProps<T>) {
  if (loading) {
    return (
      <div className={[baseStyles, className].filter(Boolean).join(' ')}>
        <div className={loadingContainerStyles}>
          <LoadingSpinner size="lg" />
          <span className={loadingTextStyles}>{LIST.LOADING_MESSAGE}</span>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className={[baseStyles, className].filter(Boolean).join(' ')}>
        <div className={emptyStyles}>{emptyMessage}</div>
      </div>
    );
  }

  return (
    <div className={[baseStyles, className].filter(Boolean).join(' ')}>
      <ul className={listStyles}>
        {items.map((item, index) => {
          const key = keyExtractor ? keyExtractor(item, index) : index;
          return (
            <li key={key} className={itemStyles}>
              {renderItem(item, index)}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
