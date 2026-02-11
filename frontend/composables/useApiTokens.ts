import type { APIToken } from '~/types'

export const useApiTokens = () => {
  const { apiFetch } = useApi()

  const getTokens = async (): Promise<{ data: APIToken[] | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<APIToken[]>('/api/v1/auth/tokens/')
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching tokens:', error)
      return { data: null, success: false, error }
    }
  }

  const createToken = async (name: string): Promise<{ data: APIToken | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<APIToken>('/api/v1/auth/tokens/create/', {
        method: 'POST',
        body: { name }
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error creating token:', error)
      return { data: null, success: false, error }
    }
  }

  const deleteToken = async (id: number): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch(`/api/v1/auth/tokens/${id}/`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting token:', error)
      return { success: false, error }
    }
  }

  return { getTokens, createToken, deleteToken }
}
