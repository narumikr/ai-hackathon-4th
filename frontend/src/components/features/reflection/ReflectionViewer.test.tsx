import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import { EMOJI_LABELS, FORM_LABELS, LABELS, SECTION_TITLES } from '@/constants';
import type { ReflectionPamphletResponse, TravelPlanResponse } from '@/types';
import { ReflectionViewer } from './ReflectionViewer';

// next/imageをモック
vi.mock('next/image', () => ({
  default: (props: { src: string; alt: string }) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={props.src} alt={props.alt} />;
  },
}));

describe('ReflectionViewer', () => {
  const createMockTravel = (overrides?: Partial<TravelPlanResponse>): TravelPlanResponse => ({
    id: '1',
    userId: 'user-1',
    title: '京都の歴史探訪',
    destination: '京都',
    spots: [
      { id: 'spot-1', name: '清水寺', description: '有名な寺院' },
      { id: 'spot-2', name: '金閣寺', description: '黄金の寺院' },
    ],
    status: 'completed',
    guideGenerationStatus: 'succeeded',
    reflectionGenerationStatus: 'succeeded',
    createdAt: '2024-03-15T00:00:00Z',
    updatedAt: '2024-03-17T00:00:00Z',
    reflection: {
      id: 'reflection-1',
      planId: '1',
      userId: 'user-1',
      photos: [],
      spotNotes: {},
      createdAt: '2024-03-17T00:00:00Z',
    },
    ...overrides,
  });

  const createMockPamphlet = (
    overrides?: Partial<ReflectionPamphletResponse>
  ): ReflectionPamphletResponse => ({
    travelSummary: '京都の歴史を深く学ぶことができました。',
    spotReflections: [
      { spotName: '清水寺', reflection: '清水寺の本堂から京都市街を望む絶景でした。' },
      { spotName: '金閣寺', reflection: '金閣寺の黄金に輝く姿は圧巻でした。' },
    ],
    nextTripSuggestions: ['奈良の東大寺を訪れる', '姫路城を見学する'],
    ...overrides,
  });

  describe('rendering', () => {
    it('renders travel title', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(travel.title)).toBeInTheDocument();
    });

    it('renders travel destination', () => {
      const travel = createMockTravel({ destination: '奈良' });
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(/奈良/)).toBeInTheDocument();
    });

    it('renders completed date', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(new RegExp(LABELS.COMPLETED_DATE))).toBeInTheDocument();
    });

    it('renders spot memories section title', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(SECTION_TITLES.SPOT_MEMORIES)).toBeInTheDocument();
    });

    it('renders overall impression section title', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(FORM_LABELS.OVERALL_IMPRESSION_PLAIN)).toBeInTheDocument();
    });

    it('renders travel summary', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        travelSummary: '素晴らしい体験でした。',
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText('素晴らしい体験でした。')).toBeInTheDocument();
    });
  });

  describe('spot reflections display', () => {
    it('renders all spot reflections', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [
          { spotName: 'スポット1', reflection: '振り返り1' },
          { spotName: 'スポット2', reflection: '振り返り2' },
          { spotName: 'スポット3', reflection: '振り返り3' },
        ],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText('振り返り1')).toBeInTheDocument();
      expect(screen.getByText('振り返り2')).toBeInTheDocument();
      expect(screen.getByText('振り返り3')).toBeInTheDocument();
    });

    it('renders spot names', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [
          { spotName: '清水寺', reflection: '振り返り内容' },
          { spotName: '金閣寺', reflection: '振り返り内容' },
        ],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(/清水寺/)).toBeInTheDocument();
      expect(screen.getByText(/金閣寺/)).toBeInTheDocument();
    });

    it('handles empty spot reflections array', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({ spotReflections: [] });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      // Should still render the section title
      expect(screen.getByText(SECTION_TITLES.SPOT_MEMORIES)).toBeInTheDocument();
    });

    it('handles single spot reflection', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: '唯一のスポット', reflection: '唯一の振り返り' }],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText('唯一の振り返り')).toBeInTheDocument();
    });
  });

  describe('next trip suggestions', () => {
    it('renders next trip suggestions when available', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        nextTripSuggestions: ['提案1', '提案2', '提案3'],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(/提案1/)).toBeInTheDocument();
      expect(screen.getByText(/提案2/)).toBeInTheDocument();
      expect(screen.getByText(/提案3/)).toBeInTheDocument();
    });

    it('does not render next trip section when suggestions are empty', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        nextTripSuggestions: [],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.queryByText(/次の旅行の提案/)).not.toBeInTheDocument();
    });
  });

  describe('emojis', () => {
    it('renders pin emoji for destination', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const emojiElements = container.querySelectorAll(`[aria-label="${EMOJI_LABELS.PIN}"]`);
      expect(emojiElements.length).toBeGreaterThan(0);
    });

    it('renders checkmark emoji for completion', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const emojiElements = container.querySelectorAll(`[aria-label="${EMOJI_LABELS.CHECKMARK}"]`);
      expect(emojiElements.length).toBeGreaterThan(0);
    });

    it('renders airplane emoji for next trip suggestions', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        nextTripSuggestions: ['提案1'],
      });

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const emojiElements = container.querySelectorAll(`[aria-label="${EMOJI_LABELS.AIRPLANE}"]`);
      expect(emojiElements.length).toBeGreaterThan(0);
    });
  });

  describe('base styles', () => {
    it('has proper travel overview container styles', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const overviewContainer = container.querySelector('.border-primary-200');
      expect(overviewContainer).toHaveClass('rounded-lg', 'bg-primary-50', 'p-6');
    });

    it('has proper title heading styles', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const title = screen.getByText(travel.title);
      expect(title.tagName).toBe('H2');
      expect(title).toHaveClass('font-bold', 'text-2xl');
    });

    it('has proper section heading styles', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const sectionHeading = screen.getByText(SECTION_TITLES.SPOT_MEMORIES);
      expect(sectionHeading.tagName).toBe('H3');
      expect(sectionHeading).toHaveClass('font-bold', 'text-xl', 'border-b');
    });

    it('spot cards have proper styles', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: 'テストスポット', reflection: 'テスト振り返り' }],
      });

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const spotCard = container.querySelector('.border-neutral-200.bg-white.shadow-sm');
      expect(spotCard).toHaveClass('rounded-lg', 'p-6');
    });
  });

  describe('text formatting', () => {
    it('preserves whitespace in spot reflections', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: 'スポット', reflection: '一行目\n二行目\n三行目' }],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const reflection = screen.getByText(/一行目/);
      expect(reflection).toHaveClass('whitespace-pre-wrap');
    });

    it('preserves whitespace in travel summary', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        travelSummary: '段落1\n\n段落2\n\n段落3',
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const summary = screen.getByText(/段落1/);
      expect(summary).toHaveClass('whitespace-pre-wrap');
    });
  });

  describe('edge cases', () => {
    it('handles empty travel summary', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({ travelSummary: '' });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(FORM_LABELS.OVERALL_IMPRESSION_PLAIN)).toBeInTheDocument();
    });

    it('handles very long travel title', () => {
      const longTitle =
        '歴史と文化を巡る日本の古都京都・奈良の文化財と伝統工芸体験を含む充実の3日間の旅';
      const travel = createMockTravel({ title: longTitle });
      const pamphlet = createMockPamphlet();

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('handles very long spot reflections', () => {
      const longReflection =
        '清水寺の本堂から見える京都市街の景色は本当に素晴らしく、春の桜、夏の新緑、秋の紅葉、冬の雪景色と四季折々の美しさを楽しむことができます。特に今回訪れた時期は新緑の季節で、目に鮮やかな緑が広がっていました。';
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: 'スポット', reflection: longReflection }],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(longReflection)).toBeInTheDocument();
    });

    it('handles very long travel summary', () => {
      const longSummary =
        '今回の京都旅行を通じて、日本の歴史と文化の深さを改めて実感しました。訪れた各寺社では、それぞれに独自の歴史があり、建築様式や庭園のデザインからも当時の人々の美意識や価値観を感じ取ることができました。';
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({ travelSummary: longSummary });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(longSummary)).toBeInTheDocument();
    });

    it('handles special characters in reflections', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: 'スポット', reflection: '素晴らしい！感動的！！！' }],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      expect(screen.getByText(/素晴らしい！感動的！！！/)).toBeInTheDocument();
    });
  });

  describe('layout structure', () => {
    it('has space-y-8 for main sections', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet();

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const mainContainer = container.querySelector('.space-y-8');
      expect(mainContainer).toBeInTheDocument();
    });

    it('spot list has space-y-8', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [
          { spotName: 'スポット1', reflection: '振り返り1' },
          { spotName: 'スポット2', reflection: '振り返り2' },
        ],
      });

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const spotList = container.querySelectorAll('.space-y-8');
      expect(spotList.length).toBeGreaterThan(0);
    });
  });

  describe('accessibility', () => {
    it('uses semantic heading hierarchy', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: 'テストスポット', reflection: 'テスト' }],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      // H2 for travel title
      const h2 = screen.getByRole('heading', { level: 2 });
      expect(h2).toHaveTextContent(travel.title);

      // H3 for sections
      const h3Elements = screen.getAllByRole('heading', { level: 3 });
      expect(h3Elements.length).toBeGreaterThan(0);

      // H4 for individual spot reflections
      const h4Elements = screen.getAllByRole('heading', { level: 4 });
      expect(h4Elements.length).toBeGreaterThan(0);
    });

    it('emoji elements have proper aria-label', () => {
      const travel = createMockTravel();
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: 'テストスポット', reflection: 'テスト' }],
      });

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const emojiElements = container.querySelectorAll('[role="img"]');
      expect(emojiElements.length).toBeGreaterThan(0);

      emojiElements.forEach(emoji => {
        expect(emoji).toHaveAttribute('aria-label');
      });
    });
  });

  describe('photo display', () => {
    it('renders photos when available', () => {
      const travel = createMockTravel({
        spots: [{ id: 'spot-1', name: '清水寺', description: '' }],
        reflection: {
          id: 'reflection-1',
          planId: '1',
          userId: 'user-1',
          photos: [
            {
              id: 'photo-1',
              spotId: 'spot-1',
              url: 'https://example.com/photo1.jpg',
              analysis: '写真の分析',
              userDescription: '清水寺の写真',
            },
          ],
          spotNotes: {},
          createdAt: '2024-03-17T00:00:00Z',
        },
      });
      const pamphlet = createMockPamphlet({
        spotReflections: [{ spotName: '清水寺', reflection: '振り返り' }],
      });

      render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const image = screen.getByAltText('清水寺の写真');
      expect(image).toBeInTheDocument();
    });

    it('does not render photo section when no photos', () => {
      const travel = createMockTravel({
        reflection: {
          id: 'reflection-1',
          planId: '1',
          userId: 'user-1',
          photos: [],
          spotNotes: {},
          createdAt: '2024-03-17T00:00:00Z',
        },
      });
      const pamphlet = createMockPamphlet();

      const { container } = render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

      const photoGrid = container.querySelector('.grid.grid-cols-2');
      expect(photoGrid).not.toBeInTheDocument();
    });
  });
});
