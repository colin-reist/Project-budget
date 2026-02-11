import { startRegistration, startAuthentication } from '@simplewebauthn/browser';
import type {
  PublicKeyCredentialCreationOptionsJSON,
  PublicKeyCredentialRequestOptionsJSON,
} from '@simplewebauthn/types';

export const useWebAuthn = () => {
  const { apiFetch } = useApi();
  const { fetchUser } = useAuth();
  const router = useRouter();

  const accessToken = useCookie('access_token', {
    maxAge: 60 * 15,
    sameSite: 'strict',
    secure: process.env.NODE_ENV === 'production',
  });

  const refreshToken = useCookie('refresh_token', {
    maxAge: 60 * 60 * 24 * 7,
    sameSite: 'strict',
    secure: process.env.NODE_ENV === 'production',
  });

  const registerWebAuthn = async (username: string) => {
    try {
      // Get registration options from server
      const options = await apiFetch<PublicKeyCredentialCreationOptionsJSON>(
        '/api/v1/auth/webauthn/register/begin/',
        {
          method: 'POST',
          body: { username },
        }
      );

      // Verify options have required fields
      if (!options || !options.challenge) {
        console.error('Invalid options received:', options);
        throw new Error('Invalid registration options received from server');
      }

      // Start registration with browser WebAuthn API
      const credential = await startRegistration(options);

      // Send credential to server for verification
      const response = await apiFetch('/api/v1/auth/webauthn/register/complete/', {
        method: 'POST',
        body: {
          username,
          credential,
        },
      });

      return { success: true, data: response };
    } catch (error: any) {
      console.error('WebAuthn registration error:', error);
      return {
        success: false,
        error: error.message || 'Registration failed',
      };
    }
  };

  const authenticateWebAuthn = async () => {
    try {
      // Get authentication options from server
      const options = await apiFetch<PublicKeyCredentialRequestOptionsJSON>(
        '/api/v1/auth/webauthn/login/begin/',
        {
          method: 'POST',
        }
      );

      // Start authentication with browser WebAuthn API
      const credential = await startAuthentication(options);

      // Send credential to server for verification
      const response = await apiFetch<{
        access: string;
        refresh: string;
        user: any;
      }>('/api/v1/auth/webauthn/login/complete/', {
        method: 'POST',
        body: { credential },
      });

      // Store tokens
      accessToken.value = response.access;
      refreshToken.value = response.refresh;

      // Fetch user data with the new access token
      await fetchUser(response.access);

      return { success: true };
    } catch (error: any) {
      console.error('WebAuthn authentication error:', error);
      return {
        success: false,
        error: error.message || 'Authentication failed',
      };
    }
  };

  const listCredentials = async () => {
    try {
      const credentials = await apiFetch('/api/v1/auth/webauthn/credentials/');
      return { success: true, data: credentials };
    } catch (error: any) {
      console.error('List credentials error:', error);
      return {
        success: false,
        error: error.message || 'Failed to list credentials',
      };
    }
  };

  const deleteCredential = async (credentialId: number) => {
    try {
      await apiFetch(`/api/v1/auth/webauthn/credentials/${credentialId}/`, {
        method: 'DELETE',
      });
      return { success: true };
    } catch (error: any) {
      console.error('Delete credential error:', error);
      return {
        success: false,
        error: error.message || 'Failed to delete credential',
      };
    }
  };

  return {
    registerWebAuthn,
    authenticateWebAuthn,
    listCredentials,
    deleteCredential,
  };
};
