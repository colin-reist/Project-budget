export interface UserProfile {
  id: number
  monthly_income: number
  currency: 'CHF' | 'EUR' | 'USD' | 'GBP'
  salary_day: number | null
  created_at: string
  updated_at: string
  available_budget_info?: {
    available_budget: number
    total_budget_allocations: number
    remaining_budget: number
  }
}

export const useUserProfile = () => {
  const { apiFetch } = useApi()

  // Global reactive state for user profile
  const userProfile = useState<UserProfile | null>('userProfile', () => null)

  // Computed property for currency with fallback to CHF
  const currency = computed(() => userProfile.value?.currency || 'CHF')

  // Flag to track if profile has been loaded
  const isProfileLoaded = useState<boolean>('isProfileLoaded', () => false)

  /**
   * Fetch and store user profile in global state
   */
  const fetchProfile = async (): Promise<{ success: boolean; error?: any }> => {
    try {
      const data = await apiFetch('/api/v1/auth/profile/me/', {
        method: 'GET'
      })
      userProfile.value = data
      isProfileLoaded.value = true
      return { success: true }
    } catch (error) {
      console.error('Error fetching profile:', error)
      return { success: false, error }
    }
  }

  /**
   * Auto-fetch profile on first access if not already loaded
   */
  const ensureProfileLoaded = async () => {
    if (!isProfileLoaded.value) {
      await fetchProfile()
    }
  }

  /**
   * Get current user's profile (legacy method, prefer using userProfile ref directly)
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
   * Update current user's profile and refresh global state
   */
  const updateProfile = async (profileData: {
    monthly_income?: number | string
    currency?: string
    salary_day?: number | null
  }): Promise<{ data: any | null; success: boolean; error?: any }> => {
    try {
      const data = await apiFetch('/api/v1/auth/profile/update/', {
        method: 'PATCH',
        body: profileData
      })
      // Update global state with new data
      userProfile.value = data
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
    userProfile,
    currency,
    fetchProfile,
    ensureProfileLoaded,
    getProfile,
    updateProfile,
    changePassword,
    deleteAccount
  }
}
