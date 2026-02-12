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

const BRACKET_SOURCE_REGEX = /\s*\[\s*(?:出典|参照):\s*(.+?)\s*\]\s*$/u;
const PAREN_SOURCE_REGEX = /\s*(?:（|\()\s*(?:出典|参照):\s*(.+?)\s*(?:）|\))\s*$/u;
const TRAILING_MARKDOWN_LINK_REGEX = /\s*(\[[^\]]+\]\(https?:\/\/[^)\s]+\))\s*$/u;
const MARKDOWN_LINK_REGEX = /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/u;
const MARKDOWN_LINK_GLOBAL_REGEX = /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/gu;
const STANDALONE_MARKDOWN_LINK_REGEX = /^\[[^\]]+\]\(https?:\/\/[^)\s]+\)$/u;
const STANDALONE_URL_LINE_REGEX = /^\(?https?:\/\/[^)\s]+\)?$/u;
const STANDALONE_BRACKET_LABEL_REGEX = /^\[[^\]]+\]$/u;

function trimUrlSuffix(url: string): string {
  return url.replace(/[.,;:!?。、）】＞]+$/u, '');
}

function parseMarkdownLink(linkText: string): { url: string; label: string } | null {
  const match = linkText.match(MARKDOWN_LINK_REGEX);
  if (!match) {
    return null;
  }
  const url = trimUrlSuffix(match[2]);
  const label = match[1].trim() || url;
  return { url, label };
}

function sanitizeDisplayContent(content: string): string {
  const lines = content
    .split('\n')
    .map(line => line.replace(MARKDOWN_LINK_GLOBAL_REGEX, '').trim());

  while (lines.length > 0) {
    const lastLine = lines[lines.length - 1].trim();

    if (
      STANDALONE_MARKDOWN_LINK_REGEX.test(lastLine) ||
      STANDALONE_URL_LINE_REGEX.test(lastLine) ||
      STANDALONE_BRACKET_LABEL_REGEX.test(lastLine)
    ) {
      lines.pop();
      continue;
    }

    if (lines.length >= 2) {
      const prevLine = lines[lines.length - 2].trim();
      if (
        STANDALONE_BRACKET_LABEL_REGEX.test(prevLine) &&
        STANDALONE_URL_LINE_REGEX.test(lastLine)
      ) {
        lines.pop();
        lines.pop();
        continue;
      }
    }

    break;
  }

  return lines.join('\n').trim();
}

function extractTrailingSource(text: string): { content: string; sourceContent: string | null } {
  const bracketMatch = text.match(BRACKET_SOURCE_REGEX);
  if (bracketMatch) {
    return {
      content: text.replace(BRACKET_SOURCE_REGEX, '').trim(),
      sourceContent: bracketMatch[1].trim(),
    };
  }

  const parenMatch = text.match(PAREN_SOURCE_REGEX);
  if (parenMatch) {
    return {
      content: text.replace(PAREN_SOURCE_REGEX, '').trim(),
      sourceContent: parenMatch[1].trim(),
    };
  }

  const markdownMatch = text.match(TRAILING_MARKDOWN_LINK_REGEX);
  if (markdownMatch) {
    return {
      content: text.replace(TRAILING_MARKDOWN_LINK_REGEX, '').trim(),
      sourceContent: markdownMatch[1].trim(),
    };
  }

  return { content: text, sourceContent: null };
}

function parseSourceContent(sourceContent: string): { url: string | null; label: string | null } {
  const markdownSource = parseMarkdownLink(sourceContent);
  if (markdownSource) {
    return markdownSource;
  }

  const urlMatch = sourceContent.match(/https?:\/\/[^\s)\]}>]+/);
  if (!urlMatch) {
    return { url: null, label: null };
  }

  const extractedUrl = trimUrlSuffix(urlMatch[0]);
  const rawLabel = sourceContent
    .replace(urlMatch[0], '')
    .replace(/^[\s:：()\[\]「」『』（）-]+|[\s:：()\[\]「」『』（）-]+$/g, '')
    .trim();

  return {
    url: extractedUrl,
    label: rawLabel || extractedUrl,
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
  const extracted = extractTrailingSource(text);
  const baseContent = extracted.content;
  let source: { url: string | null; label: string | null };

  if (extracted.sourceContent) {
    source = parseSourceContent(extracted.sourceContent);
  } else {
    const firstMarkdownLink = baseContent.match(MARKDOWN_LINK_REGEX);
    source = firstMarkdownLink
      ? parseSourceContent(firstMarkdownLink[0])
      : { url: null, label: null };
  }

  const content = sanitizeDisplayContent(baseContent);

  return {
    content,
    source,
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
  const extracted = extractTrailingSource(lastLine);

  const contentLines = lines.slice(0, -1);
  const lastLineContent = extracted.content;

  if (lastLineContent) {
    contentLines.push(lastLineContent);
  }

  const baseContent = contentLines.join('\n');
  let source: { url: string | null; label: string | null };

  if (extracted.sourceContent) {
    source = parseSourceContent(extracted.sourceContent);
  } else {
    const firstMarkdownLink = baseContent.match(MARKDOWN_LINK_REGEX);
    source = firstMarkdownLink
      ? parseSourceContent(firstMarkdownLink[0])
      : { url: null, label: null };
  }

  return {
    content: sanitizeDisplayContent(baseContent),
    source,
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
  const extracted = extractTrailingSource(text);
  if (!extracted.sourceContent) {
    return text;
  }

  const sourceContent = extracted.sourceContent;
  const isValidUrl = /^https?:\/\//.test(sourceContent);
  const hasMarkdownUrl = MARKDOWN_LINK_REGEX.test(sourceContent);

  if (isValidUrl || hasMarkdownUrl) {
    return text;
  }

  return extracted.content;
}
