<template>
  <div class="reg-root fade-up">
    <div class="reg-grid">

      <!-- ── Brand Panel (desktop only) ─────────────────────── -->
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
            <h1 class="brand-headline">Commencez à<br>reprendre le contrôle.</h1>
            <p class="brand-sub">
              Créez votre compte en quelques secondes et accédez à votre tableau de bord financier personnel — hébergé chez vous, pas dans un cloud tiers.
            </p>
          </div>

          <div class="feature-list">
            <div v-for="f in features" :key="f.label" class="feature-item">
              <div class="feature-icon">
                <UIcon :name="f.icon" style="width:14px;height:14px;" />
              </div>
              <span>{{ f.label }}</span>
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

            <!-- ── Success: Passkey step ── -->
            <div v-if="showPasskeyOption" :class="{ shake: shaking }" class="reg-form passkey-step">
              <div class="form-title-group">
                <div class="success-badge">
                  <UIcon name="i-heroicons-check" style="width:16px;height:16px;" />
                  Compte créé !
                </div>
                <h2 class="form-title" style="margin-top:12px;">Sécurisez votre compte</h2>
                <p class="form-sub">Enregistrez une passkey pour vous connecter sans mot de passe, compatible avec Proton Pass et votre appareil.</p>
              </div>

              <div class="passkey-card">
                <div class="passkey-card-icon">
                  <UIcon name="i-heroicons-finger-print" style="width:28px;height:28px;color:var(--accent);" />
                </div>
                <div class="passkey-card-body">
                  <div class="passkey-card-title">Connexion par Passkey</div>
                  <div class="passkey-card-desc">Biométrie, PIN ou clé de sécurité — zéro mot de passe à retenir.</div>
                </div>
              </div>

              <div v-if="passkeyError" role="alert" class="error-alert">
                <UIcon name="i-heroicons-exclamation-triangle" style="width:18px;height:18px;color:var(--danger);flex-shrink:0;margin-top:1px;" />
                <span style="font-size:13px;line-height:1.45">{{ passkeyError }}</span>
              </div>

              <button type="button" :disabled="loadingPasskey" class="submit-btn" @click="handleRegisterPasskey">
                <template v-if="loadingPasskey">
                  <span class="btn-spinner" />
                  <span>Enregistrement…</span>
                </template>
                <template v-else>
                  <UIcon name="i-heroicons-finger-print" style="width:18px;height:18px;" />
                  <span>Enregistrer une Passkey</span>
                </template>
              </button>

              <button type="button" class="skip-btn" @click="skipPasskey">
                Continuer sans passkey →
              </button>
            </div>

            <!-- ── Registration Form ── -->
            <form v-else :class="{ shake: shaking }" class="reg-form" @submit.prevent="handleRegister">

              <div class="form-title-group">
                <h2 class="form-title">Créer votre compte</h2>
                <p class="form-sub">Rejoignez Budget Tracker et prenez le contrôle de vos finances.</p>
              </div>

              <!-- Username -->
              <div class="field-group">
                <label for="username" class="field-label">
                  Nom d'utilisateur <span style="color:var(--accent)">*</span>
                </label>
                <div
                  class="field-wrap"
                  :class="{
                    'field-focused':  focused === 'username',
                    'field-error':    fieldErr.username,
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
                    v-model="form.username"
                    type="text"
                    placeholder="colin"
                    autocomplete="username"
                    inputmode="text"
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

              <!-- Email -->
              <div class="field-group">
                <label for="email" class="field-label">
                  Adresse email <span style="color:var(--accent)">*</span>
                </label>
                <div
                  class="field-wrap"
                  :class="{
                    'field-focused':  focused === 'email',
                    'field-error':    fieldErr.email,
                    'field-disabled': loading,
                  }"
                >
                  <UIcon
                    name="i-heroicons-envelope"
                    class="field-icon"
                    :style="{ color: focused === 'email' ? 'var(--accent)' : 'var(--ink-4)' }"
                  />
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    placeholder="vous@exemple.com"
                    autocomplete="email"
                    inputmode="email"
                    :disabled="loading"
                    class="field-input"
                    @focus="focused = 'email'"
                    @blur="focused = null"
                    @input="fieldErr.email = ''"
                  >
                </div>
                <p v-if="fieldErr.email" class="field-err">{{ fieldErr.email }}</p>
              </div>

              <!-- First + Last name -->
              <div class="name-row">
                <div class="field-group">
                  <label for="first_name" class="field-label">Prénom</label>
                  <div
                    class="field-wrap"
                    :class="{
                      'field-focused':  focused === 'first_name',
                      'field-disabled': loading,
                    }"
                  >
                    <input
                      id="first_name"
                      v-model="form.first_name"
                      type="text"
                      placeholder="Colin"
                      autocomplete="given-name"
                      :disabled="loading"
                      class="field-input"
                      style="padding-left:12px"
                      @focus="focused = 'first_name'"
                      @blur="focused = null"
                    >
                  </div>
                </div>
                <div class="field-group">
                  <label for="last_name" class="field-label">Nom</label>
                  <div
                    class="field-wrap"
                    :class="{
                      'field-focused':  focused === 'last_name',
                      'field-disabled': loading,
                    }"
                  >
                    <input
                      id="last_name"
                      v-model="form.last_name"
                      type="text"
                      placeholder="Reist"
                      autocomplete="family-name"
                      :disabled="loading"
                      class="field-input"
                      style="padding-left:12px"
                      @focus="focused = 'last_name'"
                      @blur="focused = null"
                    >
                  </div>
                </div>
              </div>

              <!-- Password -->
              <div class="field-group">
                <label for="password" class="field-label">
                  Mot de passe <span style="color:var(--accent)">*</span>
                </label>
                <div
                  class="field-wrap"
                  :class="{
                    'field-focused':  focused === 'password',
                    'field-error':    fieldErr.password,
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
                    v-model="form.password"
                    :type="showPwd ? 'text' : 'password'"
                    placeholder="Minimum 8 caractères"
                    autocomplete="new-password"
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
                <!-- Password strength -->
                <div v-if="form.password" class="pwd-strength">
                  <div class="pwd-bars">
                    <div
                      v-for="i in 4"
                      :key="i"
                      class="pwd-bar"
                      :class="i <= pwdScore ? pwdBarClass : 'pwd-bar-empty'"
                    />
                  </div>
                  <span class="pwd-label" :class="pwdLabelClass">{{ pwdLabel }}</span>
                </div>
                <p v-if="fieldErr.password" class="field-err">{{ fieldErr.password }}</p>
              </div>

              <!-- Confirm password -->
              <div class="field-group">
                <label for="confirmPassword" class="field-label">
                  Confirmer le mot de passe <span style="color:var(--accent)">*</span>
                </label>
                <div
                  class="field-wrap"
                  :class="{
                    'field-focused':  focused === 'confirmPassword',
                    'field-error':    fieldErr.confirmPassword,
                    'field-disabled': loading,
                  }"
                >
                  <UIcon
                    name="i-heroicons-shield-check"
                    class="field-icon"
                    :style="{ color: focused === 'confirmPassword' ? 'var(--accent)' : 'var(--ink-4)' }"
                  />
                  <input
                    id="confirmPassword"
                    v-model="form.confirmPassword"
                    :type="showConfirmPwd ? 'text' : 'password'"
                    placeholder="Répétez votre mot de passe"
                    autocomplete="new-password"
                    :disabled="loading"
                    class="field-input"
                    @focus="focused = 'confirmPassword'"
                    @blur="focused = null"
                    @input="fieldErr.confirmPassword = ''"
                  >
                  <button
                    type="button"
                    :aria-label="showConfirmPwd ? 'Masquer' : 'Afficher'"
                    tabindex="-1"
                    class="eye-btn"
                    @click="showConfirmPwd = !showConfirmPwd"
                  >
                    <UIcon :name="showConfirmPwd ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" style="width:18px;height:18px;" />
                  </button>
                </div>
                <p v-if="fieldErr.confirmPassword" class="field-err">{{ fieldErr.confirmPassword }}</p>
              </div>

              <!-- Global error -->
              <div v-if="error" role="alert" class="error-alert">
                <UIcon name="i-heroicons-exclamation-triangle" style="width:18px;height:18px;color:var(--danger);flex-shrink:0;margin-top:1px;" />
                <span style="font-size:13px;line-height:1.45">{{ error }}</span>
              </div>

              <!-- Submit -->
              <button type="submit" :disabled="loading" class="submit-btn">
                <template v-if="loading">
                  <span class="btn-spinner" />
                  <span>Création du compte…</span>
                </template>
                <template v-else>
                  <span>Créer mon compte</span>
                  <UIcon name="i-heroicons-arrow-right" style="width:18px;height:18px;" />
                </template>
              </button>

              <!-- Login link -->
              <div class="login-row">
                Déjà un compte ?
                <NuxtLink to="/login" class="login-link">Se connecter</NuxtLink>
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

const { register } = useAuth()
const { registerWebAuthn } = useWebAuthn()
const router = useRouter()

const features = [
  { icon: 'i-heroicons-chart-bar', label: 'Budgets mensuels et suivi en temps réel' },
  { icon: 'i-heroicons-arrow-path', label: 'Transactions récurrentes automatiques' },
  { icon: 'i-heroicons-banknotes', label: 'Multi-comptes avec vue consolidée' },
  { icon: 'i-heroicons-sparkles', label: 'Objectifs d\'épargne et projections' },
  { icon: 'i-heroicons-finger-print', label: 'Connexion sans mot de passe (Passkey)' },
]

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  confirmPassword: '',
})

const loading = ref(false)
const loadingPasskey = ref(false)
const error = ref('')
const passkeyError = ref('')
const fieldErr = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})
const showPwd = ref(false)
const showConfirmPwd = ref(false)
const shaking = ref(false)
const focused = ref<string | null>(null)
const showPasskeyOption = ref(false)

const pwdScore = computed(() => {
  const p = form.password
  if (!p) return 0
  let score = 0
  if (p.length >= 8)  score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/\d/.test(p) && /[^A-Za-z0-9]/.test(p)) score++
  return Math.max(1, score)
})

const pwdLabel = computed(() => ['', 'Faible', 'Moyen', 'Bon', 'Fort'][pwdScore.value])
const pwdBarClass = computed(() => ['', 'pwd-bar-weak', 'pwd-bar-fair', 'pwd-bar-good', 'pwd-bar-strong'][pwdScore.value])
const pwdLabelClass = computed(() => ['', 'pwd-label-weak', 'pwd-label-fair', 'pwd-label-good', 'pwd-label-strong'][pwdScore.value])

const triggerShake = () => {
  shaking.value = true
  setTimeout(() => { shaking.value = false }, 450)
}

const validate = () => {
  let ok = true
  fieldErr.username = form.username.trim() ? '' : "Le nom d'utilisateur est requis"
  if (fieldErr.username) ok = false

  if (!form.email.trim()) {
    fieldErr.email = "L'email est requis"
    ok = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    fieldErr.email = 'Adresse email invalide'
    ok = false
  } else {
    fieldErr.email = ''
  }

  if (!form.password) {
    fieldErr.password = 'Le mot de passe est requis'
    ok = false
  } else if (form.password.length < 8) {
    fieldErr.password = 'Minimum 8 caractères'
    ok = false
  } else {
    fieldErr.password = ''
  }

  if (!form.confirmPassword) {
    fieldErr.confirmPassword = 'Veuillez confirmer le mot de passe'
    ok = false
  } else if (form.password !== form.confirmPassword) {
    fieldErr.confirmPassword = 'Les mots de passe ne correspondent pas'
    ok = false
  } else {
    fieldErr.confirmPassword = ''
  }

  return ok
}

const handleRegister = async () => {
  error.value = ''
  if (!validate()) { triggerShake(); return }
  loading.value = true

  const { confirmPassword, ...rest } = form
  const result = await register({ ...rest, password2: confirmPassword })

  if (result.success) {
    showPasskeyOption.value = true
  } else {
    if (typeof result.error === 'string') {
      error.value = result.error
    } else if (result.errors) {
      const firstField = Object.keys(result.errors)[0] as keyof typeof fieldErr
      if (firstField in fieldErr) {
        (fieldErr as any)[firstField] = Array.isArray(result.errors[firstField])
          ? result.errors[firstField][0]
          : result.errors[firstField]
      } else {
        error.value = Object.values(result.errors).flat().join(' ')
      }
    }
    triggerShake()
  }

  loading.value = false
}

const handleRegisterPasskey = async () => {
  loadingPasskey.value = true
  passkeyError.value = ''
  const result = await registerWebAuthn(form.username)
  if (result.success) {
    router.push('/')
  } else {
    passkeyError.value = result.error || 'Erreur lors de l\'enregistrement de la passkey'
  }
  loadingPasskey.value = false
}

const skipPasskey = () => router.push('/')
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
.reg-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Geist', ui-sans-serif, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.reg-grid {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
@media (min-width: 1024px) {
  .reg-grid {
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

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(226,232,240,0.75);
}
.feature-icon {
  width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0;
  background: rgba(59,130,246,0.15);
  border: 1px solid rgba(59,130,246,0.25);
  display: grid; place-items: center;
  color: #93c5fd;
}

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

.form-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px 0;
}
.form-inner { width: 100%; max-width: 400px; }

.reg-form { display: flex; flex-direction: column; gap: 16px; }

.form-title-group { margin-bottom: 4px; }
.form-title { margin: 0; font-size: 26px; font-weight: 600; letter-spacing: -0.5px; color: var(--ink); line-height: 1.2; }
.form-sub   { margin: 6px 0 0; font-size: 14px; color: var(--ink-3); }

/* Name row */
.name-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
@media (min-width: 1280px) {
  .name-row { flex-direction: row; gap: 12px; }
  .name-row .field-group { flex: 1; min-width: 0; }
}

/* Fields */
.field-group { display: flex; flex-direction: column; gap: 5px; }
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

/* Password strength */
.pwd-strength {
  display: flex; align-items: center; gap: 10px; margin-top: 2px;
}
.pwd-bars {
  display: flex; gap: 4px; flex: 1;
}
.pwd-bar {
  flex: 1; height: 3px; border-radius: 99px; transition: background 0.25s;
}
.pwd-bar-empty  { background: var(--line-strong); }
.pwd-bar-weak   { background: #ef4444; }
.pwd-bar-fair   { background: #f97316; }
.pwd-bar-good   { background: #eab308; }
.pwd-bar-strong { background: #22c55e; }

.pwd-label { font-size: 11px; font-weight: 500; white-space: nowrap; }
.pwd-label-weak   { color: #ef4444; }
.pwd-label-fair   { color: #f97316; }
.pwd-label-good   { color: #ca8a04; }
.pwd-label-strong { color: #16a34a; }

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
  margin-top: 4px;
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

/* Login link */
.login-row {
  text-align: center; font-size: 13.5px; color: var(--ink-3); margin-top: 2px;
}
.login-link {
  color: var(--accent); font-weight: 500; margin-left: 4px; text-decoration: none; transition: color 0.15s;
}
.login-link:hover { color: var(--accent-hover); }

/* Passkey step */
.passkey-step { gap: 20px; }

.success-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 500;
  background: var(--success-soft); color: var(--success);
  border: 1px solid rgba(22,163,74,0.25);
}

.passkey-card {
  display: flex; align-items: center; gap: 16px;
  padding: 16px; border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--line-strong);
  box-shadow: var(--shadow-sm);
}
.passkey-card-icon {
  width: 52px; height: 52px; flex-shrink: 0;
  border-radius: var(--radius);
  background: var(--accent-soft);
  display: grid; place-items: center;
}
.passkey-card-title { font-size: 14px; font-weight: 600; color: var(--ink); }
.passkey-card-desc  { font-size: 13px; color: var(--ink-3); margin-top: 3px; }

.skip-btn {
  background: transparent; border: none; cursor: pointer; padding: 0;
  font-size: 13px; color: var(--ink-3); font-family: inherit;
  text-align: center; transition: color 0.15s;
}
.skip-btn:hover { color: var(--ink-2); }

/* Footer */
.form-footer {
  display: flex; justify-content: space-between;
  font-size: 12px; color: var(--ink-4);
}
.form-footer a { color: inherit; text-decoration: none; transition: color 0.15s; }
.form-footer a:hover { color: var(--ink-2); }
</style>
