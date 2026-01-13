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
});
