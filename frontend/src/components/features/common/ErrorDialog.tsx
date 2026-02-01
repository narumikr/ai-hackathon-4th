'use client';

import { Button, Modal } from '@/components/ui';
import { BUTTON_LABELS } from '@/constants';

type ErrorDialogProps = {
  /** ダイアログが開いているかどうか */
  isOpen: boolean;
  /** ダイアログを閉じる時のコールバック */
  onClose: () => void;
  /** ダイアログのタイトル */
  title: string;
  /** エラーメッセージ */
  message: string;
  /** OKボタンのラベル（デフォルト: 閉じる） */
  buttonLabel?: string;
};

/**
 * エラーダイアログコンポーネント
 * 同期的なAPI呼び出しのエラーを表示する
 */
export function ErrorDialog({
  isOpen,
  onClose,
  title,
  message,
  buttonLabel = BUTTON_LABELS.CLOSE,
}: ErrorDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="space-y-6">
        <p className="text-neutral-600">{message}</p>
        <div className="flex justify-end">
          <Button variant="primary" onClick={onClose}>
            {buttonLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
