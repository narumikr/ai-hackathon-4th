'use client';
import {
  type User as FirebaseUser,
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
} from 'firebase/auth';
import { useCallback, useEffect, useState } from 'react';
import { auth, initializeFirebase } from '../lib/firebase';

initializeFirebase();

export type User = {
  uid: string;
  email?: string | null;
  displayName?: string | null;
};

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u: FirebaseUser | null) => {
      if (u) {
        setUser({ uid: u.uid, email: u.email, displayName: u.displayName });
      } else {
        setUser(null);
      }
      setLoading(false);
    });
    return () => unsub();
  }, []);

  const signUpEmail = useCallback(async (email: string, password: string) => {
    return createUserWithEmailAndPassword(auth, email, password);
  }, []);

  const signInEmail = useCallback(async (email: string, password: string) => {
    return signInWithEmailAndPassword(auth, email, password);
  }, []);

  const signInGoogle = useCallback(async () => {
    const provider = new GoogleAuthProvider();
    return signInWithPopup(auth, provider);
  }, []);

  const signOut = useCallback(async () => {
    return firebaseSignOut(auth);
  }, []);

  const getIdToken = useCallback(async (): Promise<string | null> => {
    if (!auth.currentUser) return null;
    return auth.currentUser.getIdToken();
  }, []);

  return { user, loading, signUpEmail, signInEmail, signInGoogle, signOut, getIdToken };
}
