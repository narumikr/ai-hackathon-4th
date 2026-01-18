interface EmojiProps {
  symbol: string;
  label: string;
  className?: string;
}

/**
 * Emoji Component
 * アクセシビリティ対応の絵文字表示コンポーネント
 */
export function Emoji({ symbol, label, className = '' }: EmojiProps) {
  return (
    <span role="img" aria-label={label} className={className}>
      {symbol}
    </span>
  );
}
