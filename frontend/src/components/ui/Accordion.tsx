'use client';

import type { AccordionProps } from '@/types/ui';
import { useState } from 'react';

export function Accordion({
  items,
  multiple = true,
  defaultOpen = [],
  className = '',
}: AccordionProps) {
  const [openItems, setOpenItems] = useState<string[]>(defaultOpen);

  const toggleItem = (id: string) => {
    if (multiple) {
      setOpenItems(prev => (prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]));
    } else {
      setOpenItems(prev => (prev.includes(id) ? [] : [id]));
    }
  };

  const isOpen = (id: string) => openItems.includes(id);

  return (
    <div
      className={`divide-y divide-neutral-200 rounded-lg border border-neutral-300 ${className}`}
    >
      {items.map(item => {
        const open = isOpen(item.id);
        return (
          <div key={item.id} className="overflow-hidden">
            <button
              type="button"
              onClick={() => toggleItem(item.id)}
              className={[
                'flex w-full items-center justify-between px-4 py-3',
                'text-left font-medium transition-colors duration-200',
                'hover:bg-primary-50',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-300 focus-visible:ring-offset-2',
                open ? 'bg-primary-50 text-primary-900' : 'bg-white text-neutral-900',
              ].join(' ')}
            >
              <span className="text-base">{item.title}</span>
              <svg
                className={[
                  'h-5 w-5 transition-transform duration-200',
                  open ? 'rotate-180 text-primary-600' : 'rotate-0 text-neutral-500',
                ].join(' ')}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
            <div
              className={[
                'overflow-hidden transition-all duration-300 ease-in-out',
                open ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0',
              ].join(' ')}
            >
              <div className="bg-white px-4 py-3 text-neutral-700 text-sm">{item.content}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
