import type { Account, AccountSummary, PaginatedResponse } from '~/types';

export const useAccounts = () => {
  const { apiFetch } = useApi();

  const getAccounts = async (params?: {
    account_type?: string;
    currency?: string;
    is_active?: boolean;
    search?: string;
    ordering?: string;
  }) => {
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
      return {
        success: false,
        error: error.message || 'Failed to fetch accounts',
      };
    }
  };

  const getAccount = async (id: number) => {
    try {
      const account = await apiFetch<Account>(`/api/v1/accounts/${id}/`);
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Get account error:', error);
      return {
        success: false,
        error: error.message || 'Failed to fetch account',
      };
    }
  };

  const createAccount = async (accountData: {
    name: string;
    account_type: string;
    balance: string | number;
    currency: string;
    description?: string;
  }) => {
    try {
      const account = await apiFetch<Account>('/api/v1/accounts/', {
        method: 'POST',
        body: accountData,
      });
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Create account error:', error);
      return {
        success: false,
        error: error.data?.detail || error.message || 'Failed to create account',
        errors: error.data || {},
      };
    }
  };

  const updateAccount = async (id: number, accountData: Partial<Account>) => {
    try {
      const account = await apiFetch<Account>(`/api/v1/accounts/${id}/`, {
        method: 'PATCH',
        body: accountData,
      });
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Update account error:', error);
      return {
        success: false,
        error: error.data?.detail || error.message || 'Failed to update account',
        errors: error.data || {},
      };
    }
  };

  const deleteAccount = async (id: number) => {
    try {
      await apiFetch(`/api/v1/accounts/${id}/`, {
        method: 'DELETE',
      });
      return { success: true };
    } catch (error: any) {
      console.error('Delete account error:', error);
      return {
        success: false,
        error: error.message || 'Failed to delete account',
      };
    }
  };

  const getAccountsSummary = async () => {
    try {
      const summary = await apiFetch<AccountSummary>('/api/v1/accounts/summary/');
      return { success: true, data: summary };
    } catch (error: any) {
      console.error('Get accounts summary error:', error);
      return {
        success: false,
        error: error.message || 'Failed to fetch accounts summary',
      };
    }
  };

  const toggleAccountActive = async (id: number) => {
    try {
      const account = await apiFetch<Account>(`/api/v1/accounts/${id}/toggle_active/`, {
        method: 'POST',
      });
      return { success: true, data: account };
    } catch (error: any) {
      console.error('Toggle account active error:', error);
      return {
        success: false,
        error: error.message || 'Failed to toggle account status',
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
