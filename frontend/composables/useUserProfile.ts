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

  // Track ongoing profile fetch to avoid duplicate requests
  const isProfileFetching = useState<boolean>('isProfileFetching', () => false)

  // Store the pending fetch promise to allow multiple callers to await the same request
  const pendingFetch = useState<Promise<{ success: boolean; error?: any }> | null>('pendingProfileFetch', () => null)

  // Cache timestamp for mobile optimization (5 minutes cache)
  const profileCacheTime = useState<number>('profileCacheTime', () => 0)
  const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

  /**
   * Fetch and store user profile in global state
   * Optimized for mobile with request deduplication
   */
  const fetchProfile = async (forceRefresh = false): Promise<{ success: boolean; error?: any }> => {
    // If already fetching, return the pending promise
    if (isProfileFetching.value && pendingFetch.value) {
      return pendingFetch.value
    }

    // Check cache validity (for mobile performance)
    const now = Date.now()
    const isCacheValid = !forceRefresh &&
                         isProfileLoaded.value &&
                         (now - profileCacheTime.value) < CACHE_DURATION

    if (isCacheValid) {
      return { success: true }
    }

    // Start fetching
    isProfileFetching.value = true

    const fetchPromise = (async () => {
      try {
        const data = await apiFetch('/api/v1/auth/profile/me/', {
          method: 'GET'
        })
        userProfile.value = data
        isProfileLoaded.value = true
        profileCacheTime.value = Date.now()
        return { success: true }
      } catch (error) {
        console.error('Error fetching profile:', error)
        return { success: false, error }
      } finally {
        isProfileFetching.value = false
        pendingFetch.value = null
      }
    })()

    pendingFetch.value = fetchPromise
    return fetchPromise
  }

  /**
   * Auto-fetch profile on first access if not already loaded
   * Optimized to prevent duplicate requests
   */
  const ensureProfileLoaded = async () => {
    if (!isProfileLoaded.value || isProfileFetching.value) {
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
