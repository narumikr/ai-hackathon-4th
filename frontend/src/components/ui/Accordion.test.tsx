import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Accordion } from './Accordion';

describe('Accordion', () => {
  const mockItems = [
    {
      id: '1',
      title: 'アイテム1',
      content: <p>コンテンツ1</p>,
    },
    {
      id: '2',
      title: 'アイテム2',
      content: <p>コンテンツ2</p>,
    },
    {
      id: '3',
      title: 'アイテム3',
      content: <p>コンテンツ3</p>,
    },
  ];

  it('基本的なレンダリングができること', () => {
    render(<Accordion items={mockItems} />);
    expect(screen.getByText('アイテム1')).toBeInTheDocument();
    expect(screen.getByText('アイテム2')).toBeInTheDocument();
    expect(screen.getByText('アイテム3')).toBeInTheDocument();
  });

  it('アイテムをクリックすると開閉できること', () => {
    render(<Accordion items={mockItems} />);

    const button1 = screen.getByText('アイテム1');
    fireEvent.click(button1);

    // コンテンツが表示される
    const content1 = screen.getByText('コンテンツ1');
    expect(content1).toBeVisible();
  });

  it('単一モードでは1つだけ開くこと', () => {
    render(<Accordion items={mockItems} multiple={false} />);

    const button1 = screen.getByText('アイテム1');
    const button2 = screen.getByText('アイテム2');

    fireEvent.click(button1);
    expect(screen.getByText('コンテンツ1')).toBeVisible();

    fireEvent.click(button2);
    expect(screen.getByText('コンテンツ2')).toBeVisible();

    // アイテム1が閉じることを確認（max-h-0とopacity-0クラスを持つ）
    const content1Container = screen.getByText('コンテンツ1').parentElement?.parentElement;
    expect(content1Container).toHaveClass('max-h-0', 'opacity-0');
  });

  it('複数モードでは複数開くことができること', () => {
    render(<Accordion items={mockItems} multiple={true} />);

    const button1 = screen.getByText('アイテム1');
    const button2 = screen.getByText('アイテム2');

    fireEvent.click(button1);
    fireEvent.click(button2);

    expect(screen.getByText('コンテンツ1')).toBeVisible();
    expect(screen.getByText('コンテンツ2')).toBeVisible();
  });

  it('defaultOpenで初期状態を指定できること', () => {
    render(<Accordion items={mockItems} defaultOpen={['1', '2']} multiple={true} />);

    expect(screen.getByText('コンテンツ1')).toBeVisible();
    expect(screen.getByText('コンテンツ2')).toBeVisible();
  });

  it('開いているアイテムを再度クリックすると閉じること', () => {
    render(<Accordion items={mockItems} />);

    const button1 = screen.getByText('アイテム1');

    fireEvent.click(button1);
    expect(screen.getByText('コンテンツ1')).toBeVisible();

    fireEvent.click(button1);
    const content1Container = screen.getByText('コンテンツ1').parentElement?.parentElement;
    expect(content1Container).toHaveClass('max-h-0', 'opacity-0');
  });

  it('カスタムclassNameが適用されること', () => {
    const { container } = render(<Accordion items={mockItems} className="custom-class" />);
    const accordion = container.querySelector('.custom-class');
    expect(accordion).toBeInTheDocument();
  });

  describe('アクセシビリティ属性', () => {
    it('aria-expanded属性が閉じている状態ではfalseになること', () => {
      render(<Accordion items={mockItems} />);

      const button1 = screen.getByRole('button', { name: 'アイテム1' });
      expect(button1).toHaveAttribute('aria-expanded', 'false');
    });

    it('aria-expanded属性が開いている状態ではtrueになること', () => {
      render(<Accordion items={mockItems} />);

      const button1 = screen.getByRole('button', { name: 'アイテム1' });
      fireEvent.click(button1);

      expect(button1).toHaveAttribute('aria-expanded', 'true');
    });

    it('aria-controls属性が適切なコンテンツ領域を指していること', () => {
      render(<Accordion items={mockItems} />);

      const button1 = screen.getByRole('button', { name: 'アイテム1' });
      const ariaControls = button1.getAttribute('aria-controls');

      expect(ariaControls).toBe('accordion-content-1');

      // コンテンツ領域が存在することを確認
      const contentRegion = document.getElementById('accordion-content-1');
      expect(contentRegion).toBeInTheDocument();
    });

    it('コンテンツ領域にrole="region"が設定されていること', () => {
      render(<Accordion items={mockItems} />);

      const contentRegion = document.getElementById('accordion-content-1');
      // <section>要素は暗黙的にregionロールを持つ
      expect(contentRegion?.tagName).toBe('SECTION');
    });

    it('コンテンツ領域にaria-labelledby属性が設定されていること', () => {
      render(<Accordion items={mockItems} />);

      const contentRegion = document.getElementById('accordion-content-1');
      expect(contentRegion).toHaveAttribute('aria-labelledby', 'accordion-button-1');

      // ボタンが存在することを確認
      const button = document.getElementById('accordion-button-1');
      expect(button).toBeInTheDocument();
    });

    it('複数のアイテムでそれぞれ正しいaria属性が設定されていること', () => {
      render(<Accordion items={mockItems} />);

      mockItems.forEach(item => {
        const button = screen.getByRole('button', { name: item.title });
        const contentRegion = document.getElementById(`accordion-content-${item.id}`);

        expect(button).toHaveAttribute('aria-expanded', 'false');
        expect(button).toHaveAttribute('aria-controls', `accordion-content-${item.id}`);
        expect(button).toHaveAttribute('id', `accordion-button-${item.id}`);
        // <section>要素は暗黙的にregionロールを持つ
        expect(contentRegion?.tagName).toBe('SECTION');
        expect(contentRegion).toHaveAttribute('aria-labelledby', `accordion-button-${item.id}`);
      });
    });
  });
});
