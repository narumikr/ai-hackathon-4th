'use client';
import { useAuthContext } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import type React from 'react';
import { useState } from 'react';

export default function AuthForm() {
  const { signInEmail, signInGoogle } = useAuthContext();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signInEmail(email, password);
      router.push('/');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'サインインに失敗しました';
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
      const message = err instanceof Error ? err.message : 'Googleサインインに失敗しました';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md rounded bg-white p-6 shadow">
      <h2 className="mb-4 font-semibold text-2xl">ログイン</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="text-red-600">{error}</div>}
        <div>
          <label htmlFor="auth-email" className="block font-medium text-sm">
            メールアドレス
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
            パスワード
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
            {submitting ? '処理中…' : 'メールでサインイン'}
          </button>
          <button
            type="button"
            onClick={handleGoogle}
            className="rounded bg-yellow-500 px-4 py-2 text-black"
            disabled={submitting}
          >
            Google
          </button>
        </div>
      </form>
    </div>
  );
}
