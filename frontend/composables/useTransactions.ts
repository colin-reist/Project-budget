import type { Transaction, PaginatedResponse } from '~/types'

export const useTransactions = () => {
  const { apiFetch } = useApi()

  /**
   * Récupérer la liste des transactions
   */
  const getTransactions = async (params?: {
    type?: 'income' | 'expense' | 'transfer'
    account?: number
    category?: number
    date?: string
    is_recurring?: boolean
    search?: string
    ordering?: string
    page?: number
  }): Promise<{ data: PaginatedResponse<Transaction> | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<PaginatedResponse<Transaction>>('/api/v1/transactions/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching transactions:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Récupérer une transaction par son ID
   */
  const getTransaction = async (id: number): Promise<{ data: Transaction | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Transaction>(`/api/v1/transactions/${id}/`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching transaction:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Créer une nouvelle transaction
   */
  const createTransaction = async (transactionData: Partial<Transaction>): Promise<{ data: Transaction | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Transaction>('/api/v1/transactions/', {
        method: 'POST',
        body: transactionData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating transaction:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Mettre à jour une transaction
   */
  const updateTransaction = async (id: number, transactionData: Partial<Transaction>): Promise<{ data: Transaction | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Transaction>(`/api/v1/transactions/${id}/`, {
        method: 'PUT',
        body: transactionData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating transaction:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Supprimer une transaction
   */
  const deleteTransaction = async (id: number): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch(`/api/v1/transactions/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting transaction:', error)
      return { success: false, error }
    }
  }

  /**
   * Récupérer les statistiques des transactions
   */
  const getStatistics = async (params?: {
    start_date?: string
    end_date?: string
  }): Promise<{
    data: {
      income: { total: number; count: number }
      expense: { total: number; count: number }
      transfer: { total: number; count: number }
      net: number
    } | null
    success: boolean
    error?: any
  }> => {
    try {
      const data = await apiFetch('/api/v1/transactions/statistics/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching statistics:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Récupérer les transactions par catégorie
   */
  const getByCategory = async (params?: {
    type?: 'income' | 'expense'
    start_date?: string
    end_date?: string
  }): Promise<{
    data: Array<{
      category_id: number
      category_name: string
      color: string
      total: number
      count: number
    }> | null
    success: boolean
    error?: any
  }> => {
    try {
      const data = await apiFetch('/api/v1/transactions/by_category/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching by category:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Récupérer le résumé mensuel
   */
  const getMonthlySummary = async (year?: number): Promise<{
    data: Record<number, {
      month: number
      income: number
      expense: number
      net: number
    }> | null
    success: boolean
    error?: any
  }> => {
    try {
      const data = await apiFetch('/api/v1/transactions/monthly_summary/', {
        method: 'GET',
        params: year ? { year } : undefined
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching monthly summary:', error)
      return { data: null, success: false, error }
    }
  }

  return {
    getTransactions,
    getTransaction,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    getStatistics,
    getByCategory,
    getMonthlySummary
  }
}
