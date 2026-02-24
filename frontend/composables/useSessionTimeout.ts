import { ref, watch, onUnmounted } from 'vue';

const INACTIVITY_TIMEOUT = 10 * 60 * 1000; // 10 minutes
const WARNING_DURATION = 60; // seconds

export const useSessionTimeout = () => {
  const { logout, refreshAccessToken, isAuthenticated } = useAuth();

  const showWarning = useState<boolean>('session-timeout-warning', () => false);
  const countdown = useState<number>('session-timeout-countdown', () => WARNING_DURATION);

  let inactivityTimer: ReturnType<typeof setTimeout> | null = null;
  let countdownTimer: ReturnType<typeof setInterval> | null = null;
  let tokenRefreshTimer: ReturnType<typeof setInterval> | null = null;

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

  const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'click', 'touchstart', 'scroll'];

  const handleActivity = () => resetInactivityTimer();

  const start = () => {
    if (!import.meta.client) return;
    ACTIVITY_EVENTS.forEach(event => window.addEventListener(event, handleActivity, { passive: true }));
    resetInactivityTimer();
    startTokenRefresh();
  };

  const stop = () => {
    if (!import.meta.client) return;
    ACTIVITY_EVENTS.forEach(event => window.removeEventListener(event, handleActivity));
    clearTimers();
    if (tokenRefreshTimer) { clearInterval(tokenRefreshTimer); tokenRefreshTimer = null; }
  };

  // Watch auth state
  watch(isAuthenticated, (val) => {
    if (val) start();
    else stop();
  }, { immediate: true });

  onUnmounted(() => stop());

  return { showWarning, countdown, stayConnected, forceLogout };
};
