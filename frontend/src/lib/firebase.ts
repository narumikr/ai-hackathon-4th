import { initializeApp, getApps, getApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || 'SAMPLE_API_KEY',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'your-app.firebaseapp.com',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'your-project-id',
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || '1:123:web:abcdef',
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || 'your-project-id.appspot.com',
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '1234567890',
}

export function initializeFirebase() {
  if (!getApps().length) {
    initializeApp(firebaseConfig)
  }
  return getApp()
}

// Export auth instance (call initializeFirebase() before using in non-React modules)
initializeFirebase()
export const auth = getAuth()

export default { initializeFirebase, auth }
