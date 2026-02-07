import Image from 'next/image';

/**
 * 利用可能なアイコン名
 */
export const iconNames = [
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
] as const;

export type IconName = (typeof iconNames)[number];

/**
 * アイコンサイズ
 */
export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

const sizeMap: Record<IconSize, number> = {
  xs: 16,
  sm: 20,
  md: 24,
  lg: 32,
  xl: 48,
};

interface IconProps {
  /** アイコン名 */
  name: IconName;
  /** アイコンサイズ（デフォルト: md） */
  size?: IconSize;
  /** アクセシビリティ用のラベル */
  label?: string;
  /** 装飾用アイコンとして扱う（alt=""、aria-hidden="true"を設定） */
  decorative?: boolean;
  /** 追加のCSSクラス */
  className?: string;
}

/**
 * Icon Component
 * publicフォルダのアイコン画像を表示する共通コンポーネント
 */
export function Icon({ name, size = 'md', label, decorative = false, className = '' }: IconProps) {
  const pixelSize = sizeMap[size];

  if (decorative) {
    return (
      <Image
        src={`/icons/${name}.png`}
        alt=""
        width={pixelSize}
        height={pixelSize}
        unoptimized
        className={className}
        aria-hidden="true"
      />
    );
  }

  if (!label) {
    throw new Error('Icon component requires "label" prop when not decorative');
  }

  return (
    <Image
      src={`/icons/${name}.png`}
      alt={label}
      width={pixelSize}
      height={pixelSize}
      unoptimized
      className={className}
    />
  );
}
