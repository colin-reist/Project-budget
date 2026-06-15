import type { UseFetchOptions } from 'nuxt/app';

let isRedirecting = false;
let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

export const useApi = () => {
  const config = useRuntimeConfig();

  const apiFetch = async <T>(
    endpoint: string,
    options: UseFetchOptions<T> = {}
  ): Promise<T> => {
    const token = useCookie('access_token');
    const refreshToken = useCookie('refresh_token');

    const buildHeaders = (): Record<string, string> => {
      const h: Record<string, string> = { 'Content-Type': 'application/json' };
      if (options.headers) Object.assign(h, options.headers);
      if (token.value) h['Authorization'] = `Bearer ${token.value}`;
      return h;
    };

    const apiBase = import.meta.server ? config.apiBaseServer : config.public.apiBase;

    const doFetch = () => $fetch<T>(`${apiBase}${endpoint}`, {
      ...options as any,
      headers: buildHeaders(),
      credentials: 'include',
    });

    try {
      return await doFetch();
    } catch (error: any) {
      if ((error.status === 401 || error.status === 403) && typeof window !== 'undefined') {
        // Skip refresh for auth endpoints to avoid infinite loops
        if (endpoint.includes('/auth/login') || endpoint.includes('/auth/token/refresh') || endpoint.includes('/auth/logout')) {
          token.value = null;
          refreshToken.value = null;
          if (!isRedirecting) {
            isRedirecting = true;
            window.location.href = '/login';
            setTimeout(() => { isRedirecting = false; }, 1000);
          }
          return Promise.reject({ status: error.status, message: 'Session expirée', redirecting: true });
        }

        // Attempt silent token refresh
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = $fetch<{ access: string }>(`${apiBase}/api/v1/auth/token/refresh/`, {
            method: 'POST',
            body: { refresh: refreshToken.value },
          }).then(res => {
            token.value = (res as any).access;
            return true;
          }).catch(() => {
            token.value = null;
            refreshToken.value = null;
            return false;
          }).finally(() => {
            isRefreshing = false;
            refreshPromise = null;
          });
        }

        const refreshed = await refreshPromise;
        if (refreshed) {
          try {
            return await doFetch();
          } catch {
            // Fall through to redirect
          }
        }

        if (!isRedirecting) {
          isRedirecting = true;
          window.location.href = '/login';
          setTimeout(() => { isRedirecting = false; }, 1000);
        }
        return Promise.reject({ status: error.status, message: 'Session expirée', redirecting: true });
      }

      throw error;
    }
  };

  return { apiFetch };
};
