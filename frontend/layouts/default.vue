<template>
  <div class="app-shell" :class="colorMode.value === 'dark' ? 'dark' : ''">

    <!-- ── Sidebar (desktop ≥1024px) ─────────────────────────────── -->
    <aside v-if="isAuthenticated" class="sidebar">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">
          <UIcon name="i-heroicons-banknotes" style="width:17px;height:17px;color:#fff;" />
        </div>
        <div>
          <div class="sidebar-app-name">Budget Tracker</div>
          <div class="sidebar-app-version mono">v{{ appVersion }}</div>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <template v-for="(group, gi) in navGroups" :key="group.label">
          <div class="sidebar-group-label" :style="{ paddingTop: gi === 0 ? '4px' : '16px' }">
            {{ group.label }}
          </div>
          <NuxtLink
            v-for="item in group.items"
            :key="item.to"
            :to="item.to"
            class="sidebar-item"
            :class="{ 'sidebar-item--active': isActive(item) }"
          >
            <UIcon :name="item.icon" class="sidebar-item-icon" />
            <span>{{ item.label }}</span>
          </NuxtLink>
        </template>
      </nav>

      <!-- User + theme -->
      <div class="sidebar-footer">
        <button class="sidebar-theme-btn" @click="toggleTheme">
          <UIcon :name="isDark ? 'i-heroicons-sun' : 'i-heroicons-moon'" style="width:15px;height:15px;" />
          <span>{{ isDark ? 'Mode clair' : 'Mode sombre' }}</span>
        </button>
        <UDropdown :items="userMenuItems" :popper="{ placement: 'top-start' }">
          <button class="sidebar-user">
            <div class="sidebar-user-avatar">{{ userInitial }}</div>
            <div class="sidebar-user-info">
              <div class="sidebar-user-name">{{ user?.username }}</div>
              <div class="sidebar-user-email">{{ user?.email }}</div>
            </div>
            <UIcon name="i-heroicons-ellipsis-vertical" style="width:14px;height:14px;color:var(--ink-4);flex-shrink:0;" />
          </button>
        </UDropdown>
      </div>
    </aside>

    <!-- ── Main area ──────────────────────────────────────────────── -->
    <div class="main-area">

      <!-- Mobile top bar -->
      <div v-if="isAuthenticated" class="mobile-topbar">
        <div style="display:flex;align-items:center;gap:8px;">
          <div class="sidebar-logo-icon" style="width:26px;height:26px;border-radius:7px;">
            <UIcon name="i-heroicons-banknotes" style="width:14px;height:14px;color:#fff;" />
          </div>
          <span style="font-size:15px;font-weight:600;color:var(--ink);">Budget Tracker</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button class="ds-btn-icon" @click="toggleTheme">
            <UIcon :name="isDark ? 'i-heroicons-sun' : 'i-heroicons-moon'" style="width:16px;height:16px;" />
          </button>
          <button class="ds-btn-icon" @click="mobileMenuOpen = true">
            <UIcon name="i-heroicons-bars-3" style="width:16px;height:16px;" />
          </button>
        </div>
      </div>

      <!-- Page content -->
      <main class="page-content">
        <slot />
      </main>
    </div>

    <!-- ── Mobile slideover ───────────────────────────────────────── -->
    <USlideover v-model="mobileMenuOpen" side="right">
      <div class="p-4">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
          <span style="font-size:15px;font-weight:600;color:var(--ink);">Menu</span>
          <button class="ds-btn-icon" @click="mobileMenuOpen = false">
            <UIcon name="i-heroicons-x-mark" style="width:16px;height:16px;" />
          </button>
        </div>

        <div v-if="user" style="padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid var(--line);">
          <p style="font-size:13px;font-weight:500;color:var(--ink);margin:0;">{{ user.username }}</p>
          <p style="font-size:11px;color:var(--ink-3);margin:2px 0 0;">{{ user.email }}</p>
        </div>

        <div style="display:flex;flex-direction:column;gap:2px;">
          <template v-for="group in navGroups" :key="group.label">
            <p style="font-size:10px;text-transform:uppercase;letter-spacing:.7px;font-weight:500;color:var(--ink-4);margin:12px 0 4px 4px;">
              {{ group.label }}
            </p>
            <NuxtLink
              v-for="item in group.items"
              :key="item.to"
              :to="item.to"
              class="mobile-menu-item"
              :class="{ 'mobile-menu-item--active': isActive(item) }"
              @click="mobileMenuOpen = false"
            >
              <UIcon :name="item.icon" style="width:17px;height:17px;flex-shrink:0;" />
              {{ item.label }}
            </NuxtLink>
          </template>

          <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--line);">
            <NuxtLink to="/settings" class="mobile-menu-item" @click="mobileMenuOpen = false">
              <UIcon name="i-heroicons-user-circle" style="width:17px;height:17px;flex-shrink:0;" />
              Profil &amp; paramètres
            </NuxtLink>
            <button class="mobile-menu-item" @click="toggleTheme">
              <UIcon :name="isDark ? 'i-heroicons-sun' : 'i-heroicons-moon'" style="width:17px;height:17px;flex-shrink:0;" />
              {{ isDark ? 'Mode clair' : 'Mode sombre' }}
            </button>
            <button class="mobile-menu-item" style="color:var(--danger);" @click="mobileMenuOpen = false; logout()">
              <UIcon name="i-heroicons-arrow-right-on-rectangle" style="width:17px;height:17px;flex-shrink:0;" />
              Déconnexion
            </button>
          </div>
        </div>
      </div>
    </USlideover>

    <!-- ── Mobile bottom nav ──────────────────────────────────────── -->
    <nav v-if="isAuthenticated" class="bottom-nav">
      <NuxtLink
        v-for="link in bottomNavLinks"
        :key="link.to"
        :to="link.to"
        class="bottom-nav-item"
        :class="{ 'bottom-nav-item--active': isActive(link) }"
      >
        <UIcon :name="link.icon" style="width:22px;height:22px;" />
        <span class="bottom-nav-label">{{ link.label }}</span>
      </NuxtLink>
    </nav>

    <!-- ── Modals ─────────────────────────────────────────────────── -->
    <KeyboardShortcutHelp v-model="showShortcutsHelp" />
    <SessionTimeoutModal />
  </div>
</template>

<script setup lang="ts">
const { user, isAuthenticated, logout } = useAuth()
const { registerShortcut } = useKeyboardShortcuts()
const { generateRecurring } = useTransactions()
const config = useRuntimeConfig()
useSessionTimeout()

const route = useRoute()
const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')
const appVersion = config.public.appVersion

const mobileMenuOpen = ref(false)
const showShortcutsHelp = ref(false)

const userInitial = computed(() => {
  const name = user.value?.username || user.value?.email || '?'
  return name.charAt(0).toUpperCase()
})

const toggleTheme = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}

const navGroups = [
  {
    label: 'Pilotage',
    items: [
      { to: '/',                   label: 'Dashboard',    icon: 'i-heroicons-home' },
      { to: '/transactions',       label: 'Transactions', icon: 'i-heroicons-arrows-right-left' },
      { to: '/accounts',           label: 'Comptes',      icon: 'i-heroicons-building-library' },
      { to: '/budgets',            label: 'Enveloppes',   icon: 'i-heroicons-envelope-open' },
      { to: '/savings',            label: 'Épargne',      icon: 'i-heroicons-banknotes' },
    ],
  },
  {
    label: 'Configuration',
    items: [
      { to: '/analyses',            label: 'Analyses',    icon: 'i-heroicons-chart-bar-square' },
      { to: '/recurring',          label: 'Récurrents',  icon: 'i-heroicons-arrow-path' },
      { to: '/categories',         label: 'Catégories',  icon: 'i-heroicons-tag' },
    ],
  },
]

const bottomNavLinks = [
  { to: '/',             label: 'Accueil',      icon: 'i-heroicons-home' },
  { to: '/transactions', label: 'Transactions', icon: 'i-heroicons-arrows-right-left' },
  { to: '/accounts',     label: 'Comptes',      icon: 'i-heroicons-building-library' },
  { to: '/budgets',      label: 'Enveloppes',   icon: 'i-heroicons-envelope-open' },
  { to: '/settings',     label: 'Plus',         icon: 'i-heroicons-ellipsis-horizontal-circle' },
]

const isActive = (item: { to: string }) => {
  if (item.to === '/') return route.path === '/'
  return route.path.startsWith(item.to)
}

const userMenuItems = computed(() => [
  [
    { label: 'Profil & paramètres', icon: 'i-heroicons-user-circle', click: () => navigateTo('/settings') },
  ],
  [
    { label: 'Déconnexion', icon: 'i-heroicons-arrow-right-on-rectangle', click: () => logout() },
  ],
])

onMounted(async () => {
  await generateRecurring()
  registerShortcut('?', () => { showShortcutsHelp.value = true }, {
    description: 'Afficher l\'aide des raccourcis clavier',
  })
})
</script>

<style scoped>
/* ── App shell ─────────────────────────────────────────────── */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
}

/* ── Sidebar ───────────────────────────────────────────────── */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--line);
  display: none;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
}
@media (min-width: 1024px) { .sidebar { display: flex; } }

/* Logo */
.sidebar-logo {
  padding: 18px 16px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.sidebar-logo-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.sidebar-app-name    { font-size: 14px; font-weight: 600; color: var(--ink); letter-spacing: -0.2px; line-height: 1.2; }
.sidebar-app-version { font-size: 10px; color: var(--ink-4); line-height: 1.2; }

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 4px 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.sidebar-group-label {
  font-size: 10px;
  color: var(--ink-4);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 600;
  padding: 6px 8px 4px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 10px;
  height: 34px;
  border-radius: 7px;
  color: var(--ink-2);
  font-size: 13px;
  font-weight: 400;
  text-decoration: none;
  transition: background 0.1s, color 0.1s;
}
.sidebar-item:hover { background: var(--surface-2); }
.sidebar-item--active {
  color: var(--accent);
  background: var(--accent-soft);
  font-weight: 500;
}
.sidebar-item-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: var(--ink-3);
}
.sidebar-item--active .sidebar-item-icon { color: var(--accent); }

/* Footer */
.sidebar-footer {
  padding: 10px;
  border-top: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sidebar-theme-btn {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 7px 10px;
  height: 34px;
  border-radius: 7px;
  font-size: 13px;
  color: var(--ink-2);
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: background 0.1s;
}
.sidebar-theme-btn:hover { background: var(--surface-2); }

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 7px 10px;
  border-radius: 7px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;
}
.sidebar-user:hover { background: var(--surface-2); }
.sidebar-user-avatar {
  width: 28px; height: 28px; border-radius: 7px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
  color: #fff; display: grid; place-items: center;
  font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.sidebar-user-info { flex: 1; min-width: 0; }
.sidebar-user-name  { font-size: 12.5px; font-weight: 500; color: var(--ink); line-height: 1.2; }
.sidebar-user-email { font-size: 10.5px; color: var(--ink-3); line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── Main area ─────────────────────────────────────────────── */
.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* Mobile topbar */
.mobile-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 52px;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 30;
}
@media (min-width: 1024px) { .mobile-topbar { display: none; } }

/* Page content */
.page-content {
  flex: 1;
  padding-bottom: 72px;
}
@media (min-width: 1024px) { .page-content { padding-bottom: 0; } }

/* ── Mobile menu items ─────────────────────────────────────── */
.mobile-menu-item {
  display: flex; align-items: center; gap: 10px; width: 100%;
  padding: 8px 10px; border-radius: 7px; font-size: 13.5px;
  color: var(--ink-2); background: transparent; border: none;
  cursor: pointer; text-decoration: none; transition: background 0.1s;
  font-family: inherit;
}
.mobile-menu-item:hover { background: var(--surface-2); }
.mobile-menu-item--active { color: var(--accent); background: var(--accent-soft); font-weight: 500; }

/* ── Bottom nav ────────────────────────────────────────────── */
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 60px; background: var(--surface); border-top: 1px solid var(--line);
  display: grid; grid-template-columns: repeat(5, 1fr);
  z-index: 40; padding-bottom: env(safe-area-inset-bottom);
}
@media (min-width: 1024px) { .bottom-nav { display: none; } }
.bottom-nav-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 3px; text-decoration: none; color: var(--ink-3); transition: color 0.12s;
}
.bottom-nav-item--active { color: var(--accent); }
.bottom-nav-label { font-size: 10px; font-weight: 500; }
</style>
