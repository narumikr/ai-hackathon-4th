import { parseSource, parseSourceFromMultilineText } from './sourceUtil';

describe('sourceUtil', () => {
  it('出典テキストとURLが併記されている場合はテキストをリンクラベルにする', () => {
    const parsed = parseSource(
      '金閣寺は室町時代の建築です [出典: 京都市観光協会 https://example.com/kinkakuji]'
    );

    expect(parsed.content).toBe('金閣寺は室町時代の建築です');
    expect(parsed.source.url).toBe('https://example.com/kinkakuji');
    expect(parsed.source.label).toBe('京都市観光協会');
  });

  it('出典がURLのみの場合はURLをリンクラベルにする', () => {
    const parsed = parseSource('本文 [出典: https://example.com/source]');

    expect(parsed.content).toBe('本文');
    expect(parsed.source.url).toBe('https://example.com/source');
    expect(parsed.source.label).toBe('https://example.com/source');
  });

  it('出典がURLを含まない場合はリンク情報を返さない', () => {
    const parsed = parseSource('本文 [出典: 京都市史 第2巻]');

    expect(parsed.content).toBe('本文');
    expect(parsed.source.url).toBeNull();
    expect(parsed.source.label).toBeNull();
  });

  it('複数行テキストの最終行出典でもテキストリンクを抽出できる', () => {
    const parsed = parseSourceFromMultilineText(
      '1行目の説明\n2行目の説明\n[出典: 京都市公式サイト（https://example.com/city）]'
    );

    expect(parsed.content).toBe('1行目の説明\n2行目の説明');
    expect(parsed.source.url).toBe('https://example.com/city');
    expect(parsed.source.label).toBe('京都市公式サイト');
  });

  it('丸括弧の出典形式でもURLとラベルを抽出できる', () => {
    const parsed = parseSource('本文です。（出典: 伊勢神宮公式サイト https://example.com/ise）');

    expect(parsed.content).toBe('本文です。');
    expect(parsed.source.url).toBe('https://example.com/ise');
    expect(parsed.source.label).toBe('伊勢神宮公式サイト');
  });

  it('Markdownリンク形式の出典を抽出できる', () => {
    const parsed = parseSource('本文です。 [伊勢神宮公式サイト](https://example.com/ise)');

    expect(parsed.content).toBe('本文です。');
    expect(parsed.source.url).toBe('https://example.com/ise');
    expect(parsed.source.label).toBe('伊勢神宮公式サイト');
  });

  it('出典プレフィックス付きMarkdownリンクを抽出できる', () => {
    const parsed = parseSource('本文です。（出典: [伊勢神宮公式サイト](https://example.com/ise)）');

    expect(parsed.content).toBe('本文です。');
    expect(parsed.source.url).toBe('https://example.com/ise');
    expect(parsed.source.label).toBe('伊勢神宮公式サイト');
  });

  it('本文末尾に残ったMarkdown出典行を除去できる', () => {
    const parsed = parseSourceFromMultilineText(
      '本文です。\n[三内丸山遺跡公式サイト](https://sannaimaruyama.pref.aomori.jp/about/outline/)\n[出典: 三内丸山遺跡公式サイト https://sannaimaruyama.pref.aomori.jp/about/outline/]'
    );

    expect(parsed.content).toBe('本文です。');
    expect(parsed.source.url).toBe('https://sannaimaruyama.pref.aomori.jp/about/outline/');
    expect(parsed.source.label).toBe('三内丸山遺跡公式サイト');
  });

  it('本文末尾の分割URL行を除去できる', () => {
    const parsed = parseSourceFromMultilineText(
      '本文です。\n[文化庁公式サイト]\n(https://www.bunka.go.jp/seisaku/bunkazai/shokai/sekai_isan/list/jomon.html)\n[出典: 文化庁公式サイト https://www.bunka.go.jp/seisaku/bunkazai/shokai/sekai_isan/list/jomon.html]'
    );

    expect(parsed.content).toBe('本文です。');
    expect(parsed.source.url).toBe(
      'https://www.bunka.go.jp/seisaku/bunkazai/shokai/sekai_isan/list/jomon.html'
    );
    expect(parsed.source.label).toBe('文化庁公式サイト');
  });

  it('本文中のMarkdown出典リンクを除去して出典欄へ集約できる', () => {
    const parsed = parseSource(
      '1105年頃に建立されました。[中尊寺公式サイト](https://www.chusonji.or.jp/know/history.html) [出典: 平泉町公式サイト https://www.hiraizumi.or.jp/]'
    );

    expect(parsed.content).toBe('1105年頃に建立されました。');
    expect(parsed.source.url).toBe('https://www.hiraizumi.or.jp/');
    expect(parsed.source.label).toBe('平泉町公式サイト');
  });

  it('出典行がない場合でも本文中のMarkdownリンクを出典として抽出できる', () => {
    const parsed = parseSource(
      '本文です。[中尊寺公式サイト](https://www.chusonji.or.jp/know/history.html)'
    );

    expect(parsed.content).toBe('本文です。');
    expect(parsed.source.url).toBe('https://www.chusonji.or.jp/know/history.html');
    expect(parsed.source.label).toBe('中尊寺公式サイト');
  });
});
