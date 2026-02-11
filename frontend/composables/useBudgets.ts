import type { Budget, PaginatedResponse } from '~/types'

export const useBudgets = () => {
  const { apiFetch } = useApi()

  /**
   * Récupérer la liste des budgets
   */
  const getBudgets = async (params?: {
    period?: 'weekly' | 'monthly' | 'yearly'
    category?: number
    is_active?: boolean
    search?: string
  }): Promise<{ data: PaginatedResponse<Budget> | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<PaginatedResponse<Budget>>('/api/v1/budgets/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budgets:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Récupérer un budget par son ID
   */
  const getBudget = async (id: number): Promise<{ data: Budget | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Budget>(`/api/v1/budgets/${id}/`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budget:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Créer un nouveau budget
   */
  const createBudget = async (budgetData: Partial<Budget>): Promise<{ data: Budget | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Budget>('/api/v1/budgets/', {
        method: 'POST',
        body: budgetData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating budget:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Mettre à jour un budget
   */
  const updateBudget = async (id: number, budgetData: Partial<Budget>): Promise<{ data: Budget | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Budget>(`/api/v1/budgets/${id}/`, {
        method: 'PUT',
        body: budgetData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating budget:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Supprimer un budget
   */
  const deleteBudget = async (id: number): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch(`/api/v1/budgets/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting budget:', error)
      return { success: false, error }
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
    error?: any
  }> => {
    try {
      const data = await apiFetch('/api/v1/budgets/summary/')
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budgets summary:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Activer/Désactiver un budget
   */
  const toggleBudgetActive = async (id: number): Promise<{ data: Budget | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Budget>(`/api/v1/budgets/${id}/toggle_active/`, {
        method: 'POST'
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error toggling budget active:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Récupérer les données budget vs réel pour le dashboard
   */
  const getDashboardData = async (): Promise<{ data: any | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch('/api/v1/budgets/dashboard_data/')
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching budget dashboard data:', error)
      return { data: null, success: false, error }
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
