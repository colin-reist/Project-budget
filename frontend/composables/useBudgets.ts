import type { Budget, PaginatedResponse } from '~/types'
import type { StandardError } from '~/types/errors'

export const useBudgets = () => {
  const { apiFetch } = useApi()
  const { handleError } = useErrorHandler()

  /**
   * Récupérer la liste des budgets
   */
  const getBudgets = async (params?: {
    period?: 'weekly' | 'monthly' | 'yearly'
    category?: number
    is_active?: boolean
    search?: string
  }): Promise<{ data: PaginatedResponse<Budget> | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<PaginatedResponse<Budget>>('/api/v1/budgets/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budgets:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Récupérer un budget par son ID
   */
  const getBudget = async (id: number): Promise<{ data: Budget | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Budget>(`/api/v1/budgets/${id}/`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budget:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Créer un nouveau budget
   */
  const createBudget = async (budgetData: Partial<Budget>): Promise<{ data: Budget | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Budget>('/api/v1/budgets/', {
        method: 'POST',
        body: budgetData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating budget:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Mettre à jour un budget
   */
  const updateBudget = async (id: number, budgetData: Partial<Budget>): Promise<{ data: Budget | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Budget>(`/api/v1/budgets/${id}/`, {
        method: 'PUT',
        body: budgetData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating budget:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Supprimer un budget
   */
  const deleteBudget = async (id: number): Promise<{ success: boolean; error?: StandardError }> => {
    try {
      await apiFetch(`/api/v1/budgets/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting budget:', error)
      const standardError = handleError(error, { showToast: false })
      return { success: false, error: standardError }
    }
  }

  /**
   * Récupérer le résumé des budgets
   */
  const getBudgetsSummary = async (): Promise<{
    data: {
      total_budgets: number
      total_amount: number
      total_spent: number
      total_remaining: number
      over_budget_count: number
      alert_count: number
      percentage_used: number
    } | null
    success: boolean
    error?: StandardError
  }> => {
    try {
      const data = await apiFetch('/api/v1/budgets/summary/')
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budgets summary:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Activer/Désactiver un budget
   */
  const toggleBudgetActive = async (id: number): Promise<{ data: Budget | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Budget>(`/api/v1/budgets/${id}/toggle_active/`, {
        method: 'POST'
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error toggling budget active:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Récupérer les données budget vs réel pour le dashboard
   */
  const getDashboardData = async (params?: { year?: number; month?: number }): Promise<{ data: any | null; success: boolean; error?: StandardError }> => {
    try {
      const query = params ? `?year=${params.year}&month=${params.month}` : ''
      const data = await apiFetch(`/api/v1/budgets/dashboard_data/${query}`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budget dashboard data:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  return {
    getBudgets,
    getBudget,
    createBudget,
    updateBudget,
    deleteBudget,
    getBudgetsSummary,
    getDashboardData,
    toggleBudgetActive
  }
}
