import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { RadioButton } from './RadioButton';

describe('RadioButton', () => {
  it('基本的なレンダリングができること', () => {
    render(<RadioButton label="テストラベル" name="test" value="1" />);
    expect(screen.getByLabelText('テストラベル')).toBeInTheDocument();
  });

  it('ラジオボタンが選択可能であること', () => {
    render(<RadioButton label="選択可能" name="test" value="1" />);
    const radio = screen.getByLabelText('選択可能') as HTMLInputElement;
    expect(radio.checked).toBe(false);
  });

  it('disabledの場合は選択できないこと', () => {
    render(<RadioButton label="無効" name="test" value="1" disabled />);
    const radio = screen.getByLabelText('無効') as HTMLInputElement;
    expect(radio).toBeDisabled();
  });

  it('descriptionが表示されること', () => {
    render(<RadioButton label="ラベル" name="test" value="1" description="説明文" />);
    expect(screen.getByText('説明文')).toBeInTheDocument();
  });

  it('サイズバリエーションが適用されること', () => {
    const { rerender } = render(<RadioButton label="小サイズ" name="test" value="1" size="sm" />);
    let radio = screen.getByLabelText('小サイズ');
    expect(radio).toHaveClass('w-4', 'h-4');

    rerender(<RadioButton label="中サイズ" name="test" value="2" size="md" />);
    radio = screen.getByLabelText('中サイズ');
    expect(radio).toHaveClass('w-5', 'h-5');

    rerender(<RadioButton label="大サイズ" name="test" value="3" size="lg" />);
    radio = screen.getByLabelText('大サイズ');
    expect(radio).toHaveClass('w-6', 'h-6');
  });

  it('エラー状態のスタイルが適用されること', () => {
    render(<RadioButton label="エラー" name="test" value="1" error />);
    const radio = screen.getByLabelText('エラー');
    expect(radio).toHaveClass('border-red-500');
  });

  it('カスタムclassNameが適用されること', () => {
    render(<RadioButton label="カスタム" name="test" value="1" className="custom-class" />);
    const radio = screen.getByLabelText('カスタム');
    const parentDiv = radio.parentElement?.parentElement;
    expect(parentDiv).toHaveClass('custom-class');
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
});
