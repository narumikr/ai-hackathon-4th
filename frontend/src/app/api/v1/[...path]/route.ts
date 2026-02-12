import { type NextRequest, NextResponse } from 'next/server';

const BACKEND_SERVICE_URL_ENV = 'BACKEND_SERVICE_URL';
const METADATA_IDENTITY_ENDPOINT =
  'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity';

const HOP_BY_HOP_HEADERS = new Set([
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
]);

const INTERNAL_API_PREFIX = '/api/v1/internal';

const getBackendServiceUrl = (): string => {
  const url = process.env[BACKEND_SERVICE_URL_ENV]?.trim();
  if (!url) {
    throw new Error(`${BACKEND_SERVICE_URL_ENV} is required.`);
  }
  return url;
};

const normalizePathSegments = (path: string[]): string[] => {
  return path
    .map(segment => {
      try {
        return decodeURIComponent(segment);
      } catch {
        throw new Error('Invalid path segment encoding.');
      }
    })
    .map(segment => segment.trim().replace(/^\/+|\/+$/g, ''))
    .filter(Boolean);
};

const buildTargetUrl = (
  backendServiceUrl: string,
  request: NextRequest,
  normalizedPath: string[]
): URL => {
  const base = new URL(backendServiceUrl);
  base.pathname = ['/api/v1', ...normalizedPath].join('/').replace(/\/{2,}/g, '/');
  base.search = request.nextUrl.search;
  return base;
};

const getIdentityToken = async (audience: string): Promise<string> => {
  const metadataUrl = new URL(METADATA_IDENTITY_ENDPOINT);
  metadataUrl.searchParams.set('audience', audience);
  metadataUrl.searchParams.set('format', 'full');

  const response = await fetch(metadataUrl.toString(), {
    headers: {
      'Metadata-Flavor': 'Google',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch identity token from metadata server: ${response.status}.`);
  }

  const token = (await response.text()).trim();
  if (!token) {
    throw new Error('Identity token from metadata server is empty.');
  }
  return token;
};

const sanitizeResponseHeaders = (headers: Headers): Headers => {
  const sanitized = new Headers(headers);
  for (const header of HOP_BY_HOP_HEADERS) {
    sanitized.delete(header);
  }
  return sanitized;
};

export const isInternalApiPath = (normalizedPath: string[]): boolean => {
  if (!Array.isArray(normalizedPath) || normalizedPath.length === 0) {
    return false;
  }
  const firstSegment = normalizedPath[0]?.toLowerCase();
  return firstSegment === 'internal';
};

const proxyRequest = async (request: NextRequest, path: string[]): Promise<NextResponse> => {
  try {
    const normalizedPath = normalizePathSegments(path);
    if (isInternalApiPath(normalizedPath)) {
      return NextResponse.json(
        {
          detail: 'Not Found',
        },
        { status: 404 }
      );
    }

    const backendServiceUrl = getBackendServiceUrl();
    const targetUrl = buildTargetUrl(backendServiceUrl, request, normalizedPath);
    if (
      targetUrl.pathname === INTERNAL_API_PREFIX ||
      targetUrl.pathname.startsWith(`${INTERNAL_API_PREFIX}/`)
    ) {
      return NextResponse.json(
        {
          detail: 'Not Found',
        },
        { status: 404 }
      );
    }

    const forwardHeaders = new Headers(request.headers);
    for (const header of HOP_BY_HOP_HEADERS) {
      forwardHeaders.delete(header);
    }
    forwardHeaders.delete('host');
    forwardHeaders.delete('content-length');

    if (process.env.NODE_ENV === 'production') {
      const originalAuth = forwardHeaders.get('Authorization');
      if (originalAuth) {
        forwardHeaders.set('X-Forwarded-Authorization', originalAuth);
      }

      const audience = new URL(backendServiceUrl).origin;
      const identityToken = await getIdentityToken(audience);
      forwardHeaders.set('Authorization', `Bearer ${identityToken}`);
    }

    const body =
      request.method === 'GET' || request.method === 'HEAD'
        ? undefined
        : await request.arrayBuffer();

    const response = await fetch(targetUrl, {
      method: request.method,
      headers: forwardHeaders,
      body,
      cache: 'no-store',
      redirect: 'manual',
    });

    return new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: sanitizeResponseHeaders(response.headers),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unexpected proxy error.';
    return NextResponse.json(
      {
        detail: message,
      },
      { status: 502 }
    );
  }
};

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await context.params;
  return proxyRequest(request, path);
}
