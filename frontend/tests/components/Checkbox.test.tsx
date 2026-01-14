import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Checkbox } from '@/components/ui/Checkbox';

describe('Checkbox Accessibility', () => {
	it('should have aria-invalid="false" when not in error state', () => {
		render(<Checkbox label="Test checkbox" />);
		const checkbox = screen.getByRole('checkbox');
		expect(checkbox).toHaveAttribute('aria-invalid', 'false');
	});

	it('should have aria-invalid="true" when in error state', () => {
		render(<Checkbox label="Test checkbox" error={true} />);
		const checkbox = screen.getByRole('checkbox');
		expect(checkbox).toHaveAttribute('aria-invalid', 'true');
	});

	it('should have aria-describedby when description is provided', () => {
		render(<Checkbox label="Test checkbox" description="This is a description" />);
		const checkbox = screen.getByRole('checkbox');
		expect(checkbox).toHaveAttribute('aria-describedby');
		
		const describedById = checkbox.getAttribute('aria-describedby');
		const description = screen.getByText('This is a description');
		expect(description).toHaveAttribute('id', describedById);
	});

	it('should have aria-describedby when errorMessage is provided', () => {
		render(<Checkbox label="Test checkbox" error={true} errorMessage="This field is required" />);
		const checkbox = screen.getByRole('checkbox');
		expect(checkbox).toHaveAttribute('aria-describedby');
		
		const describedById = checkbox.getAttribute('aria-describedby');
		const errorMsg = screen.getByText('This field is required');
		expect(errorMsg).toHaveAttribute('id', describedById);
	});

	it('should show errorMessage instead of description when in error state', () => {
		render(
			<Checkbox 
				label="Test checkbox" 
				error={true} 
				description="Normal description" 
				errorMessage="Error message" 
			/>
		);
		
		expect(screen.getByText('Error message')).toBeInTheDocument();
		expect(screen.queryByText('Normal description')).not.toBeInTheDocument();
	});

	it('should have role="alert" on error message', () => {
		render(<Checkbox label="Test checkbox" error={true} errorMessage="This is required" />);
		const errorMsg = screen.getByText('This is required');
		expect(errorMsg).toHaveAttribute('role', 'alert');
	});

	it('should not have role="alert" on normal description', () => {
		render(<Checkbox label="Test checkbox" description="Normal description" />);
		const description = screen.getByText('Normal description');
		expect(description).not.toHaveAttribute('role', 'alert');
	});

	it('should not have aria-describedby when no description or errorMessage', () => {
		render(<Checkbox label="Test checkbox" />);
		const checkbox = screen.getByRole('checkbox');
		expect(checkbox).not.toHaveAttribute('aria-describedby');
	});
});
