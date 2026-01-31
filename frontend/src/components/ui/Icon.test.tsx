import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Icon, iconNames, type IconName, type IconSize } from './Icon';

describe('Icon', () => {
  it('デフォルトサイズ(md)でアイコンを表示する', () => {
    render(<Icon name="calendar" />);
    const img = screen.getByRole('img', { name: 'calendar' });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('width', '24');
    expect(img).toHaveAttribute('height', '24');
  });

  it('カスタムラベルを設定できる', () => {
    render(<Icon name="pin" label="場所" />);
    const img = screen.getByRole('img', { name: '場所' });
    expect(img).toBeInTheDocument();
  });

  it.each<IconSize>(['xs', 'sm', 'md', 'lg', 'xl'])(
    'サイズ %s でアイコンを表示する',
    (size) => {
      const expectedSizes: Record<IconSize, number> = {
        xs: 16,
        sm: 20,
        md: 24,
        lg: 32,
        xl: 48,
      };
      render(<Icon name="check" size={size} />);
      const img = screen.getByRole('img', { name: 'check' });
      expect(img).toHaveAttribute('width', String(expectedSizes[size]));
      expect(img).toHaveAttribute('height', String(expectedSizes[size]));
    }
  );

  it('カスタムクラス名を適用できる', () => {
    render(<Icon name="user" className="custom-class" />);
    const img = screen.getByRole('img', { name: 'user' });
    expect(img).toHaveClass('custom-class');
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

  it('正しいsrc属性を持つ', () => {
    render(<Icon name="map" />);
    const img = screen.getByRole('img', { name: 'map' });
    expect(img).toHaveAttribute('src', expect.stringContaining('map.png'));
  });
});
