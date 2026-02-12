import '@testing-library/jest-dom';

// テスト環境ではFirebase SDKを使用しないためモックする
const mockAuth = {
  currentUser: null,
  onAuthStateChanged: vi.fn(() => vi.fn()),
};

vi.mock('firebase/app', () => ({
  getApps: vi.fn(() => [{ name: '[DEFAULT]' }]),
  initializeApp: vi.fn(),
  getApp: vi.fn(() => ({})),
}));

vi.mock('firebase/auth', () => ({
  getAuth: vi.fn(() => mockAuth),
  onAuthStateChanged: vi.fn((_auth, callback: (user: null) => void) => {
    callback(null);
    return vi.fn();
  }),
  signInWithEmailAndPassword: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
  signInWithPopup: vi.fn(),
  signOut: vi.fn(),
  GoogleAuthProvider: vi.fn(() => ({
    setCustomParameters: vi.fn(),
  })),
}));

// テスト環境ではAuthGuardをパススルーにし、認証チェックをスキップする
vi.mock('@/components/features/auth/AuthGuard', () => ({
  AuthGuard: ({ children }: { children: React.ReactNode }) => children,
}));

// テスト環境ではAuthContextをモックし、認証済みユーザーを提供する
// 安定した参照を使い、Reactの無限再レンダリングを防ぐ
const mockUser = { uid: 'test-user-001', email: 'test@example.com', displayName: 'テストユーザー' };
const mockAuthContextValue = {
  user: mockUser,
  loading: false,
  signUpEmail: vi.fn(),
  signInEmail: vi.fn(),
  signInGoogle: vi.fn(),
  signOut: vi.fn(),
  getIdToken: vi.fn().mockResolvedValue('mock-id-token'),
};

vi.mock('@/contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuthContext: () => mockAuthContextValue,
}));
