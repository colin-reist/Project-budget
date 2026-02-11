import type { SavingsGoal, PaginatedResponse } from '~/types'

export const useSavingsGoals = () => {
  const { apiFetch } = useApi()

  const getSavingsGoals = async (params?: {
    status?: string
    search?: string
  }): Promise<{ data: PaginatedResponse<SavingsGoal> | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<PaginatedResponse<SavingsGoal>>('/api/v1/savings-goals/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching savings goals:', error)
      return { data: null, success: false, error }
    }
  }

  const getSavingsGoal = async (id: number): Promise<{ data: SavingsGoal | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<SavingsGoal>(`/api/v1/savings-goals/${id}/`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching savings goal:', error)
      return { data: null, success: false, error }
    }
  }

  const createSavingsGoal = async (goalData: Partial<SavingsGoal>): Promise<{ data: SavingsGoal | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<SavingsGoal>('/api/v1/savings-goals/', {
        method: 'POST',
        body: goalData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating savings goal:', error)
      return { data: null, success: false, error }
    }
  }

  const updateSavingsGoal = async (id: number, goalData: Partial<SavingsGoal>): Promise<{ data: SavingsGoal | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<SavingsGoal>(`/api/v1/savings-goals/${id}/`, {
        method: 'PUT',
        body: goalData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating savings goal:', error)
      return { data: null, success: false, error }
    }
  }

  const deleteSavingsGoal = async (id: number): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch(`/api/v1/savings-goals/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting savings goal:', error)
      return { success: false, error }
    }
  }

  const createBudgetFromGoal = async (id: number): Promise<{ data: any | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch(`/api/v1/savings-goals/${id}/create_budget/`, {
        method: 'POST'
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating budget from goal:', error)
      return { data: null, success: false, error }
    }
  }

  return {
    getSavingsGoals,
    getSavingsGoal,
    createSavingsGoal,
    updateSavingsGoal,
    deleteSavingsGoal,
    createBudgetFromGoal
  }
}
