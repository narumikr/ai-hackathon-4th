import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Icon, type IconName, type IconSize, iconNames } from './Icon';

describe('Icon', () => {
  it('デフォルトサイズ(md)でアイコンを表示する', () => {
    render(<Icon name="calendar" label="カレンダー" />);
    const img = screen.getByRole('img', { name: 'カレンダー' });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('width', '24');
    expect(img).toHaveAttribute('height', '24');
  });

  it('カスタムラベルを設定できる', () => {
    render(<Icon name="pin" label="場所" />);
    const img = screen.getByRole('img', { name: '場所' });
    expect(img).toBeInTheDocument();
  });

  it.each<IconSize>(['xs', 'sm', 'md', 'lg', 'xl'])('サイズ %s でアイコンを表示する', size => {
    const expectedSizes: Record<IconSize, number> = {
      xs: 16,
      sm: 20,
      md: 24,
      lg: 32,
      xl: 48,
    };
    render(<Icon name="check" label="チェック" size={size} />);
    const img = screen.getByRole('img', { name: 'チェック' });
    expect(img).toHaveAttribute('width', String(expectedSizes[size]));
    expect(img).toHaveAttribute('height', String(expectedSizes[size]));
  });

  it('カスタムクラス名を適用できる', () => {
    render(<Icon name="user" label="ユーザー" className="custom-class" />);
    const img = screen.getByRole('img', { name: 'ユーザー' });
    expect(img).toHaveClass('custom-class');
  });

  it('装飾用アイコンとして表示できる', () => {
    const { container } = render(<Icon name="calendar" decorative />);
    const img = container.querySelector('img');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('alt', '');
    expect(img).toHaveAttribute('aria-hidden', 'true');
  });

  it('labelが未指定かつdecorativeがfalseの場合はエラーになる', () => {
    expect(() => render(<Icon name="calendar" />)).toThrow(
      'Icon component requires "label" prop when not decorative'
    );
  });

  it('全てのアイコン名が定義されている', () => {
    const expectedIcons: IconName[] = [
      'calendar',
      'check',
      'hint',
      'image',
      'map',
      'museum',
      'note',
      'photo',
      'pin',
      'study',
      'upload',
      'user',
      'write',
    ];
    expect(iconNames).toEqual(expectedIcons);
  });

  it('src属性が設定されている', () => {
    render(<Icon name="map" label="地図" />);
    const img = screen.getByRole('img', { name: '地図' });
    expect(img).toHaveAttribute('src');
    expect(img).toHaveAttribute('alt', '地図');
  });
});
