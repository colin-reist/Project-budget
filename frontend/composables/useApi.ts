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

          // Redirect to login page using window.location for reliability
          if (typeof window !== 'undefined') {
            console.log('Session expirée, redirection vers la page de login...');
            window.location.href = '/login';
          }

          // Reset the flag after a short delay
          setTimeout(() => {
            isRedirecting = false;
          }, 1000);
        }

        // Don't re-throw auth errors to avoid console spam
        // Just return a rejected promise
        return Promise.reject({
          status: error.status,
          message: 'Session expirée',
          redirecting: true
        });
      }

      // Re-throw other errors so they can be handled by the caller
      throw error;
    }
  };

  return {
    apiFetch,
  };
};
