import type { User, TokenResponse } from '~/types';

export const useAuth = () => {
  const { apiFetch } = useApi();
  const router = useRouter();

  const user = useState<User | null>('user', () => null);
  const isAuthenticated = computed(() => !!user.value);

  const accessToken = useCookie('access_token', {
    maxAge: 60 * 15, // 15 minutes
    sameSite: 'strict',
    secure: process.env.NODE_ENV === 'production',
  });

  const refreshToken = useCookie('refresh_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 days
    sameSite: 'strict',
    secure: process.env.NODE_ENV === 'production',
  });

  const register = async (userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => {
    try {
      const response = await apiFetch<TokenResponse>('/api/v1/auth/register/', {
        method: 'POST',
        body: userData,
      });

      accessToken.value = response.access;
      refreshToken.value = response.refresh;

      await fetchUser(response.access);

      return { success: true };
    } catch (error: any) {
      console.error('Register error:', error);
      return {
        success: false,
        error: error.data?.detail || error.data || 'Registration failed',
        errors: error.data || {}
      };
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await apiFetch<TokenResponse>('/api/v1/auth/login/', {
        method: 'POST',
        body: { username, password },
      });

      accessToken.value = response.access;
      refreshToken.value = response.refresh;

      await fetchUser(response.access);

      return { success: true };
    } catch (error: any) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.data?.detail || 'Login failed'
      };
    }
  };

  const logout = async () => {
    try {
      await apiFetch('/api/v1/auth/logout/', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      accessToken.value = null;
      refreshToken.value = null;
      user.value = null;
      router.push('/login');
    }
  };

  const fetchUser = async (token?: string) => {
    try {
      const headers: any = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const userData = await apiFetch<User>('/api/v1/auth/me/', {
        headers
      });
      user.value = userData;
    } catch (error) {
      console.error('Fetch user error:', error);
      accessToken.value = null;
      refreshToken.value = null;
      user.value = null;
    }
  };

  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available');
      }

      const response = await apiFetch<{ access: string }>('/api/v1/auth/token/refresh/', {
        method: 'POST',
        body: { refresh: refreshToken.value },
      });

      accessToken.value = response.access;
      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      await logout();
      return false;
    }
  };

  return {
    user,
    isAuthenticated,
    register,
    login,
    logout,
    fetchUser,
    refreshAccessToken,
  };
};
