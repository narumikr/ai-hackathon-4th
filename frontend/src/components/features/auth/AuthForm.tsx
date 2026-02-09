'use client'
import React, { useState } from 'react'
import { useAuth } from '../../../hooks/useAuth'

export default function AuthForm() {
  const { user, loading, signInEmail, signInGoogle, signOut } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await signInEmail(email, password)
    } catch (err: any) {
      setError(err?.message || 'サインインに失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  const handleGoogle = async () => {
    setError(null)
    setSubmitting(true)
    try {
      await signInGoogle()
    } catch (err: any) {
      setError(err?.message || 'Googleサインインに失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (err) {
      // ignore
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-semibold mb-4">ログイン</h2>

      {loading ? (
        <div className="text-center py-6">読み込み中…</div>
      ) : user ? (
        <div>
          <p className="mb-2">ログイン中: <strong>{user.email || user.displayName || user.uid}</strong></p>
          <button className="px-4 py-2 bg-red-500 text-white rounded" onClick={handleSignOut}>サインアウト</button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="text-red-600">{error}</div>}
          <div>
            <label className="block text-sm font-medium">メールアドレス</label>
            <input className="mt-1 w-full border rounded px-3 py-2" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-medium">パスワード</label>
            <input className="mt-1 w-full border rounded px-3 py-2" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>

          <div className="flex gap-2">
            <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded" disabled={submitting}>
              {submitting ? '処理中…' : 'メールでサインイン'}
            </button>
            <button type="button" onClick={handleGoogle} className="px-4 py-2 bg-yellow-500 text-black rounded" disabled={submitting}>
              Google
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
