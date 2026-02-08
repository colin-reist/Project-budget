import type { UseFetchOptions } from 'nuxt/app';

export const useApi = () => {
  const config = useRuntimeConfig();

  const apiFetch = async <T>(
    endpoint: string,
    options: UseFetchOptions<T> = {}
  ) => {
    // Get fresh cookie value on each request
    const token = useCookie('access_token');

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    }

    return $fetch<T>(`${config.public.apiBase}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include',
    });
  };

  return {
    apiFetch,
  };
};
