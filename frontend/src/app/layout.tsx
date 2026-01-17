import type { Metadata } from 'next';
import './globals.css';
import { Footer, Header } from '@/components/layout';

export const metadata: Metadata = {
  title: 'Historical Travel Agent',
  description: '歴史学習特化型旅行AIエージェント',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
