import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Checkbox } from './Checkbox';

describe('Checkbox', () => {
  describe('基本的なレンダリング', () => {
    it('labelなしでレンダリングできること', () => {
      const { container } = render(<Checkbox />);
      const checkbox = container.querySelector('input[type="checkbox"]');
      expect(checkbox).toBeInTheDocument();
    });

    it('labelありでレンダリングできること', () => {
      render(<Checkbox label="テストラベル" />);
      expect(screen.getByLabelText('テストラベル')).toBeInTheDocument();
    });

    it('チェックボックスのtype属性がcheckboxであること', () => {
      render(<Checkbox label="テスト" />);
      const checkbox = screen.getByLabelText('テスト') as HTMLInputElement;
      expect(checkbox.type).toBe('checkbox');
    });
  });

  describe('Props: id', () => {
    it('カスタムIDが指定できること', () => {
      render(<Checkbox id="custom-id" label="カスタムID" />);
      const checkbox = screen.getByLabelText('カスタムID');
      expect(checkbox.id).toBe('custom-id');
    });

    it('IDを指定しない場合は自動生成されること', () => {
      render(<Checkbox label="自動ID" />);
      const checkbox = screen.getByLabelText('自動ID');
      expect(checkbox.id).toMatch(/^checkbox-/);
    });
  });

  describe('Props: label', () => {
    it('ラベルが表示されること', () => {
      render(<Checkbox label="表示ラベル" />);
      expect(screen.getByText('表示ラベル')).toBeInTheDocument();
    });

    it('ラベルなしでも動作すること', () => {
      const { container } = render(<Checkbox />);
      const checkbox = container.querySelector('input[type="checkbox"]');
      expect(checkbox).toBeInTheDocument();
    });

    it('ラベルをクリックするとチェックボックスが切り替わること', () => {
      render(<Checkbox label="クリック可能" />);
      const checkbox = screen.getByLabelText('クリック可能') as HTMLInputElement;
      const label = screen.getByText('クリック可能');

      expect(checkbox.checked).toBe(false);
      fireEvent.click(label);
      expect(checkbox.checked).toBe(true);
    });
  });

  describe('Props: size', () => {
    it('デフォルトサイズ(md)が適用されること', () => {
      render(<Checkbox label="デフォルト" />);
      const checkbox = screen.getByLabelText('デフォルト');
      expect(checkbox).toHaveClass('w-5', 'h-5');
    });

    it('smサイズが適用されること', () => {
      render(<Checkbox label="小" size="sm" />);
      const checkbox = screen.getByLabelText('小');
      expect(checkbox).toHaveClass('w-4', 'h-4');
    });

    it('mdサイズが適用されること', () => {
      render(<Checkbox label="中" size="md" />);
      const checkbox = screen.getByLabelText('中');
      expect(checkbox).toHaveClass('w-5', 'h-5');
    });

    it('lgサイズが適用されること', () => {
      render(<Checkbox label="大" size="lg" />);
      const checkbox = screen.getByLabelText('大');
      expect(checkbox).toHaveClass('w-6', 'h-6');
    });

    it('ラベルのフォントサイズがsmの場合に適用されること', () => {
      render(<Checkbox label="小サイズラベル" size="sm" />);
      const label = screen.getByText('小サイズラベル');
      expect(label).toHaveClass('text-sm');
    });

    it('ラベルのフォントサイズがmdの場合に適用されること', () => {
      render(<Checkbox label="中サイズラベル" size="md" />);
      const label = screen.getByText('中サイズラベル');
      expect(label).toHaveClass('text-base');
    });

    it('ラベルのフォントサイズがlgの場合に適用されること', () => {
      render(<Checkbox label="大サイズラベル" size="lg" />);
      const label = screen.getByText('大サイズラベル');
      expect(label).toHaveClass('text-lg');
    });
  });

  describe('Props: disabled', () => {
    it('デフォルトでは無効化されていないこと', () => {
      render(<Checkbox label="有効" />);
      const checkbox = screen.getByLabelText('有効');
      expect(checkbox).not.toBeDisabled();
    });

    it('disabled=trueで無効化されること', () => {
      render(<Checkbox label="無効" disabled />);
      const checkbox = screen.getByLabelText('無効');
      expect(checkbox).toBeDisabled();
    });

    it('disabled時のスタイルが適用されること', () => {
      render(<Checkbox label="無効スタイル" disabled />);
      const checkbox = screen.getByLabelText('無効スタイル');
      expect(checkbox).toHaveClass(
        'cursor-not-allowed',
        'border-neutral-300',
        'bg-neutral-100',
        'opacity-50'
      );
    });

    it('disabled時のラベルスタイルが適用されること', () => {
      render(<Checkbox label="無効ラベル" disabled />);
      const label = screen.getByText('無効ラベル');
      expect(label).toHaveClass('cursor-not-allowed', 'text-neutral-400');
    });
  });

  describe('Props: error', () => {
    it('デフォルトではエラー状態でないこと', () => {
      render(<Checkbox label="正常" />);
      const checkbox = screen.getByLabelText('正常');
      expect(checkbox).toHaveClass('border-primary-500');
      expect(checkbox).not.toHaveClass('border-red-500');
    });

    it('error=trueでエラー状態になること', () => {
      render(<Checkbox label="エラー" error />);
      const checkbox = screen.getByLabelText('エラー');
      expect(checkbox).toHaveClass('border-red-500', 'accent-red-500');
    });

    it('エラー時のラベルスタイルが適用されること', () => {
      render(<Checkbox label="エラーラベル" error />);
      const label = screen.getByText('エラーラベル');
      expect(label).toHaveClass('text-red-700');
    });

    it('エラー時のフォーカスリングが赤色になること', () => {
      render(<Checkbox label="エラーフォーカス" error />);
      const checkbox = screen.getByLabelText('エラーフォーカス');
      expect(checkbox).toHaveClass('focus:ring-red-300');
    });
  });

  describe('Props: description', () => {
    it('descriptionが表示されること', () => {
      render(<Checkbox label="ラベル" description="説明文テキスト" />);
      expect(screen.getByText('説明文テキスト')).toBeInTheDocument();
    });

    it('descriptionなしでも動作すること', () => {
      render(<Checkbox label="説明なし" />);
      expect(screen.queryByText('説明')).not.toBeInTheDocument();
    });

    it('disabled時のdescriptionスタイルが適用されること', () => {
      render(<Checkbox label="ラベル" description="無効な説明" disabled />);
      const description = screen.getByText('無効な説明');
      expect(description).toHaveClass('text-neutral-300');
    });

    it('error時のdescriptionスタイルが適用されること', () => {
      render(<Checkbox label="ラベル" description="エラー説明" error />);
      const description = screen.getByText('エラー説明');
      expect(description).toHaveClass('text-red-600');
    });
  });

  describe('Props: className', () => {
    it('カスタムclassNameが親要素に適用されること', () => {
      render(<Checkbox label="カスタム" className="custom-class" />);
      const checkbox = screen.getByLabelText('カスタム');
      const parentDiv = checkbox.parentElement?.parentElement;
      expect(parentDiv).toHaveClass('custom-class');
    });

    it('複数のclassNameが適用されること', () => {
      render(<Checkbox label="複数クラス" className="class1 class2" />);
      const checkbox = screen.getByLabelText('複数クラス');
      const parentDiv = checkbox.parentElement?.parentElement;
      expect(parentDiv).toHaveClass('class1', 'class2');
    });
  });

  describe('イベントハンドラ', () => {
    it('onChangeイベントが発火すること', () => {
      const handleChange = vi.fn();
      render(<Checkbox label="変更イベント" onChange={handleChange} />);
      const checkbox = screen.getByLabelText('変更イベント');

      fireEvent.click(checkbox);
      expect(handleChange).toHaveBeenCalledTimes(1);
    });

    it('onClickイベントが発火すること', () => {
      const handleClick = vi.fn();
      render(<Checkbox label="クリックイベント" onClick={handleClick} />);
      const checkbox = screen.getByLabelText('クリックイベント');

      fireEvent.click(checkbox);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('スタイル', () => {
    it('通常時のボーダー色が適用されること', () => {
      render(<Checkbox label="ボーダー" />);
      const checkbox = screen.getByLabelText('ボーダー');
      expect(checkbox).toHaveClass('border-primary-500');
    });

    it('アクセントカラーが適用されること', () => {
      render(<Checkbox label="アクセント" />);
      const checkbox = screen.getByLabelText('アクセント');
      expect(checkbox).toHaveClass('accent-primary-500');
    });

    it('ホバー時のボーダー色が設定されていること', () => {
      render(<Checkbox label="ホバー" />);
      const checkbox = screen.getByLabelText('ホバー');
      expect(checkbox).toHaveClass('hover:border-primary-600');
    });

    it('フォーカス時のリングが設定されていること', () => {
      render(<Checkbox label="フォーカス" />);
      const checkbox = screen.getByLabelText('フォーカス');
      expect(checkbox).toHaveClass(
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-offset-2',
        'focus:ring-primary-300'
      );
    });

    it('トランジションが設定されていること', () => {
      render(<Checkbox label="トランジション" />);
      const checkbox = screen.getByLabelText('トランジション');
      expect(checkbox).toHaveClass('transition-all', 'duration-200', 'ease-out');
    });

    it('角丸が設定されていること', () => {
      render(<Checkbox label="角丸" />);
      const checkbox = screen.getByLabelText('角丸');
      expect(checkbox).toHaveClass('rounded');
    });
  });

  describe('複数のPropsの組み合わせ', () => {
    it('error + disabledが同時に適用されること', () => {
      render(<Checkbox label="エラー＋無効" error disabled />);
      const checkbox = screen.getByLabelText('エラー＋無効');
      expect(checkbox).toBeDisabled();
      expect(checkbox).toHaveClass('cursor-not-allowed', 'opacity-50');
    });

    it('すべてのPropsが同時に適用されること', () => {
      const handleChange = vi.fn();
      render(
        <Checkbox
          id="full-props"
          label="全Props"
          size="lg"
          description="完全な説明"
          className="custom-full"
          onChange={handleChange}
        />
      );

      const checkbox = screen.getByLabelText('全Props') as HTMLInputElement;
      expect(checkbox.id).toBe('full-props');
      expect(checkbox).toHaveClass('w-6', 'h-6');
      expect(screen.getByText('完全な説明')).toBeInTheDocument();

      const parentDiv = checkbox.parentElement?.parentElement;
      expect(parentDiv).toHaveClass('custom-full');

      fireEvent.click(checkbox);
      expect(handleChange).toHaveBeenCalled();
    });
  });
});
