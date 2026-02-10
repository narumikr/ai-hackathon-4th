import { getApp, getApps, initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const requireEnv = (key: string): string => {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Environment variable ${key} is required but not set.`);
  }
  return value;
};

const firebaseConfig = {
  apiKey: requireEnv('NEXT_PUBLIC_FIREBASE_API_KEY'),
  authDomain: requireEnv('NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN'),
  projectId: requireEnv('NEXT_PUBLIC_FIREBASE_PROJECT_ID'),
  appId: requireEnv('NEXT_PUBLIC_FIREBASE_APP_ID'),
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET ?? '',
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID ?? '',
};

export function initializeFirebase() {
  if (!getApps().length) {
    initializeApp(firebaseConfig);
  }
  return getApp();
}

// Export auth instance (call initializeFirebase() before using in non-React modules)
initializeFirebase();
export const auth = getAuth();

export default { initializeFirebase, auth };
