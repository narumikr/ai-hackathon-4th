import { render, screen } from '@testing-library/react';

import HomePage from './page';

describe('HomePage', () => {
  it('renders the title and description', () => {
    render(<HomePage />);

    expect(screen.getByRole('heading', { name: 'Historical Travel Agent' })).toBeInTheDocument();
    expect(screen.getByText('歴史学習特化型旅行AIエージェント')).toBeInTheDocument();
  });
});
