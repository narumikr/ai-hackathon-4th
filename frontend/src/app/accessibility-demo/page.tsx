'use client';

import { Checkbox } from '@/components/ui/Checkbox';
import { RadioButton } from '@/components/ui/RadioButton';

/**
 * Accessibility Demo for Checkbox and RadioButton Components
 *
 * This page demonstrates the accessibility improvements:
 * - aria-invalid: Indicates error state to screen readers
 * - aria-describedby: Links input to description/error message
 * - role="alert": Announces error messages immediately
 * - errorMessage prop: Provides specific error feedback
 */
export default function AccessibilityDemo() {
  return (
    <div className="mx-auto max-w-4xl space-y-12 p-8">
      <div>
        <h1 className="mb-2 text-3xl font-bold">Accessibility Demo</h1>
        <p className="text-neutral-600">
          Demonstrating accessibility improvements for Checkbox and RadioButton components
        </p>
      </div>

      {/* Checkbox Examples */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold">Checkbox Component</h2>

        <div className="space-y-4 rounded-lg border border-neutral-200 p-6">
          <h3 className="font-semibold">Normal State</h3>
          <Checkbox
            label="I agree to the terms and conditions"
            description="Please read our terms before agreeing"
          />
          <div className="mt-2 rounded bg-neutral-50 p-3 text-sm">
            <strong>Accessibility:</strong> Has aria-invalid="false" and aria-describedby linking to
            description
          </div>
        </div>

        <div className="space-y-4 rounded-lg border border-red-200 bg-red-50 p-6">
          <h3 className="font-semibold">Error State (with errorMessage)</h3>
          <Checkbox
            label="I agree to the terms and conditions"
            description="Please read our terms before agreeing"
            error={true}
            errorMessage="You must agree to the terms to continue"
          />
          <div className="mt-2 rounded bg-white p-3 text-sm">
            <strong>Accessibility:</strong>
            <ul className="ml-4 mt-1 list-disc space-y-1">
              <li>Has aria-invalid="true"</li>
              <li>Has aria-describedby linking to error message</li>
              <li>Error message has role="alert" for immediate announcement</li>
              <li>Error message overrides description when both are present</li>
            </ul>
          </div>
        </div>

        <div className="space-y-4 rounded-lg border border-neutral-200 p-6">
          <h3 className="font-semibold">Disabled State</h3>
          <Checkbox
            label="This option is disabled"
            description="This option is not available"
            disabled={true}
          />
        </div>
      </section>

      {/* RadioButton Examples */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold">RadioButton Component</h2>

        <div className="space-y-4 rounded-lg border border-neutral-200 p-6">
          <h3 className="font-semibold">Normal State</h3>
          <div className="space-y-3">
            <RadioButton
              name="delivery"
              label="Standard Delivery"
              description="Delivery in 3-5 business days"
            />
            <RadioButton
              name="delivery"
              label="Express Delivery"
              description="Delivery in 1-2 business days"
            />
          </div>
          <div className="mt-2 rounded bg-neutral-50 p-3 text-sm">
            <strong>Accessibility:</strong> Each has aria-invalid="false" and aria-describedby
            linking to description
          </div>
        </div>

        <div className="space-y-4 rounded-lg border border-red-200 bg-red-50 p-6">
          <h3 className="font-semibold">Error State (no selection made)</h3>
          <div className="space-y-3">
            <RadioButton
              name="payment"
              label="Credit Card"
              error={true}
              errorMessage="Please select a payment method"
            />
            <RadioButton
              name="payment"
              label="PayPal"
              error={true}
              errorMessage="Please select a payment method"
            />
          </div>
          <div className="mt-2 rounded bg-white p-3 text-sm">
            <strong>Accessibility:</strong>
            <ul className="ml-4 mt-1 list-disc space-y-1">
              <li>Each has aria-invalid="true"</li>
              <li>Each has aria-describedby linking to error message</li>
              <li>Error messages have role="alert"</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Testing Instructions */}
      <section className="rounded-lg border border-blue-200 bg-blue-50 p-6">
        <h2 className="mb-4 text-xl font-bold">Testing with Screen Readers</h2>
        <div className="space-y-3 text-sm">
          <p>To test these accessibility improvements:</p>
          <ol className="ml-4 list-decimal space-y-2">
            <li>
              <strong>On Mac:</strong> Enable VoiceOver (Cmd + F5) and navigate through the form
            </li>
            <li>
              <strong>On Windows:</strong> Use NVDA or JAWS screen reader
            </li>
            <li>
              <strong>What to listen for:</strong>
              <ul className="ml-4 mt-1 list-disc">
                <li>Normal checkboxes announce their label and description</li>
                <li>Error state checkboxes announce "invalid" and the error message</li>
                <li>Error messages are announced immediately with role="alert"</li>
              </ul>
            </li>
          </ol>
        </div>
      </section>
    </div>
  );
}
