/**
 * 出典情報のパース・処理ユーティリティ
 */

export interface ParsedSource {
  content: string;
  source: {
    url: string | null;
    label: string | null;
  };
}

/**
 * [出典: ...] の形式のテキストをパースする
 * @param text パース対象のテキスト
 * @returns パース済みのオブジェクト（content: 本文, source: 出典情報）
 *
 * @example
 * parseSource("これはテキストです [出典: https://example.com]")
 * // => { content: "これはテキストです", source: { url: "https://example.com", label: "https://example.com" } }
 *
 * @example
 * parseSource("これはテキストです [出典: Wikipedia]")
 * // => { content: "これはテキストです", source: { url: null, label: null } }
 */
export function parseSource(text: string): ParsedSource {
  const sourceRegex = /\s*\[出典:\s*(.+?)\]\s*$/;
  const match = text.match(sourceRegex);

  if (!match) {
    return {
      content: text,
      source: { url: null, label: null },
    };
  }

  const sourceContent = match[1].trim();
  const isValidUrl = /^https?:\/\//.test(sourceContent);

  return {
    content: text.replace(sourceRegex, '').trim(),
    source: {
      url: isValidUrl ? sourceContent : null,
      label: isValidUrl ? sourceContent : null,
    },
  };
}

/**
 * 複数行のテキストから最終行の出典情報をパースする
 * （各行の最後に [出典: ...] がある場合に対応）
 * @param text パース対象のテキスト（複数行可能）
 * @returns パース済みのオブジェクト
 */
export function parseSourceFromMultilineText(text: string): ParsedSource {
  const lines = text.split('\n');
  const lastLine = lines[lines.length - 1];

  const sourceRegex = /\s*\[出典:\s*(.+?)\]\s*$/;
  const match = lastLine.match(sourceRegex);

  if (!match) {
    return {
      content: text,
      source: { url: null, label: null },
    };
  }

  const sourceContent = match[1].trim();
  const isValidUrl = /^https?:\/\//.test(sourceContent);

  const contentLines = lines.slice(0, -1);
  const lastLineContent = lastLine.replace(sourceRegex, '').trim();

  if (lastLineContent) {
    contentLines.push(lastLineContent);
  }

  return {
    content: contentLines.join('\n'),
    source: {
      url: isValidUrl ? sourceContent : null,
      label: isValidUrl ? sourceContent : null,
    },
  };
}

/**
 * 出典なしで [出典: ...] を削除する（URLでない場合）
 * @param text 処理対象のテキスト
 * @returns 出典が削除されたテキスト
 *
 * @example
 * stripSourceIfNotUrl("テキスト [出典: Wikipedia]")
 * // => "テキスト"
 *
 * @example
 * stripSourceIfNotUrl("テキスト [出典: https://example.com]")
 * // => "テキスト [出典: https://example.com]"
 */
export function stripSourceIfNotUrl(text: string): string {
  const sourceRegex = /\s*\[出典:\s*(.+?)\]\s*$/;
  const match = text.match(sourceRegex);

  if (!match) {
    return text;
  }

  const sourceContent = match[1].trim();
  const isValidUrl = /^https?:\/\//.test(sourceContent);

  if (isValidUrl) {
    return text;
  }

  return text.replace(sourceRegex, '').trim();
}
