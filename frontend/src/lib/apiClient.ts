import { auth } from './firebase';

type FetchOptions = Omit<RequestInit, 'headers'> & { headers?: Record<string, string> };

async function getIdToken(): Promise<string | null> {
  if (!auth || !auth.currentUser) return null;
  try {
    return await auth.currentUser.getIdToken();
  } catch (e) {
    return null;
  }
}

export async function apiFetch(input: RequestInfo, init?: FetchOptions) {
  const token = await getIdToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init && init.headers ? init.headers : {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  return fetch(input, { ...init, headers });
}

export default { apiFetch };
