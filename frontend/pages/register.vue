<template>
  <NuxtLayout name="auth">
    <div class="space-y-6">
      <div>
        <h2 class="text-center text-2xl font-bold text-gray-900 dark:text-white">
          Créer un compte
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Rejoignez Budget Tracker et prenez le contrôle de vos finances
        </p>
      </div>

      <!-- Registration Form -->
      <UForm :state="registerForm" :validate="validate" @submit="handleRegister">
        <div class="space-y-4">
          <!-- Username -->
          <UFormGroup label="Nom d'utilisateur" name="username" required>
            <UInput
              v-model="registerForm.username"
              placeholder="Choisissez un nom d'utilisateur"
              autocomplete="username"
              :disabled="loading"
            />
          </UFormGroup>

          <!-- Email -->
          <UFormGroup label="Email" name="email" required>
            <UInput
              v-model="registerForm.email"
              type="email"
              placeholder="votre@email.com"
              autocomplete="email"
              :disabled="loading"
            />
          </UFormGroup>

          <!-- First Name (optional) -->
          <UFormGroup label="Prénom" name="first_name">
            <UInput
              v-model="registerForm.first_name"
              placeholder="Votre prénom"
              autocomplete="given-name"
              :disabled="loading"
            />
          </UFormGroup>

          <!-- Last Name (optional) -->
          <UFormGroup label="Nom" name="last_name">
            <UInput
              v-model="registerForm.last_name"
              placeholder="Votre nom"
              autocomplete="family-name"
              :disabled="loading"
            />
          </UFormGroup>

          <!-- Password -->
          <UFormGroup label="Mot de passe" name="password" required>
            <UInput
              v-model="registerForm.password"
              type="password"
              placeholder="Créez un mot de passe sécurisé"
              autocomplete="new-password"
              :disabled="loading"
            />
            <template #help>
              <p class="text-xs text-gray-500 mt-1">
                Minimum 8 caractères, incluant majuscules, minuscules et chiffres
              </p>
            </template>
          </UFormGroup>

          <!-- Confirm Password -->
          <UFormGroup label="Confirmer le mot de passe" name="confirmPassword" required>
            <UInput
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="Confirmez votre mot de passe"
              autocomplete="new-password"
              :disabled="loading"
            />
          </UFormGroup>

          <!-- Error Display -->
          <UAlert
            v-if="error"
            color="red"
            variant="soft"
            icon="i-heroicons-exclamation-triangle"
            :title="error"
            :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'red', variant: 'link' }"
            @close="error = ''"
          />

          <!-- Field Errors -->
          <div v-if="fieldErrors && Object.keys(fieldErrors).length > 0" class="space-y-2">
            <UAlert
              v-for="(errors, field) in fieldErrors"
              :key="field"
              color="red"
              variant="soft"
              :title="`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`"
            />
          </div>

          <!-- Submit Button -->
          <UButton
            type="submit"
            block
            size="lg"
            :loading="loading"
            :disabled="loading"
          >
            Créer mon compte
          </UButton>
        </div>
      </UForm>

      <!-- Success State - Register Passkey -->
      <div v-if="showPasskeyOption" class="space-y-4">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300 dark:border-gray-600" />
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white dark:bg-gray-800 text-gray-500">
              Optionnel
            </span>
          </div>
        </div>

        <UCard>
          <div class="text-center space-y-4">
            <div class="mx-auto h-12 w-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <UIcon name="i-heroicons-finger-print" class="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Enregistrer une Passkey
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Sécurisez votre compte avec une passkey (compatible avec Proton Pass)
              </p>
            </div>
            <div class="flex gap-3 justify-center">
              <UButton
                color="primary"
                :loading="loadingPasskey"
                @click="handleRegisterPasskey"
              >
                Enregistrer une Passkey
              </UButton>
              <UButton
                color="white"
                @click="skipPasskey"
              >
                Plus tard
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Login Link -->
      <div class="text-center text-sm">
        <span class="text-gray-500">Déjà un compte ?</span>
        <NuxtLink to="/login" class="font-medium text-primary-600 hover:text-primary-500 ml-1">
          Se connecter
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

const { register } = useAuth();
const { registerWebAuthn } = useWebAuthn();
const router = useRouter();

const registerForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const loadingPasskey = ref(false);
const error = ref('');
const fieldErrors = ref<Record<string, string[]>>({});
const showPasskeyOption = ref(false);

// Form validation
const validate = (state: any) => {
  const errors = [];

  if (!state.username) {
    errors.push({ path: 'username', message: 'Le nom d\'utilisateur est requis' });
  }

  if (!state.email) {
    errors.push({ path: 'email', message: 'L\'email est requis' });
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email)) {
    errors.push({ path: 'email', message: 'Email invalide' });
  }

  if (!state.password) {
    errors.push({ path: 'password', message: 'Le mot de passe est requis' });
  } else if (state.password.length < 8) {
    errors.push({ path: 'password', message: 'Le mot de passe doit contenir au moins 8 caractères' });
  }

  if (!state.confirmPassword) {
    errors.push({ path: 'confirmPassword', message: 'Veuillez confirmer le mot de passe' });
  } else if (state.password !== state.confirmPassword) {
    errors.push({ path: 'confirmPassword', message: 'Les mots de passe ne correspondent pas' });
  }

  return errors;
};

const handleRegister = async () => {
  loading.value = true;
  error.value = '';
  fieldErrors.value = {};

  // Rename confirmPassword to password2 for Django backend
  const { confirmPassword, ...rest } = registerForm;
  const userData = {
    ...rest,
    password2: confirmPassword
  };

  const result = await register(userData);

  if (result.success) {
    showPasskeyOption.value = true;
  } else {
    if (typeof result.error === 'string') {
      error.value = result.error;
    } else if (result.errors) {
      fieldErrors.value = result.errors;
    }
  }

  loading.value = false;
};

const handleRegisterPasskey = async () => {
  loadingPasskey.value = true;
  error.value = '';

  const result = await registerWebAuthn(registerForm.username);

  if (result.success) {
    router.push('/');
  } else {
    error.value = result.error || 'Erreur lors de l\'enregistrement de la passkey';
  }

  loadingPasskey.value = false;
};

const skipPasskey = () => {
  router.push('/');
};
</script>
