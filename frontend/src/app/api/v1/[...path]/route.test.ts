import { NextRequest } from 'next/server';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { GET, isInternalApiPath } from './route';

describe('isInternalApiPath', () => {
  it('returns true when first path segment is internal', () => {
    expect(isInternalApiPath(['internal', 'tasks', 'spot-image'])).toBe(true);
  });

  it('returns false for empty path', () => {
    expect(isInternalApiPath([])).toBe(false);
  });

  it('returns false for non-internal public api path', () => {
    expect(isInternalApiPath(['travel-plans'])).toBe(false);
  });
});

describe('api proxy route', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it('returns 404 and does not proxy internal path', async () => {
    vi.stubEnv('BACKEND_SERVICE_URL', 'https://backend.example.com');
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const request = new NextRequest('http://localhost/api/v1/internal/tasks/spot-image');

    const response = await GET(request, {
      params: Promise.resolve({ path: ['internal', 'tasks', 'spot-image'] }),
    });

    expect(response.status).toBe(404);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('returns 404 when first path segment starts with slash', async () => {
    vi.stubEnv('BACKEND_SERVICE_URL', 'https://backend.example.com');
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const request = new NextRequest('http://localhost/api/v1/%2Finternal/tasks/spot-image');

    const response = await GET(request, {
      params: Promise.resolve({ path: ['/internal', 'tasks', 'spot-image'] }),
    });

    expect(response.status).toBe(404);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('returns 404 when first path segment is encoded internal path', async () => {
    vi.stubEnv('BACKEND_SERVICE_URL', 'https://backend.example.com');
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const request = new NextRequest('http://localhost/api/v1/%252Finternal/tasks/spot-image');

    const response = await GET(request, {
      params: Promise.resolve({ path: ['%2Finternal', 'tasks', 'spot-image'] }),
    });

    expect(response.status).toBe(404);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('returns 404 when first path segment has leading spaces', async () => {
    vi.stubEnv('BACKEND_SERVICE_URL', 'https://backend.example.com');
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const request = new NextRequest('http://localhost/api/v1/internal/tasks/spot-image');

    const response = await GET(request, {
      params: Promise.resolve({ path: ['  internal', 'tasks', 'spot-image'] }),
    });

    expect(response.status).toBe(404);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('returns 502 and does not proxy when path segment encoding is invalid', async () => {
    vi.stubEnv('BACKEND_SERVICE_URL', 'https://backend.example.com');
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const request = new NextRequest('http://localhost/api/v1/travel-plans');

    const response = await GET(request, {
      params: Promise.resolve({ path: ['%E0%A4%A'] }),
    });

    expect(response.status).toBe(502);
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('proxies public API path to backend service', async () => {
    vi.stubEnv('BACKEND_SERVICE_URL', 'https://backend.example.com');
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      })
    );
    const request = new NextRequest('http://localhost/api/v1/travel-plans?user_id=u1');

    const response = await GET(request, {
      params: Promise.resolve({ path: ['travel-plans'] }),
    });

    expect(response.status).toBe(200);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.objectContaining({
        href: 'https://backend.example.com/api/v1/travel-plans?user_id=u1',
      }),
      expect.objectContaining({
        method: 'GET',
      })
    );
  });
});
