export default defineNuxtRouteMiddleware(async (to, from) => {
  const { isAuthenticated, fetchUser } = useAuth()
  const accessToken = useCookie('access_token')

  // Si un token existe mais l'utilisateur n'est pas chargé, le charger
  if (accessToken.value && !isAuthenticated.value) {
    try {
      await fetchUser(accessToken.value)
    } catch (error) {
      // Token invalide, rediriger vers login
      accessToken.value = null
      const refreshToken = useCookie('refresh_token')
      refreshToken.value = null
      return navigateTo('/login')
    }
  }

  // Vérifier l'authentification
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
