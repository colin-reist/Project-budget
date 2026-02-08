import type { Category, PaginatedResponse } from '~/types'

export const useCategories = () => {
  const { apiFetch } = useApi()

  /**
   * Récupérer la liste des catégories
   */
  const getCategories = async (params?: {
    type?: 'income' | 'expense'
    is_active?: boolean
    search?: string
  }): Promise<{ data: PaginatedResponse<Category> | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<PaginatedResponse<Category>>('/api/v1/categories/', {
        method: 'GET',
        params
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching categories:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Récupérer une catégorie par son ID
   */
  const getCategory = async (id: number): Promise<{ data: Category | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Category>(`/api/v1/categories/${id}/`)
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching category:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Créer une nouvelle catégorie
   */
  const createCategory = async (categoryData: Partial<Category>): Promise<{ data: Category | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Category>('/api/v1/categories/', {
        method: 'POST',
        body: categoryData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating category:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Mettre à jour une catégorie
   */
  const updateCategory = async (id: number, categoryData: Partial<Category>): Promise<{ data: Category | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<Category>(`/api/v1/categories/${id}/`, {
        method: 'PUT',
        body: categoryData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating category:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Supprimer une catégorie
   */
  const deleteCategory = async (id: number): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch(`/api/v1/categories/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting category:', error)
      return { success: false, error }
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
