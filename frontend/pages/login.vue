<template>
  <NuxtLayout name="auth">
    <div class="space-y-6">
      <div>
        <h2 class="text-center text-2xl font-bold text-gray-900 dark:text-white">
          Connexion à votre compte
        </h2>
      </div>

      <!-- WebAuthn Login -->
      <div>
        <UButton
          block
          size="lg"
          color="primary"
          icon="i-heroicons-finger-print"
          :loading="loadingWebAuthn"
          @click="handleWebAuthnLogin"
        >
          Se connecter avec Passkey
        </UButton>
      </div>

      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300 dark:border-gray-600" />
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white dark:bg-gray-800 text-gray-500">
            Ou continuer avec
          </span>
        </div>
      </div>

      <!-- Traditional Login Form -->
      <UForm :state="loginForm" @submit="handleLogin">
        <div class="space-y-4">
          <UFormGroup label="Nom d'utilisateur" name="username" required>
            <UInput
              v-model="loginForm.username"
              placeholder="Entrez votre nom d'utilisateur"
              autocomplete="username"
            />
          </UFormGroup>

          <UFormGroup label="Mot de passe" name="password" required>
            <UInput
              v-model="loginForm.password"
              type="password"
              placeholder="Entrez votre mot de passe"
              autocomplete="current-password"
            />
          </UFormGroup>

          <div v-if="error" class="text-sm text-red-600 dark:text-red-400">
            {{ error }}
          </div>

          <UButton
            type="submit"
            block
            size="lg"
            :loading="loading"
          >
            Se connecter
          </UButton>
        </div>
      </UForm>

      <div class="text-center text-sm">
        <span class="text-gray-500">Pas encore de compte ?</span>
        <NuxtLink to="/register" class="font-medium text-primary-600 hover:text-primary-500 ml-1">
          S'inscrire
        </NuxtLink>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
  middleware: 'guest'
});

const { login } = useAuth();
const { authenticateWebAuthn } = useWebAuthn();
const router = useRouter();

const loginForm = reactive({
  username: '',
  password: '',
});

const loading = ref(false);
const loadingWebAuthn = ref(false);
const error = ref('');

const handleLogin = async () => {
  loading.value = true;
  error.value = '';

  const result = await login(loginForm.username, loginForm.password);

  if (result.success) {
    router.push('/');
  } else {
    error.value = result.error || 'Une erreur est survenue';
  }

  loading.value = false;
};

const handleWebAuthnLogin = async () => {
  loadingWebAuthn.value = true;
  error.value = '';

  const result = await authenticateWebAuthn();

  if (result.success) {
    router.push('/');
  } else {
    error.value = result.error || 'Authentification échouée';
  }

  loadingWebAuthn.value = false;
};
</script>
