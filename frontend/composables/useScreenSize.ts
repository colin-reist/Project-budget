/**
 * Screen size detection composable
 * Optimized for mobile with reactive breakpoints
 */

export const useScreenSize = () => {
  // Breakpoints matching Tailwind CSS defaults
  const breakpoints = {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536
  }

  // Reactive screen width
  const screenWidth = ref(0)

  // Computed breakpoint checks
  const isMobile = computed(() => screenWidth.value < breakpoints.sm)
  const isTablet = computed(() => screenWidth.value >= breakpoints.sm && screenWidth.value < breakpoints.lg)
  const isDesktop = computed(() => screenWidth.value >= breakpoints.lg)

  const isSmallScreen = computed(() => screenWidth.value < breakpoints.md)
  const isMediumScreen = computed(() => screenWidth.value >= breakpoints.md && screenWidth.value < breakpoints.xl)
  const isLargeScreen = computed(() => screenWidth.value >= breakpoints.xl)

  // Update screen width
  const updateScreenWidth = () => {
    if (process.client) {
      screenWidth.value = window.innerWidth
    }
  }

  // Initialize and add resize listener
  onMounted(() => {
    updateScreenWidth()
    window.addEventListener('resize', updateScreenWidth)
  })

  // Cleanup
  onUnmounted(() => {
    if (process.client) {
      window.removeEventListener('resize', updateScreenWidth)
    }
  })

  return {
    screenWidth,
    isMobile,
    isTablet,
    isDesktop,
    isSmallScreen,
    isMediumScreen,
    isLargeScreen,
    breakpoints
  }
}
