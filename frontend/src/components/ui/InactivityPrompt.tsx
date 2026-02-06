'use client';

import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';

import { INACTIVITY_PROMPT } from '@/constants/ui';

interface InactivityPromptProps {
  /** 非アクティブ判定までの時間（ミリ秒）デフォルト: 5000 (5秒) */
  inactivityDelay?: number;
}

const STORAGE_KEY = 'inactivity-prompt-dismissed';

/**
 * 非アクティブ時にユーザーに次のアクションを促すプロンプトコンポーネント
 * 画面右下にフェードインアニメーションで表示される
 * セッション中に一度表示され、ユーザーが閉じた場合は再表示されない
 */
export function InactivityPrompt({ inactivityDelay = 5000 }: InactivityPromptProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isFadingIn, setIsFadingIn] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fadeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // セッションストレージから dismissed 状態を読み込む
  useEffect(() => {
    const dismissed = sessionStorage.getItem(STORAGE_KEY) === 'true';
    setIsDismissed(dismissed);
  }, []);

  const resetTimer = useCallback(() => {
    // 既存のタイマーをクリア
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    if (fadeTimerRef.current) {
      clearTimeout(fadeTimerRef.current);
    }

    // プロンプトが表示されている場合は非表示にする
    setIsFadingIn(false);
    setIsVisible(false);

    // 既に閉じられている場合は新しいタイマーを設定しない
    if (isDismissed) {
      return;
    }

    // 新しいタイマーを設定
    timerRef.current = setTimeout(() => {
      setIsVisible(true);
      // DOM更新後にフェードインを開始
      fadeTimerRef.current = setTimeout(() => {
        setIsFadingIn(true);
      }, 50);
    }, inactivityDelay);
  }, [inactivityDelay, isDismissed]);

  const handleClose = useCallback(() => {
    setIsFadingIn(false);
    setIsVisible(false);
    setIsDismissed(true);
    // セッションストレージに保存
    sessionStorage.setItem(STORAGE_KEY, 'true');

    // タイマーをクリア（再表示されないようにする）
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    if (fadeTimerRef.current) {
      clearTimeout(fadeTimerRef.current);
    }
  }, []);

  useEffect(() => {
    // 既に閉じられている場合は何もしない
    if (isDismissed) {
      return;
    }

    // 監視するイベントタイプ（scrollは頻繁に発火するため除外）
    const events = ['mousedown', 'keydown', 'touchstart'];

    // イベントリスナーを追加
    events.forEach(event => {
      document.addEventListener(event, resetTimer);
    });

    // 初回タイマーを開始
    resetTimer();

    // クリーンアップ
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, resetTimer);
      });
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current);
      }
    };
  }, [isDismissed, resetTimer]);

  if (!isVisible) return null;

  return (
    <div
      data-testid="inactivity-prompt"
      className={`fixed right-6 bottom-6 z-40 max-w-sm rounded-lg bg-white p-4 shadow-lg transition-opacity duration-500 ${
        isFadingIn ? 'opacity-100' : 'opacity-0'
      }`}
      // biome-ignore lint/a11y/useSemanticElements: Using div with role="status" for better positioning and styling control
      role="status"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <Link
            href="/travel/new"
            className="block font-medium text-base text-primary-600 hover:text-primary-700 hover:underline"
            onClick={handleClose}
          >
            {INACTIVITY_PROMPT.MESSAGE}
          </Link>
        </div>
        <button
          type="button"
          onClick={handleClose}
          className="rounded-md p-1 text-neutral-400 transition-colors duration-200 hover:bg-neutral-100 hover:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary-300"
          aria-label={INACTIVITY_PROMPT.CLOSE_BUTTON}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
  );
}
