'use client';

import { useCallback, useState } from 'react';

import { type ApiError, toApiError } from '@/lib/api';

export type UseApiRequestResult<T, Args extends unknown[]> = {
  execute: (...args: Args) => Promise<T>;
  isLoading: boolean;
  error: ApiError | null;
  resetError: () => void;
};

export const useApiRequest = <T, Args extends unknown[]>(
  request: (...args: Args) => Promise<T>
): UseApiRequestResult<T, Args> => {
  const [inFlightCount, setInFlightCount] = useState(0);
  const [error, setError] = useState<ApiError | null>(null);
  const isLoading = inFlightCount > 0;

  const execute = useCallback(
    async (...args: Args): Promise<T> => {
      setInFlightCount(count => count + 1);
      setError(null);
      try {
        return await request(...args);
      } catch (err) {
        const apiError = toApiError(err);
        setError(apiError);
        throw apiError;
      } finally {
        setInFlightCount(count => Math.max(0, count - 1));
      }
    },
    [request]
  );

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  return { execute, isLoading, error, resetError };
};
