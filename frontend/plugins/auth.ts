export default defineNuxtPlugin(async () => {
  const { fetchUser } = useAuth()
  const accessToken = useCookie('access_token')

  // Si un token existe, restaurer l'utilisateur au démarrage
  if (accessToken.value) {
    try {
      await fetchUser(accessToken.value)
    } catch (error) {
      console.error('Failed to restore user session:', error)
      // Le token est invalide, on le supprime
      accessToken.value = null
      const refreshToken = useCookie('refresh_token')
      refreshToken.value = null
    }
  }
})
