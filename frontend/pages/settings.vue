<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Paramètres
      </h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">
        Gérez vos paramètres et préférences
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-400" />
    </div>

    <!-- Settings Content -->
    <div v-else class="space-y-6">
      <!-- Profile Section -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              Informations du profil
            </h2>
            <UButton
              v-if="!editingProfile"
              size="sm"
              variant="soft"
              icon="i-heroicons-pencil"
              @click="editingProfile = true"
            >
              Modifier
            </UButton>
          </div>
        </template>

        <div v-if="!editingProfile" class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Nom d'utilisateur</label>
            <p class="mt-1 text-base text-gray-900 dark:text-white">{{ profile?.username }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Email</label>
            <p class="mt-1 text-base text-gray-900 dark:text-white">{{ profile?.email }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Revenu mensuel</label>
            <p class="mt-1 text-base text-gray-900 dark:text-white">{{ formatCurrency(profile?.monthly_income || 0) }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Devise par défaut</label>
            <p class="mt-1 text-base text-gray-900 dark:text-white">{{ profile?.currency || 'CHF' }}</p>
          </div>
        </div>

        <form v-else @submit.prevent="handleProfileUpdate" class="space-y-4">
          <UFormGroup label="Nom d'utilisateur" :error="profileErrors.username">
            <UInput
              v-model="profileForm.username"
              placeholder="Nom d'utilisateur"
              disabled
            />
            <template #help>
              <span class="text-xs text-gray-500">Le nom d'utilisateur ne peut pas être modifié</span>
            </template>
          </UFormGroup>

          <UFormGroup label="Email" :error="profileErrors.email">
            <UInput
              v-model="profileForm.email"
              type="email"
              placeholder="email@example.com"
              disabled
            />
            <template #help>
              <span class="text-xs text-gray-500">L'email ne peut pas être modifié</span>
            </template>
          </UFormGroup>

          <UFormGroup label="Revenu mensuel (CHF)" :error="profileErrors.monthly_income">
            <UInput
              v-model="profileForm.monthly_income"
              type="number"
              step="0.01"
              placeholder="0.00"
              icon="i-heroicons-banknotes"
            />
          </UFormGroup>

          <UFormGroup label="Devise par défaut" :error="profileErrors.currency">
            <USelectMenu
              v-model="profileForm.currency"
              :options="currencies"
            />
          </UFormGroup>

          <div class="flex justify-end gap-2">
            <UButton
              type="button"
              variant="soft"
              @click="cancelProfileEdit"
            >
              Annuler
            </UButton>
            <UButton
              type="submit"
              :loading="submitting"
            >
              Enregistrer
            </UButton>
          </div>
        </form>
      </UCard>

      <!-- Password Section -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              Sécurité
            </h2>
            <UButton
              v-if="!changingPassword"
              size="sm"
              variant="soft"
              icon="i-heroicons-lock-closed"
              @click="changingPassword = true"
            >
              Changer le mot de passe
            </UButton>
          </div>
        </template>

        <div v-if="!changingPassword" class="text-gray-600 dark:text-gray-400">
          <p>Dernière modification du mot de passe : Jamais</p>
        </div>

        <form v-else @submit.prevent="handlePasswordChange" class="space-y-4">
          <UFormGroup label="Mot de passe actuel" required :error="passwordErrors.current_password">
            <UInput
              v-model="passwordForm.current_password"
              type="password"
              placeholder="••••••••"
            />
          </UFormGroup>

          <UFormGroup label="Nouveau mot de passe" required :error="passwordErrors.new_password">
            <UInput
              v-model="passwordForm.new_password"
              type="password"
              placeholder="••••••••"
            />
          </UFormGroup>

          <UFormGroup label="Confirmer le nouveau mot de passe" required :error="passwordErrors.confirm_password">
            <UInput
              v-model="passwordForm.confirm_password"
              type="password"
              placeholder="••••••••"
            />
          </UFormGroup>

          <div class="flex justify-end gap-2">
            <UButton
              type="button"
              variant="soft"
              @click="cancelPasswordChange"
            >
              Annuler
            </UButton>
            <UButton
              type="submit"
              :loading="submitting"
            >
              Changer le mot de passe
            </UButton>
          </div>
        </form>
      </UCard>

      <!-- Passkeys Section -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                Passkeys
              </h2>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Gérez vos passkeys pour une authentification sécurisée sans mot de passe
              </p>
            </div>
            <UButton
              size="sm"
              icon="i-heroicons-plus"
              @click="handleAddPasskey"
              :loading="addingPasskey"
            >
              Ajouter une Passkey
            </UButton>
          </div>
        </template>

        <!-- Loading State -->
        <div v-if="loadingCredentials" class="flex justify-center py-8">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin h-6 w-6 text-gray-400" />
        </div>

        <!-- Empty State -->
        <div v-else-if="credentials.length === 0" class="text-center py-8">
          <UIcon name="i-heroicons-finger-print" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p class="text-gray-600 dark:text-gray-400">
            Aucune passkey enregistrée. Ajoutez-en une pour vous connecter rapidement et en toute sécurité.
          </p>
        </div>

        <!-- Credentials List -->
        <div v-else class="space-y-3">
          <div
            v-for="credential in credentials"
            :key="credential.id"
            class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
          >
            <div class="flex items-center gap-3">
              <UIcon name="i-heroicons-finger-print" class="h-6 w-6 text-primary-600" />
              <div>
                <p class="font-medium text-gray-900 dark:text-white">
                  {{ credential.device_name || 'Passkey sans nom' }}
                </p>
                <div class="text-sm text-gray-500 dark:text-gray-400 space-x-3">
                  <span>Créée le {{ formatDate(credential.created_at) }}</span>
                  <span v-if="credential.last_used">
                    • Dernière utilisation: {{ formatDate(credential.last_used) }}
                  </span>
                </div>
              </div>
            </div>
            <UButton
              color="red"
              variant="ghost"
              icon="i-heroicons-trash"
              aria-label="Supprimer la passkey"
              @click="confirmDeleteCredential(credential.id)"
              :loading="deletingCredentialId === credential.id"
            />
          </div>
        </div>
      </UCard>

      <!-- API Tokens Section -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                Tokens API (iOS Shortcuts)
              </h2>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Gérez vos tokens pour l'intégration avec iOS Shortcuts
              </p>
            </div>
            <UButton
              size="sm"
              icon="i-heroicons-plus"
              @click="showTokenModal = true"
            >
              Générer un token
            </UButton>
          </div>
        </template>

        <!-- Loading State -->
        <div v-if="loadingTokens" class="flex justify-center py-8">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin h-6 w-6 text-gray-400" />
        </div>

        <!-- Empty State -->
        <div v-else-if="apiTokens.length === 0" class="text-center py-8">
          <UIcon name="i-heroicons-device-phone-mobile" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p class="text-gray-600 dark:text-gray-400">
            Aucun token API. Créez-en un pour envoyer des transactions depuis iOS Shortcuts.
          </p>
        </div>

        <!-- Tokens List -->
        <div v-else class="space-y-3">
          <div
            v-for="token in apiTokens"
            :key="token.id"
            class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
          >
            <div class="flex items-center gap-3">
              <UIcon name="i-heroicons-key" class="h-6 w-6 text-primary-600" />
              <div>
                <p class="font-medium text-gray-900 dark:text-white">
                  {{ token.name }}
                </p>
                <div class="text-sm text-gray-500 dark:text-gray-400 space-x-3">
                  <span>Créé le {{ formatDate(token.created_at) }}</span>
                  <span v-if="token.last_used">
                    &bull; Dernier usage: {{ formatDate(token.last_used) }}
                  </span>
                </div>
              </div>
            </div>
            <UButton
              color="red"
              variant="ghost"
              icon="i-heroicons-trash"
              aria-label="Révoquer le token"
              @click="confirmDeleteToken(token.id)"
              :loading="deletingTokenId === token.id"
            />
          </div>
        </div>
      </UCard>

      <!-- Token Creation Modal -->
      <UModal v-model="showTokenModal">
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">
              {{ newTokenValue ? 'Token créé' : 'Nouveau token API' }}
            </h3>
          </template>

          <!-- Creation Form -->
          <div v-if="!newTokenValue" class="space-y-4">
            <UFormGroup label="Nom du token" required>
              <UInput
                v-model="newTokenName"
                placeholder="Ex: iPhone de Reist"
                icon="i-heroicons-device-phone-mobile"
              />
            </UFormGroup>
            <div class="flex justify-end gap-2">
              <UButton variant="ghost" color="gray" @click="showTokenModal = false">
                Annuler
              </UButton>
              <UButton @click="handleCreateToken" :loading="creatingToken" :disabled="!newTokenName">
                Générer
              </UButton>
            </div>
          </div>

          <!-- Token Display (shown once) -->
          <div v-else class="space-y-4">
            <UAlert
              color="orange"
              variant="soft"
              icon="i-heroicons-exclamation-triangle"
              title="Copiez ce token maintenant"
              description="Ce token ne sera plus affiché. Conservez-le dans un endroit sûr."
            />
            <div class="relative">
              <UInput
                :model-value="newTokenValue"
                readonly
                class="font-mono text-sm"
              />
              <UButton
                class="absolute right-1 top-1"
                size="xs"
                variant="ghost"
                icon="i-heroicons-clipboard-document"
                @click="copyToken"
              />
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg text-sm">
              <p class="font-medium mb-1">Utilisation dans iOS Shortcuts :</p>
              <code class="text-xs break-all">
                POST {{ apiBase }}/api/v1/ios/transaction/<br>
                Authorization: Bearer {{ newTokenValue }}<br>
                Body: { "amount": 12.50, "label": "Courses", "category": "Alimentation" }
              </code>
            </div>
            <div class="flex justify-end">
              <UButton @click="closeTokenModal">
                Fermer
              </UButton>
            </div>
          </div>
        </UCard>
      </UModal>

      <!-- Confirm Delete Passkey Modal -->
      <ConfirmModal
        v-model="showConfirmDeleteCredential"
        title="Supprimer la passkey"
        message="Êtes-vous sûr de vouloir supprimer cette passkey ? Vous ne pourrez plus l'utiliser pour vous connecter."
        confirm-label="Supprimer"
        @confirm="executeDeleteCredential"
      />

      <!-- Confirm Delete Token Modal -->
      <ConfirmModal
        v-model="showConfirmDeleteToken"
        title="Révoquer le token"
        message="Êtes-vous sûr de vouloir révoquer ce token ? Les raccourcis iOS utilisant ce token ne fonctionneront plus."
        confirm-label="Révoquer"
        confirm-color="red"
        icon="i-heroicons-key"
        @confirm="executeDeleteToken"
      />

      <!-- Delete Account - Step 1: Password -->
      <ConfirmModal
        v-model="showDeleteAccountModal"
        v-if="deleteAccountStep === 1"
        title="Supprimer le compte"
        message="Pour confirmer, entrez votre mot de passe :"
        confirm-label="Continuer"
        confirm-color="red"
        require-input
        input-label="Mot de passe"
        input-type="password"
        input-placeholder="Votre mot de passe"
        @confirm="handleDeleteAccountStep1"
      />

      <!-- Delete Account - Step 2: Type DELETE -->
      <ConfirmModal
        v-model="showDeleteAccountModal"
        v-if="deleteAccountStep === 2"
        title="Confirmer la suppression"
        message="Cette action est irréversible. Tapez « DELETE » pour confirmer la suppression définitive de votre compte :"
        confirm-label="Supprimer définitivement"
        confirm-color="red"
        require-input
        input-label="Confirmation"
        input-placeholder="DELETE"
        expected-input="DELETE"
        @confirm="handleDeleteAccountStep2"
      />

      <!-- Account Info Section -->
      <UCard>
        <template #header>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Informations du compte
          </h2>
        </template>

        <div class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Compte créé le</label>
            <p class="mt-1 text-base text-gray-900 dark:text-white">
              {{ profile?.date_joined ? new Date(profile.date_joined).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              }) : 'N/A' }}
            </p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500 dark:text-gray-400">Dernière connexion</label>
            <p class="mt-1 text-base text-gray-900 dark:text-white">
              {{ profile?.last_login ? new Date(profile.last_login).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              }) : 'Jamais' }}
            </p>
          </div>
        </div>
      </UCard>

      <!-- Danger Zone -->
      <UCard class="border-red-200 dark:border-red-800">
        <template #header>
          <h2 class="text-lg font-semibold text-red-600 dark:text-red-400">
            Zone de danger
          </h2>
        </template>

        <div class="space-y-4">
          <div>
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-2">
              Supprimer le compte
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Une fois votre compte supprimé, toutes vos données seront définitivement effacées. Cette action est irréversible.
            </p>
            <UButton
              color="red"
              variant="soft"
              icon="i-heroicons-trash"
              @click="confirmDeleteAccount"
            >
              Supprimer mon compte
            </UButton>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { getProfile, updateProfile, changePassword, deleteAccount } = useUserProfile()
const { logout } = useAuth()
const { registerWebAuthn, listCredentials, deleteCredential } = useWebAuthn()
const { getTokens, createToken, deleteToken } = useApiTokens()
const toast = useToast()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

// State
const profile = ref<any>(null)
const loading = ref(true)
const submitting = ref(false)
const editingProfile = ref(false)
const changingPassword = ref(false)

// Passkeys State
const credentials = ref<any[]>([])
const loadingCredentials = ref(false)
const addingPasskey = ref(false)
const deletingCredentialId = ref<number | null>(null)

// API Tokens State
const apiTokens = ref<any[]>([])
const loadingTokens = ref(false)
const showTokenModal = ref(false)
const newTokenName = ref('')
const newTokenValue = ref('')
const creatingToken = ref(false)
const deletingTokenId = ref<number | null>(null)

// Forms
const profileForm = ref({
  username: '',
  email: '',
  monthly_income: '',
  currency: 'CHF'
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// Errors
const profileErrors = ref<Record<string, string>>({})
const passwordErrors = ref<Record<string, string>>({})

// Options
const currencies = ['CHF', 'EUR', 'USD', 'GBP']

// Fetch profile
const fetchProfile = async () => {
  loading.value = true
  const result = await getProfile()

  if (result.success && result.data) {
    profile.value = result.data
    profileForm.value = {
      username: result.data.username || '',
      email: result.data.email || '',
      monthly_income: result.data.monthly_income || '',
      currency: result.data.currency || 'CHF'
    }
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de charger le profil',
      color: 'red'
    })
  }

  loading.value = false
}

// Handle profile update
const handleProfileUpdate = async () => {
  submitting.value = true
  profileErrors.value = {}

  const result = await updateProfile({
    monthly_income: profileForm.value.monthly_income,
    currency: profileForm.value.currency
  })

  submitting.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Profil mis à jour avec succès',
      color: 'green'
    })
    editingProfile.value = false
    await fetchProfile()
  } else {
    if (result.error?.data) {
      const errors = result.error.data
      Object.keys(errors).forEach(key => {
        if (Array.isArray(errors[key])) {
          profileErrors.value[key] = errors[key][0]
        } else if (typeof errors[key] === 'string') {
          profileErrors.value[key] = errors[key]
        }
      })
    }
    toast.add({
      title: 'Erreur',
      description: 'Impossible de mettre à jour le profil',
      color: 'red'
    })
  }
}

// Cancel profile edit
const cancelProfileEdit = () => {
  editingProfile.value = false
  profileErrors.value = {}
  if (profile.value) {
    profileForm.value = {
      username: profile.value.username || '',
      email: profile.value.email || '',
      monthly_income: profile.value.monthly_income || '',
      currency: profile.value.currency || 'CHF'
    }
  }
}

// Handle password change
const handlePasswordChange = async () => {
  submitting.value = true
  passwordErrors.value = {}

  // Validate passwords match
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordErrors.value.confirm_password = 'Les mots de passe ne correspondent pas'
    submitting.value = false
    return
  }

  // Validate password length
  if (passwordForm.value.new_password.length < 8) {
    passwordErrors.value.new_password = 'Le mot de passe doit contenir au moins 8 caractères'
    submitting.value = false
    return
  }

  const result = await changePassword({
    current_password: passwordForm.value.current_password,
    new_password: passwordForm.value.new_password
  })

  submitting.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Mot de passe changé avec succès',
      color: 'green'
    })
    changingPassword.value = false
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } else {
    if (result.error?.data?.error) {
      toast.add({
        title: 'Erreur',
        description: result.error.data.error,
        color: 'red'
      })
    } else {
      toast.add({
        title: 'Erreur',
        description: 'Impossible de changer le mot de passe',
        color: 'red'
      })
    }
  }
}

// Cancel password change
const cancelPasswordChange = () => {
  changingPassword.value = false
  passwordErrors.value = {}
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// Account deletion modal state
const showDeleteAccountModal = ref(false)
const deleteAccountStep = ref<1 | 2>(1)
const deleteAccountPassword = ref('')

const confirmDeleteAccount = () => {
  deleteAccountStep.value = 1
  deleteAccountPassword.value = ''
  showDeleteAccountModal.value = true
}

const handleDeleteAccountStep1 = (inputValue?: string) => {
  if (inputValue) {
    deleteAccountPassword.value = inputValue
    deleteAccountStep.value = 2
    // Re-open for step 2
    nextTick(() => {
      showDeleteAccountModal.value = true
    })
  }
}

const handleDeleteAccountStep2 = async (inputValue?: string) => {
  if (inputValue !== 'DELETE') {
    toast.add({
      title: 'Annulé',
      description: 'Suppression annulée — vous devez taper exactement "DELETE"',
      color: 'gray'
    })
    return
  }

  const result = await deleteAccount({
    password: deleteAccountPassword.value,
    confirm: inputValue
  })

  if (result.success) {
    toast.add({
      title: 'Compte supprimé',
      description: 'Votre compte a été supprimé avec succès',
      color: 'green'
    })
    setTimeout(() => {
      logout()
    }, 2000)
  } else {
    if (result.error?.data?.error) {
      toast.add({
        title: 'Erreur',
        description: result.error.data.error,
        color: 'red'
      })
    } else {
      toast.add({
        title: 'Erreur',
        description: 'Impossible de supprimer le compte',
        color: 'red'
      })
    }
  }
}

// Fetch credentials
const fetchCredentials = async () => {
  loadingCredentials.value = true
  const result = await listCredentials()

  if (result.success) {
    credentials.value = result.data || []
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de charger les passkeys',
      color: 'red'
    })
  }

  loadingCredentials.value = false
}

// Handle add passkey
const handleAddPasskey = async () => {
  if (!profile.value) {
    toast.add({
      title: 'Erreur',
      description: 'Profil non chargé',
      color: 'red'
    })
    return
  }

  addingPasskey.value = true

  const result = await registerWebAuthn(profile.value.username)

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Passkey ajoutée avec succès',
      color: 'green'
    })
    await fetchCredentials()
  } else {
    toast.add({
      title: 'Erreur',
      description: result.error || 'Impossible d\'ajouter la passkey',
      color: 'red'
    })
  }

  addingPasskey.value = false
}

// Confirm delete credential
const showConfirmDeleteCredential = ref(false)
const credentialToDelete = ref<number | null>(null)

const confirmDeleteCredential = (credentialId: number) => {
  credentialToDelete.value = credentialId
  showConfirmDeleteCredential.value = true
}

const executeDeleteCredential = async () => {
  if (credentialToDelete.value === null) return
  deletingCredentialId.value = credentialToDelete.value

  const result = await deleteCredential(credentialToDelete.value)
  credentialToDelete.value = null

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Passkey supprimée avec succès',
      color: 'green'
    })
    await fetchCredentials()
  } else {
    toast.add({
      title: 'Erreur',
      description: result.error || 'Impossible de supprimer la passkey',
      color: 'red'
    })
  }

  deletingCredentialId.value = null
}

// Utility functions
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: 'CHF'
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// API Tokens functions
const fetchTokens = async () => {
  loadingTokens.value = true
  const result = await getTokens()
  if (result.success && result.data) {
    apiTokens.value = result.data
  }
  loadingTokens.value = false
}

const handleCreateToken = async () => {
  creatingToken.value = true
  const result = await createToken(newTokenName.value)
  creatingToken.value = false

  if (result.success && result.data) {
    newTokenValue.value = result.data.token || ''
    await fetchTokens()
    toast.add({
      title: 'Token créé',
      description: 'Copiez-le maintenant, il ne sera plus affiché.',
      color: 'green'
    })
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de créer le token',
      color: 'red'
    })
  }
}

const closeTokenModal = () => {
  showTokenModal.value = false
  newTokenName.value = ''
  newTokenValue.value = ''
}

const copyToken = async () => {
  try {
    await navigator.clipboard.writeText(newTokenValue.value)
    toast.add({
      title: 'Copié',
      description: 'Token copié dans le presse-papier',
      color: 'green'
    })
  } catch {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de copier le token',
      color: 'red'
    })
  }
}

// Confirm delete token
const showConfirmDeleteToken = ref(false)
const tokenToDelete = ref<number | null>(null)

const confirmDeleteToken = (tokenId: number) => {
  tokenToDelete.value = tokenId
  showConfirmDeleteToken.value = true
}

const executeDeleteToken = async () => {
  if (tokenToDelete.value === null) return
  deletingTokenId.value = tokenToDelete.value
  const result = await deleteToken(tokenToDelete.value)
  tokenToDelete.value = null
  if (result.success) {
    toast.add({
      title: 'Token révoqué',
      description: 'Le token a été supprimé',
      color: 'green'
    })
    await fetchTokens()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de révoquer le token',
      color: 'red'
    })
  }
  deletingTokenId.value = null
}

// Lifecycle
onMounted(() => {
  fetchProfile()
  fetchCredentials()
  fetchTokens()
})
</script>
