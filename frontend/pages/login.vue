<template>
  <div class="login-root fade-up">
    <div class="login-grid">

      <!-- ── Brand Panel (desktop only) ────────────────────── -->
      <aside class="brand-panel">
        <div class="brand-deco" aria-hidden />

        <div class="brand-top">
          <div class="logo-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 17l5-5 4 4 8-8" /><path d="M14 8h6v6" />
            </svg>
          </div>
          <div>
            <div class="brand-name">Budget Tracker</div>
            <div class="brand-version mono">v{{ appVersion }} — self-hosted</div>
          </div>
        </div>

        <div class="brand-body">
          <div>
            <h1 class="brand-headline">Reprenez le contrôle<br>de vos finances.</h1>
            <p class="brand-sub">
              Suivez vos budgets, comptes, transactions récurrentes et objectifs d'épargne — le tout sur votre propre serveur.
            </p>
          </div>

          <div class="savings-card">
            <div class="savings-card-top">
              <div>
                <div class="savings-label">Épargne cumulée</div>
                <div class="savings-amount-row">
                  <span class="savings-amount mono">CHF 12'480</span>
                  <span class="savings-delta">+8.4%</span>
                </div>
              </div>
              <span class="savings-badge">Objectif 80%</span>
            </div>
            <div class="chart-bars">
              <div v-for="(v, i) in chartMonths" :key="i" class="chart-bar-col">
                <div
                  :style="{ height: (v / maxMonth * 100) + '%' }"
                  :class="i === chartMonths.length - 1 ? 'bar-active' : 'bar-inactive'"
                  class="chart-bar"
                />
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="m in monthLabels" :key="m">{{ m }}</span>
            </div>
          </div>
        </div>

        <div class="brand-footer">
          <span>Hosted on your Raspberry Pi 🥧</span>
        </div>
      </aside>

      <!-- ── Form Panel ─────────────────────────────────────── -->
      <div class="form-panel">
        <header class="form-header">
          <div class="header-brand">
            <div class="logo-mark" style="width:26px;height:26px">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 17l5-5 4 4 8-8" /><path d="M14 8h6v6" />
              </svg>
            </div>
            <span class="header-brand-name">Budget Tracker</span>
          </div>
          <button class="theme-btn ds-btn-icon" :aria-label="isDark ? 'Mode clair' : 'Mode sombre'" @click="toggleDark">
            <UIcon :name="isDark ? 'i-heroicons-sun' : 'i-heroicons-moon'" style="width:16px;height:16px;" />
          </button>
        </header>

        <div class="form-center">
          <div class="form-inner">
            <form :class="{ shake: shaking }" class="login-form" @submit.prevent="handleLogin">

              <div class="form-title-group">
                <h2 class="form-title">Connexion à votre compte</h2>
                <p class="form-sub">Entrez vos identifiants ou utilisez votre passkey.</p>
              </div>

              <!-- Passkey -->
              <button type="button" :disabled="loadingWebAuthn || loading" class="passkey-btn" @click="handleWebAuthnLogin">
                <span v-if="loadingWebAuthn" class="btn-spinner" />
                <UIcon v-else name="i-heroicons-finger-print" style="width:18px;height:18px;flex-shrink:0;" />
                <span>{{ loadingWebAuthn ? 'Veuillez patienter…' : 'Se connecter avec une Passkey' }}</span>
              </button>

              <!-- Or divider -->
              <div class="or-divider">
                <div class="or-line" />
                <span class="or-text">Ou continuer avec</span>
                <div class="or-line" />
              </div>

              <!-- Username -->
              <div class="field-group">
                <label for="username" class="field-label">
                  Nom d'utilisateur <span style="color:var(--accent)">*</span>
                </label>
                <div
                  class="field-wrap"
                  :class="{
                    'field-focused': focused === 'username',
                    'field-error':   fieldErr.username,
                    'field-disabled': loading,
                  }"
                >
                  <UIcon
                    name="i-heroicons-user"
                    class="field-icon"
                    :style="{ color: focused === 'username' ? 'var(--accent)' : 'var(--ink-4)' }"
                  />
                  <input
                    id="username"
                    v-model="loginForm.username"
                    type="text"
                    placeholder="colin"
                    autocomplete="username"
                    :disabled="loading"
                    class="field-input"
                    autofocus
                    @focus="focused = 'username'"
                    @blur="focused = null"
                    @input="fieldErr.username = ''"
                  >
                </div>
                <p v-if="fieldErr.username" class="field-err">{{ fieldErr.username }}</p>
              </div>

              <!-- Password -->
              <div class="field-group">
                <label for="password" class="field-label">
                  Mot de passe <span style="color:var(--accent)">*</span>
                </label>
                <div
                  class="field-wrap"
                  :class="{
                    'field-focused': focused === 'password',
                    'field-error':   fieldErr.password,
                    'field-disabled': loading,
                  }"
                >
                  <UIcon
                    name="i-heroicons-lock-closed"
                    class="field-icon"
                    :style="{ color: focused === 'password' ? 'var(--accent)' : 'var(--ink-4)' }"
                  />
                  <input
                    id="password"
                    v-model="loginForm.password"
                    :type="showPwd ? 'text' : 'password'"
                    placeholder="••••••••"
                    autocomplete="current-password"
                    :disabled="loading"
                    class="field-input"
                    @focus="focused = 'password'"
                    @blur="focused = null"
                    @input="fieldErr.password = ''"
                  >
                  <button
                    type="button"
                    :aria-label="showPwd ? 'Masquer' : 'Afficher'"
                    tabindex="-1"
                    class="eye-btn"
                    @click="showPwd = !showPwd"
                  >
                    <UIcon :name="showPwd ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" style="width:18px;height:18px;" />
                  </button>
                </div>
                <p v-if="fieldErr.password" class="field-err">{{ fieldErr.password }}</p>
              </div>

              <!-- Remember + forgot -->
              <div class="remember-row">
                <label class="remember-label">
                  <span class="remember-box" :class="{ checked: remember }">
                    <svg v-if="remember" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" style="width:11px;height:11px">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                  <input v-model="remember" type="checkbox" class="sr-only">
                  <span style="font-size:13px">Rester connecté</span>
                </label>
                <a href="#" class="forgot-link">Mot de passe oublié ?</a>
              </div>

              <!-- Error -->
              <div v-if="error" role="alert" class="error-alert">
                <UIcon name="i-heroicons-exclamation-triangle" style="width:18px;height:18px;color:var(--danger);flex-shrink:0;margin-top:1px;" />
                <span style="font-size:13px;line-height:1.45">{{ error }}</span>
              </div>

              <!-- Submit -->
              <button type="submit" :disabled="loading || loadingWebAuthn" class="submit-btn">
                <template v-if="loading">
                  <span class="btn-spinner" />
                  <span>Veuillez patienter…</span>
                </template>
                <template v-else>
                  <span>Se connecter</span>
                  <UIcon name="i-heroicons-arrow-right" style="width:18px;height:18px;" />
                </template>
              </button>

              <!-- Register -->
              <div class="register-row">
                Pas encore de compte ?
                <NuxtLink to="/register" class="register-link">Créer un compte</NuxtLink>
              </div>

              <!-- Demo hint -->
              <div class="demo-hint mono">
                <span style="opacity:.65">demo →</span>
                username: <b style="color:var(--ink-2)">demo</b>
                · password: <b style="color:var(--ink-2)">demo1234</b>
              </div>
            </form>
          </div>
        </div>

        <footer class="form-footer">
          <span>© 2026 Budget Tracker</span>
          <div style="display:flex;gap:16px;">
            <a href="#">Confidentialité</a>
            <a href="#">Conditions</a>
          </div>
        </footer>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false, middleware: 'guest' })

const config = useRuntimeConfig()
const appVersion = config.public.appVersion

const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')
const toggleDark = () => { colorMode.preference = isDark.value ? 'light' : 'dark' }

const { login } = useAuth()
const { authenticateWebAuthn } = useWebAuthn()
const router = useRouter()

const loginForm = reactive({ username: '', password: '' })
const loading = ref(false)
const loadingWebAuthn = ref(false)
const error = ref('')
const fieldErr = reactive({ username: '', password: '' })
const showPwd = ref(false)
const remember = ref(true)
const shaking = ref(false)
const focused = ref<string | null>(null)

const chartMonths = [42, 58, 51, 70, 64, 82, 76, 90]
const maxMonth = Math.max(...chartMonths)
const monthLabels = ['Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

const triggerShake = () => {
  shaking.value = true
  setTimeout(() => { shaking.value = false }, 450)
}

const validate = () => {
  fieldErr.username = loginForm.username.trim() ? '' : "Le nom d'utilisateur est requis"
  fieldErr.password = loginForm.password ? '' : 'Le mot de passe est requis'
  return !fieldErr.username && !fieldErr.password
}

const handleLogin = async () => {
  error.value = ''
  if (!validate()) { triggerShake(); return }
  loading.value = true
  const result = await login(loginForm.username, loginForm.password)
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error || 'Une erreur est survenue'
    triggerShake()
  }
  loading.value = false
}

const handleWebAuthnLogin = async () => {
  loadingWebAuthn.value = true
  error.value = ''
  const result = await authenticateWebAuthn()
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error || 'Authentification échouée'
  }
  loadingWebAuthn.value = false
}
</script>

<style scoped>
/* ── Animations ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60%  { transform: translateX(-6px); }
  40%, 80%  { transform: translateX(6px); }
}
@keyframes spin { to { transform: rotate(360deg); } }

.fade-up { animation: fadeUp .5s cubic-bezier(.2,.7,.2,1) both; }
.shake   { animation: shake 0.42s cubic-bezier(.36,.07,.19,.97); }

/* ── Root ── */
.login-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Geist', ui-sans-serif, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.login-grid {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
@media (min-width: 1024px) {
  .login-grid {
    display: grid;
    grid-template-columns: minmax(320px, 0.6fr) minmax(440px, 1fr);
  }
}

/* ── Brand panel ── */
.brand-panel {
  display: none;
  position: relative;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  padding: 40px 36px;
  background: linear-gradient(160deg, #0c1830 0%, #0f172a 38%, #122454 100%);
  border-right: 1px solid rgba(255,255,255,0.04);
}
@media (min-width: 1024px) { .brand-panel { display: flex; } }

.brand-deco {
  position: absolute; inset: 0; opacity: 0.5; pointer-events: none;
  background-image:
    radial-gradient(circle at 20% 0%, rgba(59,130,246,0.22), transparent 45%),
    radial-gradient(circle at 100% 90%, rgba(34,197,94,0.14), transparent 50%),
    linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
  background-size: auto, auto, 36px 36px, 36px 36px;
}

.brand-top {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-mark {
  width: 36px; height: 36px; border-radius: 28%;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  display: grid; place-items: center; flex-shrink: 0;
  box-shadow: 0 6px 14px -6px rgba(37,99,235,0.5), inset 0 1px 0 rgba(255,255,255,0.18);
}

.brand-name    { font-size: 16px; font-weight: 600; letter-spacing: -0.2px; color: white; }
.brand-version { font-size: 11px; color: rgba(226,232,240,0.55); letter-spacing: 0.4px; }

.brand-body {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.brand-headline {
  margin: 0; font-size: 38px; line-height: 1.1;
  letter-spacing: -0.8px; font-weight: 600; color: white;
}
.brand-sub {
  margin: 16px 0 0; font-size: 15px; line-height: 1.55;
  max-width: 380px; color: rgba(226,232,240,0.72);
}

.savings-card {
  background: rgba(15,23,42,0.55);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 20px;
  max-width: 420px;
  box-shadow: 0 20px 40px -20px rgba(0,0,0,0.45);
}
.savings-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.savings-label     { font-size: 11px; color: rgba(226,232,240,0.55); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 500; }
.savings-amount-row { display: flex; align-items: baseline; gap: 8px; margin-top: 4px; }
.savings-amount    { font-size: 26px; font-weight: 500; color: white; letter-spacing: -0.5px; }
.savings-delta     { font-size: 12px; color: #4ade80; font-weight: 500; }
.savings-badge     {
  padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 500;
  background: rgba(34,197,94,0.14); color: #86efac; border: 1px solid rgba(34,197,94,0.22);
}
.chart-bars {
  display: flex; align-items: flex-end; gap: 8px; height: 64px;
}
.chart-bar-col { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; }
.chart-bar     { width: 100%; border-radius: 3px; transition: all 0.4s ease; }
.bar-active    { background: linear-gradient(180deg, #60a5fa 0%, #2563eb 100%); }
.bar-inactive  { background: rgba(148,163,184,0.28); }
.chart-labels  { display: flex; justify-content: space-between; margin-top: 8px; font-size: 10px; color: rgba(226,232,240,0.45); }

.brand-footer {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(226,232,240,0.4);
}

/* ── Form panel ── */
.form-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 28px 24px;
  background: var(--bg);
}
@media (min-width: 640px) { .form-panel { padding: 32px 56px; } }

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}
.header-brand-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
}
@media (min-width: 1024px) {
  .header-brand-name { display: none; }
}

.theme-btn {
  background: transparent !important;
  border: 1px solid var(--line-strong) !important;
  color: var(--ink-2) !important;
}
.theme-btn:hover { background: var(--surface-2) !important; }

/* Form center */
.form-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 0;
}
.form-inner { width: 100%; max-width: 400px; }

.login-form { display: flex; flex-direction: column; gap: 18px; }

.form-title-group { margin-bottom: 6px; }
.form-title { margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.5px; color: var(--ink); line-height: 1.2; }
.form-sub   { margin: 6px 0 0; font-size: 14px; color: var(--ink-3); }

/* Passkey button */
.passkey-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  height: 44px; width: 100%;
  font-size: 14px; font-weight: 500; font-family: inherit;
  background: var(--surface); color: var(--ink);
  border: 1px solid var(--line-strong); border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  cursor: pointer; transition: background 0.15s;
}
.passkey-btn:hover:not(:disabled) { background: var(--surface-2); }
.passkey-btn:disabled { opacity: 0.55; cursor: not-allowed; }

/* Or divider */
.or-divider { display: flex; align-items: center; gap: 12px; }
.or-line    { flex: 1; height: 1px; background: var(--line); }
.or-text    { font-size: 12px; color: var(--ink-4); white-space: nowrap; }

/* Fields */
.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 13px; font-weight: 500; color: var(--ink-2); }

.field-wrap {
  display: flex; align-items: center; gap: 10px;
  height: 44px; padding: 0 12px;
  background: var(--surface); border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.field-wrap.field-focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--ring);
}
.field-wrap.field-error {
  border-color: var(--danger);
  box-shadow: 0 0 0 3px rgba(220,38,38,0.15);
}
.field-wrap.field-disabled { opacity: 0.6; }

.field-icon  { width: 18px; height: 18px; flex-shrink: 0; transition: color 0.15s; }
.field-input {
  flex: 1; font-size: 14px; background: transparent; border: none; outline: none;
  color: var(--ink); font-family: inherit;
}
.field-input::placeholder { color: var(--ink-4); }
.field-input:disabled      { cursor: not-allowed; }
.field-err { margin: 0; font-size: 12px; color: var(--danger); }

.eye-btn {
  background: transparent; border: none; cursor: pointer; padding: 0;
  color: var(--ink-4); display: grid; place-items: center;
  width: 22px; height: 22px; border-radius: 4px; transition: color 0.15s;
}
.eye-btn:hover { color: var(--ink-2); }

/* Remember row */
.remember-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: -4px;
}
.remember-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--ink-2); cursor: pointer; user-select: none; position: relative;
}
.remember-box {
  width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0;
  border: 1.5px solid var(--line-strong); background: var(--surface);
  display: grid; place-items: center; transition: all 0.15s;
}
.remember-box.checked { background: var(--accent); border-color: var(--accent); }
.forgot-link {
  font-size: 13px; font-weight: 500; color: var(--accent); text-decoration: none; transition: color 0.15s;
}
.forgot-link:hover { color: var(--accent-hover); }

/* Error alert */
.error-alert {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px;
  background: var(--danger-soft); border: 1px solid rgba(220,38,38,0.3);
  border-radius: var(--radius); color: var(--ink-2);
}

/* Submit */
.submit-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  height: 44px; width: 100%;
  font-size: 14px; font-weight: 500; font-family: inherit;
  background: var(--accent); color: white;
  border: 1px solid transparent; border-radius: var(--radius);
  box-shadow: 0 1px 0 rgba(255,255,255,0.15) inset, 0 6px 14px -8px rgba(37,99,235,0.45);
  cursor: pointer; transition: background 0.15s;
}
.submit-btn:hover:not(:disabled) { background: var(--accent-hover); }
.submit-btn:disabled { opacity: 0.55; cursor: not-allowed; }

/* Spinner */
.btn-spinner {
  width: 18px; height: 18px; border-radius: 50%;
  border: 2.4px solid rgba(255,255,255,0.22);
  border-top-color: white;
  display: block; flex-shrink: 0;
  animation: spin 0.7s linear infinite;
}
.passkey-btn .btn-spinner {
  border-color: rgba(0,0,0,0.1);
  border-top-color: var(--ink-3);
}

/* Register + footer */
.register-row {
  text-align: center; font-size: 13.5px; color: var(--ink-3); margin-top: 4px;
}
.register-link {
  color: var(--accent); font-weight: 500; margin-left: 4px; text-decoration: none; transition: color 0.15s;
}
.register-link:hover { color: var(--accent-hover); }

.demo-hint {
  margin-top: 4px; padding: 8px 12px;
  background: var(--surface-2); border: 1px dashed var(--line-strong);
  border-radius: var(--radius-sm); font-size: 11.5px; color: var(--ink-3);
}

.form-footer {
  display: flex; justify-content: space-between;
  font-size: 12px; color: var(--ink-4);
}
.form-footer a { color: inherit; text-decoration: none; transition: color 0.15s; }
.form-footer a:hover { color: var(--ink-2); }
</style>
