import type { UseFetchOptions } from 'nuxt/app';

// Global flag to prevent multiple redirects
let isRedirecting = false;

export const useApi = () => {
  const config = useRuntimeConfig();

  const apiFetch = async <T>(
    endpoint: string,
    options: UseFetchOptions<T> = {}
  ) => {
    // Get fresh cookie value on each request
    const token = useCookie('access_token');
    const refreshToken = useCookie('refresh_token');

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Merge with options headers if provided
    if (options.headers) {
      Object.assign(headers, options.headers);
    }

    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    }

    try {
      return await $fetch<T>(`${config.public.apiBase}${endpoint}`, {
        ...options as any,
        headers,
        credentials: 'include',
      });
    } catch (error: any) {
      // Check if error is authentication related (401 or 403)
      if (error.status === 401 || error.status === 403) {
        // Only redirect once, even if multiple requests fail
        if (!isRedirecting) {
          isRedirecting = true;

          // Clear tokens
          token.value = null;
          refreshToken.value = null;

          // Redirect to login page using navigateTo (Nuxt 3 way)
          await navigateTo('/login', { replace: true });

          // Reset the flag after a short delay
          setTimeout(() => {
            isRedirecting = false;
          }, 1000);
        }
      }

      // Re-throw the error so it can be handled by the caller
      throw error;
    }
  };

  return {
    apiFetch,
  };
};
