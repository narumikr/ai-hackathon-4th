'use client';
import {
  BUTTON_LABELS,
  ERROR_DIALOG_MESSAGES,
  FORM_LABELS,
  MESSAGES,
  PAGE_TITLES,
} from '@/constants';
import { useAuthContext } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import type React from 'react';
import { useState } from 'react';

export default function AuthForm() {
  const { signUpEmail, signInEmail, signInGoogle } = useAuthContext();
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (isSignUp) {
        await signUpEmail(email, password);
      } else {
        await signInEmail(email, password);
      }
      router.push('/');
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : isSignUp
            ? ERROR_DIALOG_MESSAGES.SIGN_UP_FAILED
            : ERROR_DIALOG_MESSAGES.SIGN_IN_FAILED;
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleGoogle = async () => {
    setError(null);
    setSubmitting(true);
    try {
      await signInGoogle();
      router.push('/');
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : ERROR_DIALOG_MESSAGES.SIGN_IN_GOOGLE_FAILED;
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const toggleMode = () => {
    setIsSignUp(prev => !prev);
    setError(null);
  };

  return (
    <div className="mx-auto max-w-md rounded bg-white p-6 shadow">
      <h2 className="mb-4 font-semibold text-2xl">
        {isSignUp ? PAGE_TITLES.SIGN_UP : PAGE_TITLES.SIGN_IN}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <div>
          <label htmlFor="auth-email" className="block font-medium text-sm">
            {FORM_LABELS.EMAIL}
          </label>
          <input
            id="auth-email"
            className="mt-1 w-full rounded border px-3 py-2"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="auth-password" className="block font-medium text-sm">
            {FORM_LABELS.PASSWORD}
          </label>
          <input
            id="auth-password"
            className="mt-1 w-full rounded border px-3 py-2"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            className="flex-1 rounded bg-blue-600 px-4 py-2 text-white"
            disabled={submitting}
          >
            {submitting
              ? `${MESSAGES.PROCESSING}…`
              : isSignUp
                ? BUTTON_LABELS.SIGN_UP_EMAIL
                : BUTTON_LABELS.SIGN_IN_EMAIL}
          </button>
          <button
            type="button"
            onClick={handleGoogle}
            className="rounded bg-yellow-500 px-4 py-2 text-black"
            disabled={submitting}
          >
            {BUTTON_LABELS.SIGN_IN_GOOGLE}
          </button>
        </div>
      </form>

      <div className="mt-4 text-center text-sm">
        <button type="button" onClick={toggleMode} className="text-blue-600 hover:underline">
          {isSignUp ? MESSAGES.SWITCH_TO_SIGN_IN : MESSAGES.SWITCH_TO_SIGN_UP}
        </button>
      </div>
    </div>
  );
}
