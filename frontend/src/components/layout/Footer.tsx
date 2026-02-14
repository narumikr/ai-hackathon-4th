import { COPYRIGHT_TEXT, FOOTER_LINKS } from '@/constants';
import type { FooterProps } from '@/types';

/**
 * Footer Component
 * アプリケーション共通フッター
 */
export function Footer({ className = '' }: FooterProps) {
  return (
    <footer
      className={['mt-auto border-neutral-200 border-t bg-neutral-100', className]
        .filter(Boolean)
        .join(' ')}
    >
      <div className="mx-auto max-w-screen-2xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        <div className="flex flex-col items-center justify-between gap-4 lg:flex-row">
          {/* Footer Links */}
          <nav className="flex flex-wrap justify-center gap-4 lg:justify-start lg:gap-6">
            {FOOTER_LINKS.map(link => (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-neutral-600 text-sm transition-colors hover:text-primary-700"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Copyright */}
          <p className="text-center text-neutral-500 text-sm lg:text-right">{COPYRIGHT_TEXT}</p>
        </div>
      </div>
    </footer>
  );
}
