import { render, screen } from '@testing-library/react';

import { List } from './List';

interface TestItem {
  id: number;
  name: string;
}

const testItems: TestItem[] = [
  { id: 1, name: 'Item 1' },
  { id: 2, name: 'Item 2' },
  { id: 3, name: 'Item 3' },
];

const renderTestItem = (item: TestItem) => <span>{item.name}</span>;

describe('List', () => {
  describe('rendering', () => {
    it('renders items correctly', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
      expect(screen.getByText('Item 3')).toBeInTheDocument();
    });

    it('renders as ul element with li children', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const list = screen.getByRole('list');
      expect(list.tagName).toBe('UL');

      const listItems = screen.getAllByRole('listitem');
      expect(listItems).toHaveLength(3);
    });

    it('passes item and index to renderItem function', () => {
      const mockRenderItem = vi.fn((item: TestItem, index: number) => (
        <span data-testid={`item-${index}`}>{item.name}</span>
      ));

      render(<List items={testItems} renderItem={mockRenderItem} />);

      expect(mockRenderItem).toHaveBeenCalledTimes(3);
      expect(mockRenderItem).toHaveBeenCalledWith(testItems[0], 0);
      expect(mockRenderItem).toHaveBeenCalledWith(testItems[1], 1);
      expect(mockRenderItem).toHaveBeenCalledWith(testItems[2], 2);
    });
  });

  describe('empty state', () => {
    it('shows default empty message when items array is empty', () => {
      render(<List items={[]} renderItem={renderTestItem} />);

      expect(screen.getByText('データがありません')).toBeInTheDocument();
    });

    it('shows custom empty message when provided', () => {
      render(<List items={[]} renderItem={renderTestItem} emptyMessage="リストが空です" />);

      expect(screen.getByText('リストが空です')).toBeInTheDocument();
    });

    it('does not render ul element when empty', () => {
      render(<List items={[]} renderItem={renderTestItem} />);

      expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });

    it('empty state has neutral styling', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} />);

      const emptyDiv = container.querySelector('.text-neutral-500');
      expect(emptyDiv).toBeInTheDocument();
    });

    it('empty state has dashed border', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} />);

      const emptyDiv = container.querySelector('.border-dashed');
      expect(emptyDiv).toBeInTheDocument();
    });

    it('empty state has rounded corners', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} />);

      const emptyDiv = container.querySelector('.rounded-lg');
      expect(emptyDiv).toBeInTheDocument();
    });

    it('empty state has background color', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} />);

      const emptyDiv = container.querySelector('.bg-neutral-50');
      expect(emptyDiv).toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('shows loading spinner when loading is true', () => {
      render(<List items={[]} renderItem={renderTestItem} loading />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('shows loading text when loading', () => {
      render(<List items={[]} renderItem={renderTestItem} loading />);

      expect(screen.getByText('読み込み中...')).toBeInTheDocument();
    });

    it('does not render items when loading', () => {
      render(<List items={testItems} renderItem={renderTestItem} loading />);

      expect(screen.queryByText('Item 1')).not.toBeInTheDocument();
      expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });

    it('does not render empty message when loading', () => {
      render(<List items={[]} renderItem={renderTestItem} loading />);

      expect(screen.queryByText('データがありません')).not.toBeInTheDocument();
    });

    it('loading container has primary color styling', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} loading />);

      const loadingContainer = container.querySelector('.bg-primary-50');
      expect(loadingContainer).toBeInTheDocument();
    });

    it('loading container has dashed border with primary color', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} loading />);

      const loadingContainer = container.querySelector('.border-primary-300');
      expect(loadingContainer).toBeInTheDocument();
    });

    it('loading text has primary color', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} loading />);

      const loadingText = container.querySelector('.text-primary-600');
      expect(loadingText).toBeInTheDocument();
    });

    it('loading spinner is large size', () => {
      const { container } = render(<List items={[]} renderItem={renderTestItem} loading />);

      const spinnerWrapper = container.querySelector('div[role="status"]');
      expect(spinnerWrapper).toHaveClass('w-5', 'h-5');
    });
  });

  describe('keyExtractor', () => {
    it('uses index as key by default', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const listItems = screen.getAllByRole('listitem');
      expect(listItems).toHaveLength(3);
    });

    it('uses keyExtractor when provided', () => {
      const keyExtractor = (item: TestItem) => item.id;

      render(<List items={testItems} renderItem={renderTestItem} keyExtractor={keyExtractor} />);

      const listItems = screen.getAllByRole('listitem');
      expect(listItems).toHaveLength(3);
    });

    it('passes item and index to keyExtractor', () => {
      const mockKeyExtractor = vi.fn((item: TestItem, index: number) => `key-${item.id}-${index}`);

      render(
        <List items={testItems} renderItem={renderTestItem} keyExtractor={mockKeyExtractor} />
      );

      expect(mockKeyExtractor).toHaveBeenCalledTimes(3);
      expect(mockKeyExtractor).toHaveBeenCalledWith(testItems[0], 0);
      expect(mockKeyExtractor).toHaveBeenCalledWith(testItems[1], 1);
      expect(mockKeyExtractor).toHaveBeenCalledWith(testItems[2], 2);
    });
  });

  describe('className prop', () => {
    it('applies additional className when provided', () => {
      const { container } = render(
        <List items={testItems} renderItem={renderTestItem} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('combines className with default classes', () => {
      const { container } = render(
        <List items={testItems} renderItem={renderTestItem} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('w-full', 'custom-class');
    });

    it('applies className in empty state', () => {
      const { container } = render(
        <List items={[]} renderItem={renderTestItem} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('applies className in loading state', () => {
      const { container } = render(
        <List items={[]} renderItem={renderTestItem} loading className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('base styles', () => {
    it('has full width by default', () => {
      const { container } = render(<List items={testItems} renderItem={renderTestItem} />);

      expect(container.firstChild).toHaveClass('w-full');
    });
  });

  describe('list item styles', () => {
    it('list items have padding', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const listItems = screen.getAllByRole('listitem');
      listItems.forEach(item => {
        expect(item).toHaveClass('py-3');
      });
    });

    it('first item has no top padding', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const listItems = screen.getAllByRole('listitem');
      expect(listItems[0]).toHaveClass('first:pt-0');
    });

    it('last item has no bottom padding', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const listItems = screen.getAllByRole('listitem');
      expect(listItems[listItems.length - 1]).toHaveClass('last:pb-0');
    });
  });

  describe('list divider styles', () => {
    it('list has divide-y class for vertical dividers', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const list = screen.getByRole('list');
      expect(list).toHaveClass('divide-y');
    });

    it('list has neutral divider color', () => {
      render(<List items={testItems} renderItem={renderTestItem} />);

      const list = screen.getByRole('list');
      expect(list).toHaveClass('divide-neutral-200');
    });
  });

  describe('with different item types', () => {
    it('works with string items', () => {
      const stringItems = ['Apple', 'Banana', 'Cherry'];
      render(<List items={stringItems} renderItem={item => <span>{item}</span>} />);

      expect(screen.getByText('Apple')).toBeInTheDocument();
      expect(screen.getByText('Banana')).toBeInTheDocument();
      expect(screen.getByText('Cherry')).toBeInTheDocument();
    });

    it('works with number items', () => {
      const numberItems = [1, 2, 3];
      render(<List items={numberItems} renderItem={item => <span>Number: {item}</span>} />);

      expect(screen.getByText('Number: 1')).toBeInTheDocument();
      expect(screen.getByText('Number: 2')).toBeInTheDocument();
      expect(screen.getByText('Number: 3')).toBeInTheDocument();
    });

    it('works with complex objects', () => {
      interface ComplexItem {
        id: string;
        title: string;
        description: string;
      }

      const complexItems: ComplexItem[] = [
        { id: 'a', title: 'First', description: 'First description' },
        { id: 'b', title: 'Second', description: 'Second description' },
      ];

      render(
        <List
          items={complexItems}
          renderItem={item => (
            <div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          )}
          keyExtractor={item => item.id}
        />
      );

      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('First description')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
      expect(screen.getByText('Second description')).toBeInTheDocument();
    });
  });

  describe('single item', () => {
    it('renders correctly with single item', () => {
      const singleItem = [{ id: 1, name: 'Only Item' }];

      render(<List items={singleItem} renderItem={renderTestItem} />);

      expect(screen.getByText('Only Item')).toBeInTheDocument();
      expect(screen.getAllByRole('listitem')).toHaveLength(1);
    });
  });

  describe('loading priority', () => {
    it('loading state takes priority over items', () => {
      render(<List items={testItems} renderItem={renderTestItem} loading />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.queryByText('Item 1')).not.toBeInTheDocument();
    });

    it('loading state takes priority over empty message', () => {
      render(<List items={[]} renderItem={renderTestItem} loading emptyMessage="Empty!" />);

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.queryByText('Empty!')).not.toBeInTheDocument();
    });
  });

  describe('render item with complex content', () => {
    it('renders interactive elements in items', () => {
      const handleClick = vi.fn();

      render(
        <List
          items={testItems}
          renderItem={item => (
            <button type="button" onClick={handleClick}>
              {item.name}
            </button>
          )}
        />
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(3);
    });

    it('renders nested lists in items', () => {
      interface NestedItem {
        id: number;
        name: string;
        subItems: string[];
      }

      const nestedItems: NestedItem[] = [
        { id: 1, name: 'Parent', subItems: ['Child 1', 'Child 2'] },
      ];

      render(
        <List
          items={nestedItems}
          renderItem={item => (
            <div>
              <span>{item.name}</span>
              <ul>
                {item.subItems.map(sub => (
                  <li key={sub}>{sub}</li>
                ))}
              </ul>
            </div>
          )}
        />
      );

      expect(screen.getByText('Parent')).toBeInTheDocument();
      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
    });
  });
});
