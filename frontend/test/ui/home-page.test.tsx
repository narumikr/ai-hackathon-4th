import { fireEvent, render, screen, within } from '@testing-library/react';

import HomePage from '@/app/page';
import { APP_DESCRIPTION, APP_NAME, BUTTON_LABELS, HOME_CONTENT } from '@/constants';

describe('HomePage', () => {
  // 1. 基本表示テスト
  describe('基本表示テスト', () => {
    // 1.1 ページタイトルと説明の表示
    describe('ページタイトルと説明の表示 (home-basic-display-001)', () => {
      it('アプリ名「Historical Travel Agent」がh1要素として表示される', () => {
        render(<HomePage />);

        const heading = screen.getByRole('heading', { level: 1, name: APP_NAME });
        expect(heading).toBeInTheDocument();
      });

      it('アプリ説明「歴史学習特化型旅行AIエージェント」が表示される', () => {
        render(<HomePage />);

        expect(screen.getByText(APP_DESCRIPTION)).toBeInTheDocument();
      });

      it('ヒーローサブタイトルが表示される', () => {
        render(<HomePage />);

        expect(
          screen.getByText((content, element) => {
            return (
              element?.tagName.toLowerCase() === 'p' &&
              content.includes('旅行前に歴史的背景を学び')
            );
          })
        ).toBeInTheDocument();
      });
    });

    // 1.2 セクション見出しの表示
    describe('セクション見出しの表示 (home-basic-display-002)', () => {
      it('「主な機能」セクション見出しが表示される', () => {
        render(<HomePage />);

        expect(
          screen.getByRole('heading', { name: HOME_CONTENT.SECTION_TITLES.MAIN_FEATURES })
        ).toBeInTheDocument();
      });

      it('「使い方」セクション見出しが表示される', () => {
        render(<HomePage />);

        expect(
          screen.getByRole('heading', { name: HOME_CONTENT.SECTION_TITLES.HOW_TO_USE })
        ).toBeInTheDocument();
      });

      it('「さあ、歴史を学ぶ旅を始めましょう」セクション見出しが表示される', () => {
        render(<HomePage />);

        expect(
          screen.getByRole('heading', { name: HOME_CONTENT.SECTION_TITLES.CTA })
        ).toBeInTheDocument();
      });
    });
  });

  // 2. ナビゲーション・リンクテスト
  describe('ナビゲーション・リンクテスト', () => {
    // 2.1 メインCTAボタンの表示と機能
    describe('メインCTAボタンの表示と機能 (home-navigation-001)', () => {
      it('「新しい旅行を作成」ボタンが表示される', () => {
        render(<HomePage />);

        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.CREATE_NEW_TRAVEL })
        ).toBeInTheDocument();
      });

      it('「新しい旅行を作成」ボタンが/travel/newへのリンクを持つ', () => {
        render(<HomePage />);

        const link = screen.getByRole('link', { name: BUTTON_LABELS.CREATE_NEW_TRAVEL });
        expect(link).toHaveAttribute('href', '/travel/new');
      });

      it('「旅行一覧を見る」ボタンが表示される', () => {
        render(<HomePage />);

        expect(
          screen.getByRole('button', { name: BUTTON_LABELS.VIEW_TRAVEL_LIST })
        ).toBeInTheDocument();
      });

      it('「旅行一覧を見る」ボタンが/travelへのリンクを持つ', () => {
        render(<HomePage />);

        const link = screen.getByRole('link', { name: BUTTON_LABELS.VIEW_TRAVEL_LIST });
        expect(link).toHaveAttribute('href', '/travel');
      });
    });

    // 2.2 最終CTAボタンの表示と機能
    describe('最終CTAボタンの表示と機能 (home-navigation-002)', () => {
      it('「今すぐ始める」ボタンが表示される', () => {
        render(<HomePage />);

        expect(screen.getByRole('button', { name: BUTTON_LABELS.START_NOW })).toBeInTheDocument();
      });

      it('「今すぐ始める」ボタンが/travel/newへのリンクを持つ', () => {
        render(<HomePage />);

        const ctaSection = screen.getByText(HOME_CONTENT.CTA_SUBTITLE).closest('section');
        expect(ctaSection).not.toBeNull();

        const link = within(ctaSection!).getByRole('link', { name: BUTTON_LABELS.START_NOW });
        expect(link).toHaveAttribute('href', '/travel/new');
      });
    });
  });

  // 3. コンテンツ表示テスト
  describe('コンテンツ表示テスト', () => {
    // 3.1 機能カードの表示
    describe('機能カードの表示 (home-content-001)', () => {
      it('「事前学習ガイド生成」カードが表示される', () => {
        render(<HomePage />);

        const feature = HOME_CONTENT.FEATURES[0];
        expect(screen.getByRole('heading', { name: feature.title })).toBeInTheDocument();
        expect(screen.getByText(feature.description)).toBeInTheDocument();
      });

      it('「歴史年表と地図」カードが表示される', () => {
        render(<HomePage />);

        const feature = HOME_CONTENT.FEATURES[1];
        expect(screen.getByRole('heading', { name: feature.title })).toBeInTheDocument();
        expect(screen.getByText(feature.description)).toBeInTheDocument();
      });

      it('「旅行後の振り返り」カードが表示される', () => {
        render(<HomePage />);

        const feature = HOME_CONTENT.FEATURES[2];
        expect(screen.getByRole('heading', { name: feature.title })).toBeInTheDocument();
        expect(screen.getByText(feature.description)).toBeInTheDocument();
      });

      it('3つの機能カードが全て表示される', () => {
        render(<HomePage />);

        HOME_CONTENT.FEATURES.forEach(feature => {
          expect(screen.getByRole('heading', { name: feature.title })).toBeInTheDocument();
        });
      });

      it('各機能カードに絵文字が表示される', () => {
        render(<HomePage />);

        HOME_CONTENT.FEATURES.forEach(feature => {
          const emojiLabel = screen.getByLabelText(feature.title);
          expect(emojiLabel).toBeInTheDocument();
          expect(emojiLabel).toHaveTextContent(feature.emoji);
        });
      });
    });

    // 3.2 使い方ステップの表示
    describe('使い方ステップの表示 (home-content-002)', () => {
      it('ステップ1「旅行計画を作成」が表示される', () => {
        render(<HomePage />);

        const step = HOME_CONTENT.STEPS[0];
        expect(screen.getByRole('heading', { name: step.title })).toBeInTheDocument();
        expect(screen.getByText(step.description)).toBeInTheDocument();
      });

      it('ステップ2「旅行ガイドを確認」が表示される', () => {
        render(<HomePage />);

        const step = HOME_CONTENT.STEPS[1];
        expect(screen.getByRole('heading', { name: step.title })).toBeInTheDocument();
        expect(screen.getByText(step.description)).toBeInTheDocument();
      });

      it('ステップ3「旅行を楽しむ」が表示される', () => {
        render(<HomePage />);

        const step = HOME_CONTENT.STEPS[2];
        expect(screen.getByRole('heading', { name: step.title })).toBeInTheDocument();
        expect(screen.getByText(step.description)).toBeInTheDocument();
      });

      it('ステップ4「振り返りを作成」が表示される', () => {
        render(<HomePage />);

        const step = HOME_CONTENT.STEPS[3];
        expect(screen.getByRole('heading', { name: step.title })).toBeInTheDocument();
        expect(screen.getByText(step.description)).toBeInTheDocument();
      });

      it('4つのステップが番号付きで表示される', () => {
        render(<HomePage />);

        expect(screen.getByText('1')).toBeInTheDocument();
        expect(screen.getByText('2')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument();
        expect(screen.getByText('4')).toBeInTheDocument();
      });

      it('各ステップにタイトル、説明文が表示される', () => {
        render(<HomePage />);

        HOME_CONTENT.STEPS.forEach(step => {
          expect(screen.getByRole('heading', { name: step.title })).toBeInTheDocument();
          expect(screen.getByText(step.description)).toBeInTheDocument();
        });
      });
    });
  });

  // 4. レスポンシブデザインテスト
  describe('レスポンシブデザインテスト', () => {
    // 4.1 モバイル表示の確認
    describe('モバイル表示の確認 (home-responsive-001)', () => {
      beforeEach(() => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: 375,
        });
        window.dispatchEvent(new Event('resize'));
      });

      it('モバイル幅でページがレンダリングされる', () => {
        render(<HomePage />);

        expect(screen.getByRole('heading', { level: 1, name: APP_NAME })).toBeInTheDocument();
      });

      it('CTAボタンコンテナにflex-colクラスが適用されている', () => {
        const { container } = render(<HomePage />);

        const ctaContainer = container.querySelector('.flex-col');
        expect(ctaContainer).toBeInTheDocument();
      });
    });

    // 4.2 タブレット表示の確認
    describe('タブレット表示の確認 (home-responsive-002)', () => {
      beforeEach(() => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: 768,
        });
        window.dispatchEvent(new Event('resize'));
      });

      it('タブレット幅でページがレンダリングされる', () => {
        render(<HomePage />);

        expect(screen.getByRole('heading', { level: 1, name: APP_NAME })).toBeInTheDocument();
      });
    });

    // 4.3 デスクトップ表示の確認
    describe('デスクトップ表示の確認 (home-responsive-003)', () => {
      beforeEach(() => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: 1024,
        });
        window.dispatchEvent(new Event('resize'));
      });

      it('デスクトップ幅でページがレンダリングされる', () => {
        render(<HomePage />);

        expect(screen.getByRole('heading', { level: 1, name: APP_NAME })).toBeInTheDocument();
      });

      it('機能カードのグリッドにlg:grid-cols-3クラスが適用されている', () => {
        const { container } = render(<HomePage />);

        const grid = container.querySelector('.lg\\:grid-cols-3');
        expect(grid).toBeInTheDocument();
      });
    });
  });

  // 5. アクセシビリティテスト
  describe('アクセシビリティテスト', () => {
    // 5.1 セマンティックHTML構造の確認
    describe('セマンティックHTML構造の確認 (home-accessibility-001)', () => {
      it('h1要素がページに1つだけ存在する', () => {
        render(<HomePage />);

        const h1Elements = screen.getAllByRole('heading', { level: 1 });
        expect(h1Elements).toHaveLength(1);
      });

      it('h2要素が適切な階層で使用されている', () => {
        render(<HomePage />);

        const h2Elements = screen.getAllByRole('heading', { level: 2 });
        expect(h2Elements.length).toBeGreaterThanOrEqual(3);
      });

      it('h3要素が適切な階層で使用されている', () => {
        render(<HomePage />);

        const h3Elements = screen.getAllByRole('heading', { level: 3 });
        expect(h3Elements.length).toBeGreaterThanOrEqual(7);
      });

      it('section要素が適切に使用されている', () => {
        const { container } = render(<HomePage />);

        const sectionElements = container.querySelectorAll('section');
        expect(sectionElements.length).toBeGreaterThanOrEqual(4);
      });
    });

    // 5.2 ARIA属性とアクセシビリティの確認
    describe('ARIA属性とアクセシビリティの確認 (home-accessibility-002)', () => {
      it('絵文字にaria-labelが設定されている', () => {
        render(<HomePage />);

        HOME_CONTENT.FEATURES.forEach(feature => {
          const emoji = screen.getByLabelText(feature.title);
          expect(emoji).toBeInTheDocument();
        });
      });

      it('ボタンにアクセシブルな名前が設定されている', () => {
        render(<HomePage />);

        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          expect(button).toHaveAccessibleName();
        });
      });

      it('リンクにアクセシブルな名前が設定されている', () => {
        render(<HomePage />);

        const links = screen.getAllByRole('link');
        links.forEach(link => {
          expect(link).toHaveAccessibleName();
        });
      });
    });

    // 5.3 キーボードナビゲーションの確認
    describe('キーボードナビゲーションの確認 (home-accessibility-003)', () => {
      it('Tabキーでフォーカス可能な要素を順次移動できる', () => {
        render(<HomePage />);

        const links = screen.getAllByRole('link');
        expect(links.length).toBeGreaterThan(0);

        links[0].focus();
        expect(document.activeElement).toBe(links[0]);

        fireEvent.keyDown(links[0], { key: 'Tab' });
      });

      it('リンク要素がフォーカス可能である', () => {
        render(<HomePage />);

        const links = screen.getAllByRole('link');
        links.forEach(link => {
          expect(link).not.toHaveAttribute('tabindex', '-1');
        });
      });

      it('Enterキーでリンクが有効である', () => {
        render(<HomePage />);

        const link = screen.getByRole('link', { name: BUTTON_LABELS.CREATE_NEW_TRAVEL });
        expect(link).toHaveAttribute('href');
        fireEvent.keyDown(link, { key: 'Enter' });
      });
    });
  });

  // 6. パフォーマンステスト
  describe('パフォーマンステスト', () => {
    // 6.1 初期レンダリング時間の確認
    describe('初期レンダリング時間の確認 (home-performance-001)', () => {
      it('コンポーネントが正常にマウントされる', () => {
        const startTime = performance.now();
        render(<HomePage />);
        const endTime = performance.now();

        expect(endTime - startTime).toBeLessThan(1000);
        expect(screen.getByRole('heading', { level: 1, name: APP_NAME })).toBeInTheDocument();
      });

      it('全ての主要要素がレンダリングされる', () => {
        render(<HomePage />);

        expect(screen.getByRole('heading', { level: 1, name: APP_NAME })).toBeInTheDocument();
        expect(screen.getAllByRole('heading', { level: 2 }).length).toBeGreaterThanOrEqual(3);
        expect(screen.getAllByRole('heading', { level: 3 }).length).toBeGreaterThanOrEqual(7);
        expect(screen.getAllByRole('link').length).toBeGreaterThanOrEqual(3);
      });
    });
  });

  // 7. エラーハンドリングテスト
  describe('エラーハンドリングテスト', () => {
    // 7.1 定数データの欠損時の動作確認
    describe('定数データの欠損時の動作確認 (home-error-001)', () => {
      it('機能データが存在する場合、全ての機能カードが表示される', () => {
        render(<HomePage />);

        expect(HOME_CONTENT.FEATURES.length).toBe(3);
        HOME_CONTENT.FEATURES.forEach(feature => {
          expect(screen.getByRole('heading', { name: feature.title })).toBeInTheDocument();
        });
      });

      it('ステップデータが存在する場合、全てのステップが表示される', () => {
        render(<HomePage />);

        expect(HOME_CONTENT.STEPS.length).toBe(4);
        HOME_CONTENT.STEPS.forEach(step => {
          expect(screen.getByRole('heading', { name: step.title })).toBeInTheDocument();
        });
      });

      it('必要な定数が全て定義されている', () => {
        expect(APP_NAME).toBeDefined();
        expect(APP_DESCRIPTION).toBeDefined();
        expect(HOME_CONTENT).toBeDefined();
        expect(HOME_CONTENT.HERO_SUBTITLE).toBeDefined();
        expect(HOME_CONTENT.CTA_SUBTITLE).toBeDefined();
        expect(HOME_CONTENT.SECTION_TITLES).toBeDefined();
        expect(HOME_CONTENT.FEATURES).toBeDefined();
        expect(HOME_CONTENT.STEPS).toBeDefined();
        expect(BUTTON_LABELS).toBeDefined();
        expect(BUTTON_LABELS.CREATE_NEW_TRAVEL).toBeDefined();
        expect(BUTTON_LABELS.VIEW_TRAVEL_LIST).toBeDefined();
        expect(BUTTON_LABELS.START_NOW).toBeDefined();
      });
    });
  });
});
