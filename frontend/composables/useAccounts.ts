import type { Account, AccountSummary, PaginatedResponse } from '~/types';
import type { StandardError } from '~/types/errors';

export const useAccounts = () => {
  const { apiFetch } = useApi();
  const { handleError } = useErrorHandler();

  const getAccounts = async (params?: {
    account_type?: string;
    currency?: string;
    is_active?: boolean;
    search?: string;
    ordering?: string;
  }): Promise<{ data?: PaginatedResponse<Account>; success: boolean; error?: StandardError }> => {
    try {
      const queryParams = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, value.toString());
          }
        });
      }

      const query = queryParams.toString();
      const endpoint = query ? `/api/v1/accounts/?${query}` : '/api/v1/accounts/';

      const response = await apiFetch<PaginatedResponse<Account>>(endpoint);
      return { success: true, data: response };
    } catch (error: any) {
      console.error('Get accounts error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  const getAccount = async (id: number): Promise<{ data?: Account; success: boolean; error?: StandardError }> => {
    try {
      const account = await apiFetch<Account>(`/api/v1/accounts/${id}/`);
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Get account error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  const createAccount = async (accountData: {
    name: string;
    account_type: string;
    balance: string | number;
    currency: string;
    description?: string;
  }): Promise<{ data?: Account; success: boolean; error?: StandardError }> => {
    try {
      const account = await apiFetch<Account>('/api/v1/accounts/', {
        method: 'POST',
        body: accountData,
      });
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Create account error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  const updateAccount = async (id: number, accountData: Partial<Account>): Promise<{ data?: Account; success: boolean; error?: StandardError }> => {
    try {
      const account = await apiFetch<Account>(`/api/v1/accounts/${id}/`, {
        method: 'PATCH',
        body: accountData,
      });
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Update account error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  const deleteAccount = async (id: number): Promise<{ success: boolean; error?: StandardError }> => {
    try {
      await apiFetch(`/api/v1/accounts/${id}/`, {
        method: 'DELETE',
      });
      return { success: true };
    } catch (error: any) {
      console.error('Delete account error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  const getAccountsSummary = async (): Promise<{ data?: AccountSummary; success: boolean; error?: StandardError }> => {
    try {
      const summary = await apiFetch<AccountSummary>('/api/v1/accounts/summary/');
      return { success: true, data: summary };
    } catch (error: any) {
      console.error('Get accounts summary error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  const toggleAccountActive = async (id: number): Promise<{ data?: Account; success: boolean; error?: StandardError }> => {
    try {
      const account = await apiFetch<Account>(`/api/v1/accounts/${id}/toggle_active/`, {
        method: 'POST',
      });
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Toggle account active error:', error);
      const standardError = handleError(error, { showToast: false });
      return {
        success: false,
        error: standardError,
      };
    }
  };

  return {
    getAccounts,
    getAccount,
    createAccount,
    updateAccount,
    deleteAccount,
    getAccountsSummary,
    toggleAccountActive,
  };
};
