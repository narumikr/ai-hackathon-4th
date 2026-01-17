import { fireEvent, render, screen } from '@testing-library/react';

import { Card } from './Card';

describe('Card', () => {
  describe('rendering', () => {
    it('renders children correctly', () => {
      render(<Card>Card content</Card>);

      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('renders as a div element', () => {
      render(<Card data-testid="card">Test</Card>);

      const card = screen.getByTestId('card');
      expect(card.tagName).toBe('DIV');
    });

    it('renders title when provided', () => {
      render(<Card title="Card Title" />);

      expect(screen.getByText('Card Title')).toBeInTheDocument();
    });

    it('renders title as h3 element', () => {
      render(<Card title="Card Title" />);

      const title = screen.getByRole('heading', { level: 3 });
      expect(title).toHaveTextContent('Card Title');
    });

    it('renders description when provided', () => {
      render(<Card description="Card description text" />);

      expect(screen.getByText('Card description text')).toBeInTheDocument();
    });

    it('renders actions when provided', () => {
      render(<Card actions={<button type="button">Action</button>} />);

      expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
    });

    it('renders title, description, and actions together', () => {
      render(
        <Card
          title="Title"
          description="Description"
          actions={<button type="button">Click</button>}
        >
          Content
        </Card>
      );

      expect(screen.getByText('Title')).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Click' })).toBeInTheDocument();
    });
  });

  describe('image', () => {
    it('renders image when provided', () => {
      render(<Card image={{ src: '/test-image.jpg', alt: 'Test image' }} />);

      const image = screen.getByRole('img', { name: 'Test image' });
      expect(image).toBeInTheDocument();
    });

    it('applies correct alt text to image', () => {
      render(<Card image={{ src: '/test-image.jpg', alt: 'Alt text' }} />);

      const image = screen.getByRole('img');
      expect(image).toHaveAttribute('alt', 'Alt text');
    });

    it('does not render image container when image is not provided', () => {
      const { container } = render(<Card>No image</Card>);

      const imageContainer = container.querySelector('.aspect-video');
      expect(imageContainer).not.toBeInTheDocument();
    });
  });

  describe('variants', () => {
    it('applies default variant styles by default', () => {
      render(<Card data-testid="card">Default</Card>);

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'border', 'border-neutral-200');
    });

    it('applies default variant styles when specified', () => {
      render(
        <Card data-testid="card" variant="default">
          Default
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'border-neutral-200');
    });

    it('applies outlined variant styles when specified', () => {
      render(
        <Card data-testid="card" variant="outlined">
          Outlined
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'border-2', 'border-neutral-300');
    });

    it('applies elevated variant styles when specified', () => {
      render(
        <Card data-testid="card" variant="elevated">
          Elevated
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'shadow-lg');
    });
  });

  describe('clickable behavior', () => {
    it('is not clickable by default', () => {
      render(<Card data-testid="card">Not clickable</Card>);

      const card = screen.getByTestId('card');
      expect(card).not.toHaveAttribute('role', 'button');
      expect(card).not.toHaveAttribute('tabIndex');
    });

    it('is clickable when clickable prop is true', () => {
      render(
        <Card data-testid="card" clickable>
          Clickable
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveAttribute('role', 'button');
      expect(card).toHaveAttribute('tabIndex', '0');
    });

    it('is clickable when onClick is provided', () => {
      const handleClick = vi.fn();
      render(
        <Card data-testid="card" onClick={handleClick}>
          Clickable
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveAttribute('role', 'button');
      expect(card).toHaveAttribute('tabIndex', '0');
    });

    it('applies clickable styles when clickable', () => {
      render(
        <Card data-testid="card" clickable>
          Clickable
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('cursor-pointer');
    });

    it('calls onClick when clicked', () => {
      const handleClick = vi.fn();
      render(
        <Card data-testid="card" onClick={handleClick}>
          Click me
        </Card>
      );

      const card = screen.getByTestId('card');
      fireEvent.click(card);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when not clickable and clicked', () => {
      const handleClick = vi.fn();
      render(<Card data-testid="card">Not clickable</Card>);

      const card = screen.getByTestId('card');
      fireEvent.click(card);

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('keyboard navigation', () => {
    it('triggers onClick on Enter key when clickable', () => {
      const handleClick = vi.fn();
      render(
        <Card data-testid="card" onClick={handleClick}>
          Keyboard
        </Card>
      );

      const card = screen.getByTestId('card');
      fireEvent.keyDown(card, { key: 'Enter' });

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('triggers onClick on Space key when clickable', () => {
      const handleClick = vi.fn();
      render(
        <Card data-testid="card" onClick={handleClick}>
          Keyboard
        </Card>
      );

      const card = screen.getByTestId('card');
      fireEvent.keyDown(card, { key: ' ' });

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not trigger onClick on other keys', () => {
      const handleClick = vi.fn();
      render(
        <Card data-testid="card" onClick={handleClick}>
          Keyboard
        </Card>
      );

      const card = screen.getByTestId('card');
      fireEvent.keyDown(card, { key: 'Tab' });

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('className prop', () => {
    it('applies additional className when provided', () => {
      render(
        <Card data-testid="card" className="custom-class">
          Custom
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('custom-class');
    });

    it('combines className with default classes', () => {
      render(
        <Card data-testid="card" variant="elevated" className="custom-class">
          Custom
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'shadow-lg', 'custom-class');
    });
  });

  describe('base styles', () => {
    it('has rounded corners', () => {
      render(<Card data-testid="card">Test</Card>);

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('rounded-xl');
    });

    it('has overflow hidden', () => {
      render(<Card data-testid="card">Test</Card>);

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('overflow-hidden');
    });

    it('has transition styles', () => {
      render(<Card data-testid="card">Test</Card>);

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('transition-all', 'duration-200', 'ease-out');
    });
  });

  describe('HTML attributes', () => {
    it('passes through HTML div attributes', () => {
      render(
        <Card data-testid="test-card" aria-label="Test Card">
          Test
        </Card>
      );

      const card = screen.getByTestId('test-card');
      expect(card).toHaveAttribute('aria-label', 'Test Card');
    });

    it('applies id attribute when provided', () => {
      render(<Card id="my-card">Card</Card>);

      const card = document.getElementById('my-card');
      expect(card).toBeInTheDocument();
    });
  });

  describe('content layout', () => {
    it('renders content in correct order: title, description, children, actions', () => {
      const { container } = render(
        <Card
          title="Title"
          description="Description"
          actions={<button type="button">Action</button>}
        >
          <span data-testid="children-content">Children</span>
        </Card>
      );

      const contentDiv = container.querySelector('.p-4');
      expect(contentDiv).toBeInTheDocument();

      const title = contentDiv?.querySelector('h3');
      const description = contentDiv?.querySelector('p');
      const childrenContent = screen.getByTestId('children-content');
      const actionsDiv = contentDiv?.querySelector('.mt-4');

      expect(title).toHaveTextContent('Title');
      expect(description).toHaveTextContent('Description');
      expect(childrenContent).toHaveTextContent('Children');
      expect(actionsDiv).toContainElement(screen.getByRole('button'));

      // Check order by comparing positions
      const childNodes = Array.from(contentDiv?.childNodes || []);
      const titleIndex = title ? childNodes.indexOf(title) : -1;
      const descriptionIndex = description ? childNodes.indexOf(description) : -1;
      const childrenIndex = childNodes.indexOf(childrenContent);
      const actionsIndex = actionsDiv ? childNodes.indexOf(actionsDiv) : -1;

      expect(titleIndex).toBeLessThan(descriptionIndex);
      expect(descriptionIndex).toBeLessThan(childrenIndex);
      expect(childrenIndex).toBeLessThan(actionsIndex);
    });
  });

  describe('image card use case', () => {
    it('renders as image preview card', () => {
      render(
        <Card
          data-testid="image-card"
          image={{ src: '/photo.jpg', alt: 'Photo' }}
          title="Photo Title"
          description="Photo description"
          clickable
        />
      );

      expect(screen.getByRole('img', { name: 'Photo' })).toBeInTheDocument();
      expect(screen.getByText('Photo Title')).toBeInTheDocument();
      expect(screen.getByText('Photo description')).toBeInTheDocument();
      expect(screen.getByTestId('image-card')).toHaveAttribute('role', 'button');
    });
  });

  describe('text card use case', () => {
    it('renders as text-only card', () => {
      render(
        <Card data-testid="text-card" variant="outlined" title="Info Card">
          <p>This is some informational content.</p>
        </Card>
      );

      expect(screen.getByText('Info Card')).toBeInTheDocument();
      expect(screen.getByText('This is some informational content.')).toBeInTheDocument();
      expect(screen.getByTestId('text-card')).toHaveClass('border-2');
    });
  });

  describe('action card use case', () => {
    it('renders card with action buttons', () => {
      const handleEdit = vi.fn();
      const handleDelete = vi.fn();

      render(
        <Card
          title="Item"
          description="Item description"
          actions={
            <>
              <button type="button" onClick={handleEdit}>
                Edit
              </button>
              <button type="button" onClick={handleDelete}>
                Delete
              </button>
            </>
          }
        />
      );

      fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
      expect(handleEdit).toHaveBeenCalledTimes(1);

      fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
      expect(handleDelete).toHaveBeenCalledTimes(1);
    });
  });

  describe('hover styles for clickable card', () => {
    it('has hover shadow when clickable', () => {
      render(
        <Card data-testid="card" clickable>
          Hover
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('hover:shadow-md');
    });

    it('has hover border color when clickable', () => {
      render(
        <Card data-testid="card" clickable>
          Hover
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('hover:border-primary-300');
    });

    it('has active scale when clickable', () => {
      render(
        <Card data-testid="card" clickable>
          Active
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass('active:scale-[0.98]');
    });

    it('has focus-visible ring when clickable', () => {
      render(
        <Card data-testid="card" clickable>
          Focus
        </Card>
      );

      const card = screen.getByTestId('card');
      expect(card).toHaveClass(
        'focus-visible:ring-2',
        'focus-visible:ring-primary-300',
        'focus-visible:ring-offset-2'
      );
    });
  });
});
