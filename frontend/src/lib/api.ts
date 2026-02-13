import type { GenerateTravelGuideRequest } from '@/types/guide';
import type { CreateReflectionRequest } from '@/types/reflection';
import type {
  CreateTravelPlanRequest,
  TravelPlanListResponse,
  TravelPlanResponse,
  UpdateTravelPlanRequest,
} from '@/types/travel';

import { auth } from './firebase';

export type ApiErrorDetail = string | Record<string, unknown> | null;

export class ApiError extends Error {
  readonly status: number | null;
  readonly statusText: string | null;
  readonly detail: ApiErrorDetail | undefined;
  readonly url: string | undefined;
  readonly method: string | undefined;

  constructor(
    message: string,
    options: {
      status?: number | null;
      statusText?: string | null;
      detail?: ApiErrorDetail;
      url?: string;
      method?: string;
    } = {}
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = options.status ?? null;
    this.statusText = options.statusText ?? null;
    this.detail = options.detail;
    this.url = options.url;
    this.method = options.method;
  }
}

export const toApiError = (error: unknown): ApiError => {
  if (error instanceof ApiError) {
    return error;
  }
  if (error instanceof Error) {
    return new ApiError(error.message, { detail: { reason: error.name } });
  }
  return new ApiError('Unexpected error occurred.', { detail: { error } });
};

type QueryValue = string | number | boolean;

type RequestOptions<TBody> = {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  query?: Record<string, QueryValue | null | undefined>;
  body?: TBody;
  signal?: AbortSignal;
  responseType?: 'json' | 'void';
  headers?: HeadersInit;
};

type ApiClientConfig = {
  baseUrl: string;
  prefix?: string;
  fetcher?: typeof fetch;
};

export type SpotReflectionUploadRequest = {
  planId: string;
  spotId: string;
  spotNote?: string;
  files: File[];
  signal?: AbortSignal;
};

export type ApiClient = {
  listTravelPlans: (params: {
    signal?: AbortSignal;
  }) => Promise<TravelPlanListResponse[]>;
  getTravelPlan: (params: {
    planId: string;
    signal?: AbortSignal;
  }) => Promise<TravelPlanResponse>;
  createTravelPlan: (params: {
    request: CreateTravelPlanRequest;
    signal?: AbortSignal;
  }) => Promise<TravelPlanResponse>;
  updateTravelPlan: (params: {
    planId: string;
    request: UpdateTravelPlanRequest;
    signal?: AbortSignal;
  }) => Promise<TravelPlanResponse>;
  deleteTravelPlan: (params: { planId: string; signal?: AbortSignal }) => Promise<void>;
  generateTravelGuide: (params: {
    request: GenerateTravelGuideRequest;
    signal?: AbortSignal;
  }) => Promise<TravelPlanResponse>;
  createReflection: (params: {
    request: CreateReflectionRequest;
    signal?: AbortSignal;
  }) => Promise<void>;
  uploadSpotReflection: (params: SpotReflectionUploadRequest) => Promise<void>;
};

const DEFAULT_API_PREFIX = '/api/v1';

const normalizeBaseUrl = (value: string): string => {
  const trimmed = value.trim();
  if (!trimmed) {
    throw new ApiError('API base URL is required.');
  }
  if (trimmed.startsWith('/')) {
    const normalized = trimmed.replace(/\/+$/, '');
    return normalized === '' ? '/' : normalized;
  }
  let parsed: URL;
  try {
    parsed = new URL(trimmed);
  } catch (error) {
    throw new ApiError('API base URL must be a valid absolute URL or start with "/".', {
      detail: { value: trimmed, error: String(error) },
    });
  }
  parsed.pathname = parsed.pathname.replace(/\/+$/, '');
  return parsed.toString();
};

const normalizePath = (value: string): string => value.replace(/^\/+|\/+$/g, '');

const joinPath = (...parts: string[]): string => {
  const normalized = parts.map(part => normalizePath(part)).filter(Boolean);
  return `/${normalized.join('/')}`;
};

const buildUrl = (
  baseUrl: string,
  prefix: string,
  path: string,
  query?: Record<string, QueryValue | null | undefined>
): string => {
  const queryParams = new URLSearchParams();
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) {
        continue;
      }
      queryParams.set(key, String(value));
    }
  }
  const queryString = queryParams.toString();

  if (baseUrl.startsWith('/')) {
    const pathname = joinPath(baseUrl, prefix, path);
    return queryString ? `${pathname}?${queryString}` : pathname;
  }

  const url = new URL(baseUrl);
  url.pathname = joinPath(url.pathname, prefix, path);
  if (queryString) {
    url.search = queryString;
  }
  return url.toString();
};

const assertNonEmpty = (value: string, fieldName: string): string => {
  if (!value || !value.trim()) {
    throw new ApiError(`${fieldName} is required and must not be empty.`);
  }
  return value.trim();
};

const assertNonEmptyFiles = (files: File[]): void => {
  if (!Array.isArray(files) || files.length === 0) {
    throw new ApiError('files is required and must be a non-empty array.');
  }
};

const parseJsonResponse = async (response: Response): Promise<unknown> => {
  const contentType = response.headers.get('content-type') ?? '';
  if (!contentType.includes('application/json')) {
    throw new ApiError('Expected JSON response but received a different content type.', {
      status: response.status,
      statusText: response.statusText,
      detail: { contentType },
    });
  }
  try {
    return await response.json();
  } catch (error) {
    throw new ApiError('Failed to parse JSON response.', {
      status: response.status,
      statusText: response.statusText,
      detail: { error: String(error) },
    });
  }
};

type ParsedErrorResponse = {
  message: string | null;
  detail: ApiErrorDetail;
};

const parseErrorResponse = async (response: Response): Promise<ParsedErrorResponse> => {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const payload = (await response.json()) as Record<string, unknown>;
      // Backend format: { error: { type, message, ... } }
      const errorObj = payload?.error as Record<string, unknown> | undefined;
      if (errorObj && typeof errorObj.message === 'string') {
        return { message: errorObj.message, detail: errorObj as ApiErrorDetail };
      }
      // Legacy format: { detail: ... }
      if (payload && typeof payload === 'object' && 'detail' in payload) {
        const detail = payload.detail as ApiErrorDetail;
        return {
          message: typeof detail === 'string' ? detail : null,
          detail: detail ?? (payload as ApiErrorDetail),
        };
      }
      return { message: null, detail: payload as ApiErrorDetail };
    } catch (error) {
      return { message: null, detail: { parseError: String(error) } };
    }
  }
  try {
    const text = await response.text();
    return { message: text || null, detail: text ? text : null };
  } catch (error) {
    return { message: null, detail: { parseError: String(error) } };
  }
};

const getRequiredEnv = (): string => {
  const value = process.env.NEXT_PUBLIC_API_URL;
  if (!value) {
    throw new ApiError('NEXT_PUBLIC_API_URL is required for API requests.');
  }
  return value;
};

export const createApiClient = (config: ApiClientConfig): ApiClient => {
  const baseUrl = normalizeBaseUrl(config.baseUrl);
  const prefix = config.prefix ?? DEFAULT_API_PREFIX;
  const fetcher = config.fetcher ?? fetch;

  const request = async <TResponse, TBody = undefined>(
    options: RequestOptions<TBody>
  ): Promise<TResponse> => {
    const url = buildUrl(baseUrl, prefix, options.path, options.query);
    const headers = new Headers(options.headers);
    let body: BodyInit | undefined;

    if (options.body !== undefined) {
      if (options.body instanceof FormData) {
        body = options.body;
      } else {
        headers.set('Content-Type', 'application/json');
        body = JSON.stringify(options.body);
      }
    }

    const response = await fetcher(url, {
      method: options.method,
      headers,
      body,
      signal: options.signal,
    });

    if (!response.ok) {
      const { message, detail } = await parseErrorResponse(response);
      throw new ApiError(message || `Request failed with status ${response.status}.`, {
        status: response.status,
        statusText: response.statusText,
        detail,
        url,
        method: options.method,
      });
    }

    if (options.responseType === 'void') {
      return undefined as TResponse;
    }

    const data = await parseJsonResponse(response);
    return data as TResponse;
  };

  return {
    listTravelPlans: async ({ signal }) => {
      return request<TravelPlanListResponse[]>({
        method: 'GET',
        path: '/travel-plans',
        signal,
      });
    },
    getTravelPlan: async ({ planId, signal }) => {
      assertNonEmpty(planId, 'planId');
      return request<TravelPlanResponse>({
        method: 'GET',
        path: `/travel-plans/${planId}`,
        signal,
      });
    },
    createTravelPlan: async ({ request: payload, signal }) => {
      assertNonEmpty(payload.title, 'title');
      assertNonEmpty(payload.destination, 'destination');
      return request<TravelPlanResponse, CreateTravelPlanRequest>({
        method: 'POST',
        path: '/travel-plans',
        body: payload,
        signal,
      });
    },
    updateTravelPlan: async ({ planId, request: payload, signal }) => {
      assertNonEmpty(planId, 'planId');
      return request<TravelPlanResponse, UpdateTravelPlanRequest>({
        method: 'PUT',
        path: `/travel-plans/${planId}`,
        body: payload,
        signal,
      });
    },
    deleteTravelPlan: async ({ planId, signal }) => {
      assertNonEmpty(planId, 'planId');
      return request<void>({
        method: 'DELETE',
        path: `/travel-plans/${planId}`,
        signal,
        responseType: 'void',
      });
    },
    generateTravelGuide: async ({ request: payload, signal }) => {
      assertNonEmpty(payload.planId, 'planId');
      return request<TravelPlanResponse, GenerateTravelGuideRequest>({
        method: 'POST',
        path: '/travel-guides',
        body: payload,
        signal,
      });
    },
    createReflection: async ({ request: payload, signal }) => {
      assertNonEmpty(payload.planId, 'planId');
      if (payload.userNotes !== undefined && payload.userNotes !== null) {
        assertNonEmpty(payload.userNotes, 'userNotes');
      }
      return request<void, CreateReflectionRequest>({
        method: 'POST',
        path: '/reflections',
        body: payload,
        signal,
        responseType: 'void',
      });
    },
    uploadSpotReflection: async ({ planId, spotId, spotNote, files, signal }) => {
      assertNonEmpty(planId, 'planId');
      assertNonEmpty(spotId, 'spotId');
      assertNonEmptyFiles(files);

      const formData = new FormData();
      formData.append('planId', planId);
      formData.append('spotId', spotId);
      if (spotNote?.trim()) {
        formData.append('spotNote', spotNote);
      }
      for (const file of files) {
        formData.append('files', file);
      }

      return request<void, FormData>({
        method: 'POST',
        path: '/spot-reflections',
        body: formData,
        signal,
        responseType: 'void',
      });
    },
  };
};

const authFetch: typeof fetch = async (input, init) => {
  let token: string | null = null;
  try {
    token = auth?.currentUser ? await auth.currentUser.getIdToken() : null;
  } catch {
    token = null;
  }
  const headers = new Headers(init?.headers);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetch(input, { ...init, headers });
};

export const createApiClientFromEnv = (options?: { prefix?: string }): ApiClient => {
  const baseUrl = getRequiredEnv();
  return createApiClient({ baseUrl, prefix: options?.prefix, fetcher: authFetch });
};
