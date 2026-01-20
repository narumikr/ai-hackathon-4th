import { render, screen } from '@testing-library/react';

import { EMOJI_LABELS, FORM_LABELS, LABELS, SECTION_TITLES } from '@/constants';
import type { ReflectionContent } from '@/data/sampleReflections';
import type { SampleTravel } from '@/data/sampleTravels';
import { ReflectionViewer } from './ReflectionViewer';

describe('ReflectionViewer', () => {
  const createMockTravel = (overrides?: Partial<SampleTravel>): SampleTravel => ({
    id: '1',
    title: '京都の歴史探訪',
    destination: '京都',
    status: 'completed',
    spotsCount: 3,
    createdAt: '2024-03-15',
    completedAt: '2024年3月17日',
    hasReflection: true,
    photosCount: 5,
    ...overrides,
  });

  const createMockReflection = (overrides?: Partial<ReflectionContent>): ReflectionContent => ({
    travelId: '1',
    overallComment: '京都の歴史を深く学ぶことができました。',
    photos: [
      { id: 1, comment: '清水寺の本堂から京都市街を望む絶景' },
      { id: 2, comment: '金閣寺の黄金に輝く姿は圧巻でした' },
    ],
    ...overrides,
  });

  describe('rendering', () => {
    it('renders travel title', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(travel.title)).toBeInTheDocument();
    });

    it('renders travel destination', () => {
      const travel = createMockTravel({ destination: '奈良' });
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(/奈良/)).toBeInTheDocument();
    });

    it('renders completed date', () => {
      const travel = createMockTravel({ completedAt: '2024年4月20日' });
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(new RegExp(LABELS.COMPLETED_DATE))).toBeInTheDocument();
      expect(screen.getByText(/2024年4月20日/)).toBeInTheDocument();
    });

    it('renders spot memories section title', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(SECTION_TITLES.SPOT_MEMORIES)).toBeInTheDocument();
    });

    it('renders overall impression section title', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(FORM_LABELS.OVERALL_IMPRESSION_PLAIN)).toBeInTheDocument();
    });

    it('renders overall comment', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        overallComment: '素晴らしい体験でした。',
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText('素晴らしい体験でした。')).toBeInTheDocument();
    });
  });

  describe('photo display', () => {
    it('renders all photo comments', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [
          { id: 1, comment: 'コメント1' },
          { id: 2, comment: 'コメント2' },
          { id: 3, comment: 'コメント3' },
        ],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText('コメント1')).toBeInTheDocument();
      expect(screen.getByText('コメント2')).toBeInTheDocument();
      expect(screen.getByText('コメント3')).toBeInTheDocument();
    });

    it('renders photo placeholders for each photo', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [
          { id: 1, comment: 'Comment for first photo' },
          { id: 2, comment: 'Comment for second photo' },
        ],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Each photo has a placeholder with "Photo {id}" text
      expect(screen.getByText('Photo 1')).toBeInTheDocument();
      expect(screen.getByText('Photo 2')).toBeInTheDocument();
    });

    it('renders memory scene titles for each photo', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [
          { id: 1, comment: 'First memory' },
          { id: 2, comment: 'Second memory' },
        ],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(SECTION_TITLES.MEMORY_SCENE(1))).toBeInTheDocument();
      expect(screen.getByText(SECTION_TITLES.MEMORY_SCENE(2))).toBeInTheDocument();
    });

    it('handles empty photos array', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({ photos: [] });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Should still render the section title
      expect(screen.getByText(SECTION_TITLES.SPOT_MEMORIES)).toBeInTheDocument();
      // But no photo items
      expect(screen.queryByText(/Photo \d+/)).not.toBeInTheDocument();
    });

    it('handles single photo', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: '唯一の写真コメント' }],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText('唯一の写真コメント')).toBeInTheDocument();
      expect(screen.getByText(SECTION_TITLES.MEMORY_SCENE(1))).toBeInTheDocument();
    });

    it('handles many photos', () => {
      const travel = createMockTravel();
      const photos = Array.from({ length: 10 }, (_, i) => ({
        id: i + 1,
        comment: `写真 ${i + 1} のコメント`,
      }));
      const reflection = createMockReflection({ photos });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      photos.forEach((_photo, index) => {
        expect(screen.getByText(`写真 ${index + 1} のコメント`)).toBeInTheDocument();
      });
    });
  });

  describe('emojis', () => {
    it('renders pin emoji for destination', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Check for emoji with the pin label
      const emojiElements = container.querySelectorAll(`[aria-label="${EMOJI_LABELS.PIN}"]`);
      expect(emojiElements.length).toBeGreaterThan(0);
    });

    it('renders checkmark emoji for completion', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Check for emoji with the checkmark label
      const emojiElements = container.querySelectorAll(`[aria-label="${EMOJI_LABELS.CHECKMARK}"]`);
      expect(emojiElements.length).toBeGreaterThan(0);
    });

    it('renders picture emoji for photo placeholders', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: 'Test comment' }],
      });

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Check for emoji with the picture label
      const emojiElements = container.querySelectorAll(`[aria-label="${EMOJI_LABELS.PICTURE}"]`);
      expect(emojiElements.length).toBeGreaterThan(0);
    });
  });

  describe('base styles', () => {
    it('has proper travel overview container styles', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const overviewContainer = container.querySelector('.border-primary-200');
      expect(overviewContainer).toHaveClass('rounded-lg', 'bg-primary-50', 'p-6');
    });

    it('has proper title heading styles', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const title = screen.getByText(travel.title);
      expect(title.tagName).toBe('H2');
      expect(title).toHaveClass('font-bold', 'text-2xl');
    });

    it('has proper section heading styles', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const sectionHeading = screen.getByText(SECTION_TITLES.SPOT_MEMORIES);
      expect(sectionHeading.tagName).toBe('H3');
      expect(sectionHeading).toHaveClass('font-bold', 'text-xl', 'border-b');
    });

    it('photo cards have proper styles', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: 'Test comment' }],
      });

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const photoCard = container.querySelector('.border-neutral-200.bg-white.shadow-sm');
      expect(photoCard).toHaveClass('rounded-lg', 'p-6');
    });

    it('overall comment section has proper styles', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Find the overall comment section (last section with shadow-sm)
      const sections = container.querySelectorAll('.shadow-sm');
      const overallSection = sections[sections.length - 1];
      expect(overallSection).toHaveClass('rounded-lg', 'border', 'bg-white', 'p-6');
    });
  });

  describe('text formatting', () => {
    it('preserves whitespace in photo comments', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: '一行目\n二行目\n三行目' }],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const comment = screen.getByText(/一行目/);
      expect(comment).toHaveClass('whitespace-pre-wrap');
    });

    it('preserves whitespace in overall comment', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        overallComment: '段落1\n\n段落2\n\n段落3',
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const comment = screen.getByText(/段落1/);
      expect(comment).toHaveClass('whitespace-pre-wrap');
    });
  });

  describe('responsive design', () => {
    it('photo layout has responsive flex classes', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: 'Test' }],
      });

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // The photo card content should have responsive flex direction
      const flexContainer = container.querySelector('.flex-col.md\\:flex-row');
      expect(flexContainer).toBeInTheDocument();
    });
  });

  describe('edge cases', () => {
    it('handles empty overall comment', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({ overallComment: '' });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // Section title should still be visible
      expect(screen.getByText(FORM_LABELS.OVERALL_IMPRESSION_PLAIN)).toBeInTheDocument();
    });

    it('handles very long travel title', () => {
      const longTitle =
        '歴史と文化を巡る日本の古都京都・奈良の文化財と伝統工芸体験を含む充実の3日間の旅';
      const travel = createMockTravel({ title: longTitle });
      const reflection = createMockReflection();

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('handles very long photo comments', () => {
      const longComment =
        '清水寺の本堂から見える京都市街の景色は本当に素晴らしく、春の桜、夏の新緑、秋の紅葉、冬の雪景色と四季折々の美しさを楽しむことができます。特に今回訪れた時期は新緑の季節で、目に鮮やかな緑が広がっていました。';
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: longComment }],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(longComment)).toBeInTheDocument();
    });

    it('handles very long overall comment', () => {
      const longComment =
        '今回の京都旅行を通じて、日本の歴史と文化の深さを改めて実感しました。訪れた各寺社では、それぞれに独自の歴史があり、建築様式や庭園のデザインからも当時の人々の美意識や価値観を感じ取ることができました。また、地元の方々との交流を通じて、伝統文化が現代にも息づいていることを知り、文化の継承の大切さについて考えさせられました。';
      const travel = createMockTravel();
      const reflection = createMockReflection({ overallComment: longComment });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(longComment)).toBeInTheDocument();
    });

    it('handles special characters in comments', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: '素晴らしい！感動的！！！😊🎌🏯' }],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      expect(screen.getByText(/素晴らしい！感動的！！！/)).toBeInTheDocument();
    });
  });

  describe('layout structure', () => {
    it('has space-y-8 for main sections', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection();

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const mainContainer = container.querySelector('.space-y-8');
      expect(mainContainer).toBeInTheDocument();
    });

    it('photo list has space-y-8', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [
          { id: 1, comment: 'Comment 1' },
          { id: 2, comment: 'Comment 2' },
        ],
      });

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      const photoList = container.querySelectorAll('.space-y-8');
      expect(photoList.length).toBeGreaterThan(0);
    });
  });

  describe('accessibility', () => {
    it('uses semantic heading hierarchy', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: 'Test' }],
      });

      render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // H2 for travel title
      const h2 = screen.getByRole('heading', { level: 2 });
      expect(h2).toHaveTextContent(travel.title);

      // H3 for sections
      const h3Elements = screen.getAllByRole('heading', { level: 3 });
      expect(h3Elements.length).toBeGreaterThan(0);

      // H4 for individual memories
      const h4Elements = screen.getAllByRole('heading', { level: 4 });
      expect(h4Elements.length).toBeGreaterThan(0);
    });

    it('emoji elements have proper aria-label', () => {
      const travel = createMockTravel();
      const reflection = createMockReflection({
        photos: [{ id: 1, comment: 'Test' }],
      });

      const { container } = render(<ReflectionViewer travel={travel} reflection={reflection} />);

      // All emoji elements should have role="img"
      const emojiElements = container.querySelectorAll('[role="img"]');
      expect(emojiElements.length).toBeGreaterThan(0);

      // All should have aria-label
      emojiElements.forEach(emoji => {
        expect(emoji).toHaveAttribute('aria-label');
      });
    });
  });
});
