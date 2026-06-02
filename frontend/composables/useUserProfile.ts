export interface UserProfile {
  id: number
  // User model projections (read-only from API)
  username: string
  email: string
  first_name: string
  last_name: string
  date_joined: string
  last_login: string | null
  // Financial
  monthly_income: number
  currency: 'CHF' | 'EUR' | 'USD' | 'GBP'
  salary_day: number | null
  // Personal info
  phone: string
  birth_date: string | null
  // Locale preferences
  language: string
  timezone_pref: string
  city: string
  country: string
  // Budget preferences
  budget_start_day: number
  budget_rollover: boolean
  budget_roundup: boolean
  budget_roundup_amount: string
  show_cents: boolean
  // Meta
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

  // Computed property for budget start day with fallback to 1 (calendar month)
  const budgetStartDay = computed(() => userProfile.value?.budget_start_day ?? 1)

  /**
   * Returns the budget month (year, month) for today's date given a start day.
   * With startDay=25 and today=June 2 → { year: 2026, month: 6 } (between May 25 and June 24)
   * With startDay=25 and today=June 26 → { year: 2026, month: 7 } (new period started June 25)
   */
  const getCurrentBudgetMonth = (startDay: number): { year: number; month: number } => {
    const today = new Date()
    if (startDay <= 1) return { year: today.getFullYear(), month: today.getMonth() + 1 }
    if (today.getDate() >= startDay) {
      // New period started this month → budget month is next calendar month
      const next = new Date(today.getFullYear(), today.getMonth() + 1, 1)
      return { year: next.getFullYear(), month: next.getMonth() + 1 }
    }
    return { year: today.getFullYear(), month: today.getMonth() + 1 }
  }

  /**
   * Returns ISO date strings for the start and end of a budget period (year, month).
   * With startDay=25 and (2026, 6) → { startDate: '2026-05-25', endDate: '2026-06-24' }
   * With startDay=1 → standard calendar month bounds
   */
  const getBudgetPeriodDates = (year: number, month: number, startDay: number): { startDate: string; endDate: string } => {
    const pad = (n: number) => String(n).padStart(2, '0')
    if (startDay <= 1) {
      const lastDay = new Date(year, month, 0).getDate()
      return { startDate: `${year}-${pad(month)}-01`, endDate: `${year}-${pad(month)}-${pad(lastDay)}` }
    }
    const prevMonth = month === 1 ? 12 : month - 1
    const prevYear = month === 1 ? year - 1 : year
    // Clamp start day to the actual number of days in the previous month (e.g. day 31 in February)
    const lastDayOfPrev = new Date(prevYear, prevMonth, 0).getDate()
    const actualStart = Math.min(startDay, lastDayOfPrev)
    return {
      startDate: `${prevYear}-${pad(prevMonth)}-${pad(actualStart)}`,
      endDate: `${year}-${pad(month)}-${pad(startDay - 1)}`
    }
  }

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
  const updateProfile = async (profileData: Partial<{
    monthly_income: number | string
    currency: string
    salary_day: number | null
    first_name: string
    last_name: string
    phone: string
    birth_date: string | null
    language: string
    timezone_pref: string
    city: string
    country: string
    budget_start_day: number
    budget_rollover: boolean
    budget_roundup: boolean
    budget_roundup_amount: string | number
    show_cents: boolean
  }>): Promise<{ data: any | null; success: boolean; error?: any }> => {
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

  const resetProfile = async (): Promise<{ success: boolean; error?: any }> => {
    try {
      await apiFetch('/api/v1/auth/profile/reset_profile/', { method: 'POST' })
      userProfile.value = null
      isProfileLoaded.value = false
      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  return {
    userProfile,
    currency,
    budgetStartDay,
    getCurrentBudgetMonth,
    getBudgetPeriodDates,
    fetchProfile,
    ensureProfileLoaded,
    getProfile,
    updateProfile,
    changePassword,
    deleteAccount,
    resetProfile
  }
}
