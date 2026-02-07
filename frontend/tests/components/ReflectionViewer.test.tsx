import { render, screen } from '@testing-library/react';
import { ReflectionViewer } from '@/components/features/reflection/ReflectionViewer';
import type { ReflectionPamphletResponse, TravelPlanResponse } from '@/types';
import { vi } from 'vitest';

vi.mock('next/image', () => ({
  default: ({ src, alt }: { src: string; alt: string }) => <img src={src} alt={alt} />,
}));

describe('ReflectionViewer source rendering', () => {
  it('renders URL sources as links and removes non-URL sources', () => {
    const travel: TravelPlanResponse = {
      id: 'plan-1',
      userId: 'user-1',
      title: '京都歴史探訪',
      destination: '京都',
      spots: [{ id: 'spot-1', name: '清水寺' }],
      status: 'completed',
      guideGenerationStatus: 'succeeded',
      reflectionGenerationStatus: 'succeeded',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-02T00:00:00Z',
      reflection: {
        id: 'reflection-1',
        planId: 'plan-1',
        userId: 'user-1',
        photos: [],
        spotNotes: {},
        createdAt: '2025-01-02T00:00:00Z',
      },
      guide: null,
      pamphlet: null,
    };

    const pamphlet: ReflectionPamphletResponse = {
      travelSummary: '全体の感想です\n[出典: https://example.com/summary]',
      spotReflections: [
        {
          spotName: '清水寺',
          reflection: 'とても良かった\n[出典: 書籍名]',
        },
      ],
      nextTripSuggestions: ['次回は奈良へ\n[出典: https://example.com/next]'],
    };

    render(<ReflectionViewer travel={travel} pamphlet={pamphlet} />);

    expect(screen.getByText('全体の感想です')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'https://example.com/summary' })).toHaveAttribute(
      'href',
      'https://example.com/summary'
    );

    expect(screen.getByText('とても良かった')).toBeInTheDocument();
    expect(screen.queryByText('書籍名')).not.toBeInTheDocument();

    expect(screen.getByRole('link', { name: 'https://example.com/next' })).toHaveAttribute(
      'href',
      'https://example.com/next'
    );
  });
});
