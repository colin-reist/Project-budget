import type { Category, PaginatedResponse } from '~/types'
import type { StandardError } from '~/types/errors'

export const useCategories = () => {
  const { apiFetch } = useApi()
  const { handleError } = useErrorHandler()

  /**
   * Récupérer la liste des catégories
   */
  const getCategories = async (params?: {
    type?: 'income' | 'expense'
    is_active?: boolean
    search?: string
  }): Promise<{ data: PaginatedResponse<Category> | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<PaginatedResponse<Category>>('/api/v1/categories/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching categories:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Récupérer une catégorie par son ID
   */
  const getCategory = async (id: number): Promise<{ data: Category | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Category>(`/api/v1/categories/${id}/`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching category:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Créer une nouvelle catégorie
   */
  const createCategory = async (categoryData: Partial<Category>): Promise<{ data: Category | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Category>('/api/v1/categories/', {
        method: 'POST',
        body: categoryData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating category:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Mettre à jour une catégorie
   */
  const updateCategory = async (id: number, categoryData: Partial<Category>): Promise<{ data: Category | null; success: boolean; error?: StandardError }> => {
    try {
      const data = await apiFetch<Category>(`/api/v1/categories/${id}/`, {
        method: 'PUT',
        body: categoryData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating category:', error)
      const standardError = handleError(error, { showToast: false })
      return { data: null, success: false, error: standardError }
    }
  }

  /**
   * Supprimer une catégorie
   */
  const deleteCategory = async (id: number): Promise<{ success: boolean; error?: StandardError }> => {
    try {
      await apiFetch(`/api/v1/categories/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting category:', error)
      const standardError = handleError(error, { showToast: false })
      return { success: false, error: standardError }
    }
  }

  return {
    getCategories,
    getCategory,
    createCategory,
    updateCategory,
    deleteCategory
  }
}
