import { watch, onUnmounted } from 'vue';

const INACTIVITY_TIMEOUT = 24 * 60 * 60 * 1000; // 24h (temporairement désactivé)
const WARNING_DURATION = 60; // seconds

export const useSessionTimeout = () => {
  const { logout, refreshAccessToken, isAuthenticated } = useAuth();

  const showWarning = useState<boolean>('session-timeout-warning', () => false);
  const countdown = useState<number>('session-timeout-countdown', () => WARNING_DURATION);

  let inactivityTimer: ReturnType<typeof setTimeout> | null = null;
  let countdownTimer: ReturnType<typeof setInterval> | null = null;
  let tokenRefreshTimer: ReturnType<typeof setInterval> | null = null;
  let hiddenAt: number | null = null;

  const clearTimers = () => {
    if (inactivityTimer) { clearTimeout(inactivityTimer); inactivityTimer = null; }
    if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null; }
  };

  const startCountdown = () => {
    showWarning.value = true;
    countdown.value = WARNING_DURATION;

    countdownTimer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearTimers();
        forceLogout();
      }
    }, 1000);
  };

  const resetInactivityTimer = () => {
    if (!isAuthenticated.value) return;
    if (showWarning.value) return; // don't reset if warning is shown

    if (inactivityTimer) clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
      clearTimers();
      startCountdown();
    }, INACTIVITY_TIMEOUT);
  };

  const stayConnected = () => {
    clearTimers();
    showWarning.value = false;
    countdown.value = WARNING_DURATION;
    resetInactivityTimer();
    refreshAccessToken();
  };

  const forceLogout = async () => {
    clearTimers();
    showWarning.value = false;
    if (tokenRefreshTimer) { clearInterval(tokenRefreshTimer); tokenRefreshTimer = null; }
    await logout();
  };

  const startTokenRefresh = () => {
    if (tokenRefreshTimer) clearInterval(tokenRefreshTimer);
    // Refresh token every 10 minutes (before 15min access token expires)
    tokenRefreshTimer = setInterval(() => {
      if (isAuthenticated.value && !showWarning.value) {
        refreshAccessToken();
      }
    }, 10 * 60 * 1000);
  };

  const handleVisibilityChange = async () => {
    if (!isAuthenticated.value) return;

    if (document.hidden) {
      // Tab goes to background: record time
      hiddenAt = Date.now();
    } else {
      // Tab comes back to foreground
      if (hiddenAt === null) return;
      const elapsed = Date.now() - hiddenAt;
      hiddenAt = null;

      if (elapsed >= INACTIVITY_TIMEOUT) {
        // User was away too long: show warning instead of silent logout
        clearTimers();
        startCountdown();
      } else {
        // Was away less than 10 min: refresh token proactively to avoid silent 401
        try {
          await refreshAccessToken();
        } catch {
          // refresh failed, forceLogout will be called by refreshAccessToken internally
          return;
        }
        resetInactivityTimer();
      }
    }
  };

  const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'click', 'touchstart', 'scroll'];

  const handleActivity = () => resetInactivityTimer();

  const start = () => {
    if (!import.meta.client) return;
    // Session timeout temporarily disabled — only keep token refresh
    startTokenRefresh();
  };

  const stop = () => {
    if (!import.meta.client) return;
    ACTIVITY_EVENTS.forEach(event => window.removeEventListener(event, handleActivity));
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    clearTimers();
    if (tokenRefreshTimer) { clearInterval(tokenRefreshTimer); tokenRefreshTimer = null; }
    hiddenAt = null;
  };

  // Watch auth state
  watch(isAuthenticated, (val) => {
    if (val) start();
    else stop();
  }, { immediate: true });

  onUnmounted(() => stop());

  return { showWarning, countdown, stayConnected, forceLogout };
};
