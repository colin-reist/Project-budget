export const useUserProfile = () => {
  const { apiFetch } = useApi()

  /**
   * Get current user's profile
   */
  const getProfile = async (): Promise<{ data: any | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch('/api/v1/auth/profile/me/', {
        method: 'GET'
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error fetching profile:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Update current user's profile
   */
  const updateProfile = async (profileData: {
    monthly_income?: number | string
    currency?: string
  }): Promise<{ data: any | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch('/api/v1/auth/profile/update/', {
        method: 'PATCH',
        body: profileData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error updating profile:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Change password
   */
  const changePassword = async (passwordData: {
    current_password: string
    new_password: string
  }): Promise<{ data: any | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch('/api/v1/auth/profile/change_password/', {
        method: 'POST',
        body: passwordData
      })
      return { data, success: true }
    } catch (error) {
      console.error('Error changing password:', error)
      return { data: null, success: false, error }
    }
  }

  /**
   * Delete account
   */
  const deleteAccount = async (deleteData: {
    password: string
    confirm: string
  }): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch('/api/v1/auth/profile/delete_account/', {
        method: 'DELETE',
        body: deleteData
      })
      return { success: true }
    } catch (error) {
      console.error('Error deleting account:', error)
      return { success: false, error }
    }
  }

  return {
    getProfile,
    updateProfile,
    changePassword,
    deleteAccount
  }
}
