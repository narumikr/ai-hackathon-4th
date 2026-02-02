'use client';

import { Container } from '@/components/layout';
import { Button, LoadingSpinner } from '@/components/ui';
import { BUTTON_LABELS, BUTTON_STATES } from '@/constants';
import Link from 'next/link';
import type { ReactNode } from 'react';

type GenerationStatusViewProps = {
  /** ページタイトル */
  title: string;
  /** 生成ステータス */
  status: 'processing' | 'failed';
  /** ステータスラベル（processing時に表示） */
  statusLabel: string;
  /** ヒントメッセージ（processing時に表示） */
  hintMessage?: string;
  /** エラーメッセージ（failed時に表示） */
  errorMessage?: string;
  /** リトライボタンのラベル */
  retryLabel?: string;
  /** 更新中かどうか */
  isRefreshing?: boolean;
  /** リトライ中かどうか */
  isRetrying?: boolean;
  /** 更新ボタンクリック時のコールバック */
  onRefresh?: () => void;
  /** リトライボタンクリック時のコールバック */
  onRetry?: () => void;
  /** 戻るボタンのリンク先（指定時はLinkを使用） */
  backHref?: string;
  /** 戻るボタンクリック時のコールバック（backHrefより優先） */
  onBack?: () => void;
  /** ヘッダー右側に追加するコンテンツ */
  headerActions?: ReactNode;
};

/**
 * 生成ステータス表示コンポーネント
 * processing（生成中）とfailed（失敗）の状態を表示する
 */
export function GenerationStatusView({
  title,
  status,
  statusLabel,
  hintMessage,
  errorMessage,
  retryLabel = BUTTON_LABELS.RETRY_GENERATE_GUIDE,
  isRefreshing = false,
  isRetrying = false,
  onRefresh,
  onRetry,
  backHref,
  onBack,
  headerActions,
}: GenerationStatusViewProps) {
  const renderBackButton = () => {
    if (onBack) {
      return (
        <Button variant="ghost" onClick={onBack}>
          {BUTTON_LABELS.BACK}
        </Button>
      );
    }
    if (backHref) {
      return (
        <Link
          href={backHref}
          className="inline-flex items-center rounded-md border border-transparent bg-transparent px-3 py-2 text-sm font-medium text-primary hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        >
          {BUTTON_LABELS.BACK}
        </Link>
      );
    }
    return null;
  };

  const renderRefreshButton = () => {
    if (!onRefresh) return null;

    return (
      <Button variant="secondary" onClick={onRefresh} disabled={isRefreshing}>
        {isRefreshing ? (
          <>
            <LoadingSpinner size="sm" variant="secondary" className="mr-2" />
            {BUTTON_STATES.UPDATING}
          </>
        ) : (
          BUTTON_LABELS.UPDATE
        )}
      </Button>
    );
  };

  if (status === 'processing') {
    return (
      <div className="py-8">
        <Container>
          <div className="mb-6 flex items-center justify-between">
            <h1 className="font-bold text-2xl text-neutral-900">{title}</h1>
            <div className="flex gap-2">
              {renderRefreshButton()}
              {renderBackButton()}
              {headerActions}
            </div>
          </div>
          <div className="flex flex-col items-center justify-center rounded-lg border border-warning-200 bg-warning-50 py-16">
            <LoadingSpinner size="lg" variant="primary" className="mb-4" />
            <p className="mb-2 font-semibold text-lg text-warning-800">{statusLabel}</p>
            {hintMessage && <p className="text-sm text-warning-700">{hintMessage}</p>}
          </div>
        </Container>
      </div>
    );
  }

  // status === 'failed'
  return (
    <div className="py-8">
      <Container>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-bold text-2xl text-neutral-900">{title}</h1>
          <div className="flex gap-2">
            {renderBackButton()}
            {headerActions}
          </div>
        </div>
        <div className="flex flex-col items-center justify-center rounded-lg border border-danger-200 bg-danger-50 py-16">
          <p className="mb-2 font-semibold text-danger-800 text-lg">{statusLabel}</p>
          {errorMessage && <p className="mb-6 text-danger-700 text-sm">{errorMessage}</p>}
          {onRetry && (
            <Button variant="primary" onClick={onRetry} disabled={isRetrying}>
              {isRetrying ? (
                <>
                  <LoadingSpinner size="sm" variant="primary" className="mr-2" />
                  {BUTTON_STATES.UPDATING}
                </>
              ) : (
                retryLabel
              )}
            </Button>
          )}
        </div>
      </Container>
    </div>
  );
}
