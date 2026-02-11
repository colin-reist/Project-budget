import type { PendingAlert } from '~/types'

export const useAlerts = () => {
  const { apiFetch } = useApi()

  const getAlerts = async (): Promise<{ data: PendingAlert[] | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<PendingAlert[]>('/api/v1/alerts/')
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching alerts:', error)
      return { data: null, success: false, error }
    }
  }

  const getAlertCount = async (): Promise<{ data: { count: number } | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch<{ count: number }>('/api/v1/alerts/count/')
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching alert count:', error)
      return { data: null, success: false, error }
    }
  }

  const dismissAlert = async (id: number): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch(`/api/v1/alerts/${id}/dismiss/`, {
        method: 'POST'
      })
      return { success: true }
    } catch (error) {
      console.error('Error dismissing alert:', error)
      return { success: false, error }
    }
  }

  return { getAlerts, getAlertCount, dismissAlert }
}
