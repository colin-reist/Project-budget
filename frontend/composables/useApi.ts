import type { UseFetchOptions } from 'nuxt/app';

export const useApi = () => {
  const config = useRuntimeConfig();
  const router = useRouter();

  const apiFetch = async <T>(
    endpoint: string,
    options: UseFetchOptions<T> = {}
  ) => {
    // Get fresh cookie value on each request
    const token = useCookie('access_token');
    const refreshToken = useCookie('refresh_token');

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    }

    try {
      return await $fetch<T>(`${config.public.apiBase}${endpoint}`, {
        ...options,
        headers,
        credentials: 'include',
      });
    } catch (error: any) {
      // Check if error is authentication related (401 or 403)
      if (error.status === 401 || error.status === 403) {
        // Clear tokens
        token.value = null;
        refreshToken.value = null;

        // Redirect to login page
        await router.push('/login');
      }

      // Re-throw the error so it can be handled by the caller
      throw error;
    }
  };

  return {
    apiFetch,
  };
};
