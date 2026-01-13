import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Checkbox } from './Checkbox';

describe('Checkbox', () => {
  it('基本的なレンダリングができること', () => {
    render(<Checkbox label="テストラベル" />);
    expect(screen.getByLabelText('テストラベル')).toBeInTheDocument();
  });

  it('チェックボックスがチェック可能であること', () => {
    render(<Checkbox label="チェック可能" />);
    const checkbox = screen.getByLabelText('チェック可能') as HTMLInputElement;
    expect(checkbox.checked).toBe(false);
  });

  it('disabledの場合はチェックできないこと', () => {
    render(<Checkbox label="無効" disabled />);
    const checkbox = screen.getByLabelText('無効') as HTMLInputElement;
    expect(checkbox).toBeDisabled();
  });

  it('descriptionが表示されること', () => {
    render(<Checkbox label="ラベル" description="説明文" />);
    expect(screen.getByText('説明文')).toBeInTheDocument();
  });

  it('サイズバリエーションが適用されること', () => {
    const { rerender } = render(<Checkbox label="小サイズ" size="sm" />);
    let checkbox = screen.getByLabelText('小サイズ');
    expect(checkbox).toHaveClass('w-4', 'h-4');

    rerender(<Checkbox label="中サイズ" size="md" />);
    checkbox = screen.getByLabelText('中サイズ');
    expect(checkbox).toHaveClass('w-5', 'h-5');

    rerender(<Checkbox label="大サイズ" size="lg" />);
    checkbox = screen.getByLabelText('大サイズ');
    expect(checkbox).toHaveClass('w-6', 'h-6');
  });

  it('エラー状態のスタイルが適用されること', () => {
    render(<Checkbox label="エラー" error />);
    const checkbox = screen.getByLabelText('エラー');
    expect(checkbox).toHaveClass('border-red-500');
  });

  it('カスタムclassNameが適用されること', () => {
    render(<Checkbox label="カスタム" className="custom-class" />);
    const checkbox = screen.getByLabelText('カスタム');
    const parentDiv = checkbox.parentElement?.parentElement;
    expect(parentDiv).toHaveClass('custom-class');
  });
});
