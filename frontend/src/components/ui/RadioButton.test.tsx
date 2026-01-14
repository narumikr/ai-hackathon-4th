import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { RadioButton } from './RadioButton';

describe('RadioButton', () => {
  describe('基本的なレンダリング', () => {
    it('labelなしでレンダリングできること', () => {
      const { container } = render(<RadioButton name="test" value="1" />);
      const radio = container.querySelector('input[type="radio"]');
      expect(radio).toBeInTheDocument();
    });

    it('labelありでレンダリングできること', () => {
      render(<RadioButton label="テストラベル" name="test" value="1" />);
      expect(screen.getByLabelText('テストラベル')).toBeInTheDocument();
    });

    it('ラジオボタンのtype属性がradioであること', () => {
      render(<RadioButton label="テスト" name="test" value="1" />);
      const radio = screen.getByLabelText('テスト') as HTMLInputElement;
      expect(radio.type).toBe('radio');
    });
  });

  describe('Props: id', () => {
    it('カスタムIDが指定できること', () => {
      render(<RadioButton id="custom-id" label="カスタムID" name="test" value="1" />);
      const radio = screen.getByLabelText('カスタムID');
      expect(radio.id).toBe('custom-id');
    });

    it('IDを指定しない場合は自動生成されること', () => {
      render(<RadioButton label="自動ID" name="test" value="1" />);
      const radio = screen.getByLabelText('自動ID');
      expect(radio.id).toMatch(/^radio-/);
    });
  });

  describe('Props: label', () => {
    it('ラベルが表示されること', () => {
      render(<RadioButton label="表示ラベル" name="test" value="1" />);
      expect(screen.getByText('表示ラベル')).toBeInTheDocument();
    });

    it('ラベルなしでも動作すること', () => {
      const { container } = render(<RadioButton name="test" value="1" />);
      const radio = container.querySelector('input[type="radio"]');
      expect(radio).toBeInTheDocument();
    });

    it('ラベルをクリックするとラジオボタンが選択されること', () => {
      render(<RadioButton label="クリック可能" name="test" value="1" />);
      const radio = screen.getByLabelText('クリック可能') as HTMLInputElement;
      const label = screen.getByText('クリック可能');

      expect(radio.checked).toBe(false);
      fireEvent.click(label);
      expect(radio.checked).toBe(true);
    });
  });

  describe('Props: name と value', () => {
    it('name属性が正しく設定されること', () => {
      render(<RadioButton label="テスト" name="test-name" value="1" />);
      const radio = screen.getByLabelText('テスト') as HTMLInputElement;
      expect(radio.name).toBe('test-name');
    });

    it('value属性が正しく設定されること', () => {
      render(<RadioButton label="テスト" name="test" value="test-value" />);
      const radio = screen.getByLabelText('テスト') as HTMLInputElement;
      expect(radio.value).toBe('test-value');
    });

    it('同じname属性のラジオボタンがグループ化されること', () => {
      render(
        <>
          <RadioButton label="選択肢1" name="group" value="1" />
          <RadioButton label="選択肢2" name="group" value="2" />
        </>
      );
      const radio1 = screen.getByLabelText('選択肢1') as HTMLInputElement;
      const radio2 = screen.getByLabelText('選択肢2') as HTMLInputElement;

      expect(radio1.name).toBe('group');
      expect(radio2.name).toBe('group');
    });

    it('同じグループ内では1つだけ選択できること', () => {
      render(
        <>
          <RadioButton label="選択肢1" name="group" value="1" />
          <RadioButton label="選択肢2" name="group" value="2" />
        </>
      );
      const radio1 = screen.getByLabelText('選択肢1') as HTMLInputElement;
      const radio2 = screen.getByLabelText('選択肢2') as HTMLInputElement;

      fireEvent.click(radio1);
      expect(radio1.checked).toBe(true);
      expect(radio2.checked).toBe(false);

      fireEvent.click(radio2);
      expect(radio1.checked).toBe(false);
      expect(radio2.checked).toBe(true);
    });
  });

  describe('Props: size', () => {
    it('デフォルトサイズ(md)が適用されること', () => {
      render(<RadioButton label="デフォルト" name="test" value="1" />);
      const radio = screen.getByLabelText('デフォルト');
      expect(radio).toHaveClass('w-5', 'h-5');
    });

    it('smサイズが適用されること', () => {
      render(<RadioButton label="小" name="test" value="1" size="sm" />);
      const radio = screen.getByLabelText('小');
      expect(radio).toHaveClass('w-4', 'h-4');
    });

    it('mdサイズが適用されること', () => {
      render(<RadioButton label="中" name="test" value="1" size="md" />);
      const radio = screen.getByLabelText('中');
      expect(radio).toHaveClass('w-5', 'h-5');
    });

    it('lgサイズが適用されること', () => {
      render(<RadioButton label="大" name="test" value="1" size="lg" />);
      const radio = screen.getByLabelText('大');
      expect(radio).toHaveClass('w-6', 'h-6');
    });

    it('ラベルのフォントサイズがsmの場合に適用されること', () => {
      render(<RadioButton label="小サイズラベル" name="test" value="1" size="sm" />);
      const label = screen.getByText('小サイズラベル');
      expect(label).toHaveClass('text-sm');
    });

    it('ラベルのフォントサイズがmdの場合に適用されること', () => {
      render(<RadioButton label="中サイズラベル" name="test" value="1" size="md" />);
      const label = screen.getByText('中サイズラベル');
      expect(label).toHaveClass('text-base');
    });

    it('ラベルのフォントサイズがlgの場合に適用されること', () => {
      render(<RadioButton label="大サイズラベル" name="test" value="1" size="lg" />);
      const label = screen.getByText('大サイズラベル');
      expect(label).toHaveClass('text-lg');
    });
  });

  describe('Props: disabled', () => {
    it('デフォルトでは無効化されていないこと', () => {
      render(<RadioButton label="有効" name="test" value="1" />);
      const radio = screen.getByLabelText('有効');
      expect(radio).not.toBeDisabled();
    });

    it('disabled=trueで無効化されること', () => {
      render(<RadioButton label="無効" name="test" value="1" disabled />);
      const radio = screen.getByLabelText('無効');
      expect(radio).toBeDisabled();
    });

    it('disabled時のスタイルが適用されること', () => {
      render(<RadioButton label="無効スタイル" name="test" value="1" disabled />);
      const radio = screen.getByLabelText('無効スタイル');
      expect(radio).toHaveClass(
        'cursor-not-allowed',
        'border-neutral-300',
        'bg-neutral-100',
        'opacity-50'
      );
    });

    it('disabled時のラベルスタイルが適用されること', () => {
      render(<RadioButton label="無効ラベル" name="test" value="1" disabled />);
      const label = screen.getByText('無効ラベル');
      expect(label).toHaveClass('cursor-not-allowed', 'text-neutral-400');
    });
  });

  describe('Props: error', () => {
    it('デフォルトではエラー状態でないこと', () => {
      render(<RadioButton label="正常" name="test" value="1" />);
      const radio = screen.getByLabelText('正常');
      expect(radio).toHaveClass('border-primary-500');
      expect(radio).not.toHaveClass('border-red-500');
    });

    it('error=trueでエラー状態になること', () => {
      render(<RadioButton label="エラー" name="test" value="1" error />);
      const radio = screen.getByLabelText('エラー');
      expect(radio).toHaveClass('border-red-500', 'accent-red-500');
    });

    it('エラー時のラベルスタイルが適用されること', () => {
      render(<RadioButton label="エラーラベル" name="test" value="1" error />);
      const label = screen.getByText('エラーラベル');
      expect(label).toHaveClass('text-red-700');
    });

    it('エラー時のフォーカスリングが赤色になること', () => {
      render(<RadioButton label="エラーフォーカス" name="test" value="1" error />);
      const radio = screen.getByLabelText('エラーフォーカス');
      expect(radio).toHaveClass('focus:ring-red-300');
    });
  });

  describe('Props: description', () => {
    it('descriptionが表示されること', () => {
      render(<RadioButton label="ラベル" name="test" value="1" description="説明文テキスト" />);
      expect(screen.getByText('説明文テキスト')).toBeInTheDocument();
    });

    it('descriptionなしでも動作すること', () => {
      render(<RadioButton label="説明なし" name="test" value="1" />);
      expect(screen.queryByText('説明')).not.toBeInTheDocument();
    });

    it('disabled時のdescriptionスタイルが適用されること', () => {
      render(
        <RadioButton label="ラベル" name="test" value="1" description="無効な説明" disabled />
      );
      const description = screen.getByText('無効な説明');
      expect(description).toHaveClass('text-neutral-300');
    });

    it('error時のdescriptionスタイルが適用されること', () => {
      render(<RadioButton label="ラベル" name="test" value="1" description="エラー説明" error />);
      const description = screen.getByText('エラー説明');
      expect(description).toHaveClass('text-red-600');
    });
  });

  describe('Props: className', () => {
    it('カスタムclassNameが親要素に適用されること', () => {
      render(<RadioButton label="カスタム" name="test" value="1" className="custom-class" />);
      const radio = screen.getByLabelText('カスタム');
      const parentDiv = radio.parentElement?.parentElement;
      expect(parentDiv).toHaveClass('custom-class');
    });

    it('複数のclassNameが適用されること', () => {
      render(<RadioButton label="複数クラス" name="test" value="1" className="class1 class2" />);
      const radio = screen.getByLabelText('複数クラス');
      const parentDiv = radio.parentElement?.parentElement;
      expect(parentDiv).toHaveClass('class1', 'class2');
    });
  });

  describe('イベントハンドラ', () => {
    it('onChangeイベントが発火すること', () => {
      const handleChange = vi.fn();
      render(<RadioButton label="変更イベント" name="test" value="1" onChange={handleChange} />);
      const radio = screen.getByLabelText('変更イベント');

      fireEvent.click(radio);
      expect(handleChange).toHaveBeenCalledTimes(1);
    });

    it('onClickイベントが発火すること', () => {
      const handleClick = vi.fn();
      render(<RadioButton label="クリックイベント" name="test" value="1" onClick={handleClick} />);
      const radio = screen.getByLabelText('クリックイベント');

      fireEvent.click(radio);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('スタイル', () => {
    it('通常時のボーダー色が適用されること', () => {
      render(<RadioButton label="ボーダー" name="test" value="1" />);
      const radio = screen.getByLabelText('ボーダー');
      expect(radio).toHaveClass('border-primary-500');
    });

    it('アクセントカラーが適用されること', () => {
      render(<RadioButton label="アクセント" name="test" value="1" />);
      const radio = screen.getByLabelText('アクセント');
      expect(radio).toHaveClass('accent-primary-500');
    });

    it('ホバー時のボーダー色が設定されていること', () => {
      render(<RadioButton label="ホバー" name="test" value="1" />);
      const radio = screen.getByLabelText('ホバー');
      expect(radio).toHaveClass('hover:border-primary-600');
    });

    it('フォーカス時のリングが設定されていること', () => {
      render(<RadioButton label="フォーカス" name="test" value="1" />);
      const radio = screen.getByLabelText('フォーカス');
      expect(radio).toHaveClass(
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-offset-2',
        'focus:ring-primary-300'
      );
    });

    it('トランジションが設定されていること', () => {
      render(<RadioButton label="トランジション" name="test" value="1" />);
      const radio = screen.getByLabelText('トランジション');
      expect(radio).toHaveClass('transition-all', 'duration-200', 'ease-out');
    });
  });

  describe('複数のPropsの組み合わせ', () => {
    it('error + disabledが同時に適用されること', () => {
      render(<RadioButton label="エラー＋無効" name="test" value="1" error disabled />);
      const radio = screen.getByLabelText('エラー＋無効');
      expect(radio).toBeDisabled();
      expect(radio).toHaveClass('cursor-not-allowed', 'opacity-50');
    });

    it('すべてのPropsが同時に適用されること', () => {
      const handleChange = vi.fn();
      render(
        <RadioButton
          id="full-props"
          label="全Props"
          name="test"
          value="full"
          size="lg"
          description="完全な説明"
          className="custom-full"
          onChange={handleChange}
        />
      );

      const radio = screen.getByLabelText('全Props') as HTMLInputElement;
      expect(radio.id).toBe('full-props');
      expect(radio.name).toBe('test');
      expect(radio.value).toBe('full');
      expect(radio).toHaveClass('w-6', 'h-6');
      expect(screen.getByText('完全な説明')).toBeInTheDocument();

      const parentDiv = radio.parentElement?.parentElement;
      expect(parentDiv).toHaveClass('custom-full');

      fireEvent.click(radio);
      expect(handleChange).toHaveBeenCalled();
    });
  });
});
