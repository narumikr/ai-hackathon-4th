'use client'
import { useEffect, useState, useCallback } from 'react'
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  GoogleAuthProvider,
  signInWithPopup,
  User as FirebaseUser,
} from 'firebase/auth'
import { auth, initializeFirebase } from '../lib/firebase'

initializeFirebase()

export type User = {
  uid: string
  email?: string | null
  displayName?: string | null
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u: FirebaseUser | null) => {
      if (u) {
        setUser({ uid: u.uid, email: u.email, displayName: u.displayName })
      } else {
        setUser(null)
      }
      setLoading(false)
    })
    return () => unsub()
  }, [])

  const signInEmail = useCallback(async (email: string, password: string) => {
    return signInWithEmailAndPassword(auth, email, password)
  }, [])

  const signInGoogle = useCallback(async () => {
    const provider = new GoogleAuthProvider()
    return signInWithPopup(auth, provider)
  }, [])

  const signOut = useCallback(async () => {
    return firebaseSignOut(auth)
  }, [])

  const getIdToken = useCallback(async (): Promise<string | null> => {
    if (!auth.currentUser) return null
    return auth.currentUser.getIdToken()
  }, [])

  return { user, loading, signInEmail, signInGoogle, signOut, getIdToken }
}
