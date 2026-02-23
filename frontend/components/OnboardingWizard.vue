<template>
  <UModal v-model="isOpen" :ui="{ width: 'sm:max-w-2xl' }" :prevent-close="currentStep < 3">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
              {{ steps[currentStep].title }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Étape {{ currentStep + 1 }} sur {{ steps.length }}
            </p>
          </div>
          <UButton
            v-if="currentStep === 0"
            color="gray"
            variant="ghost"
            size="sm"
            @click="skipOnboarding"
          >
            Passer
          </UButton>
        </div>
      </template>

      <!-- Progress bar -->
      <div class="mb-6">
        <UProgress :value="((currentStep + 1) / steps.length) * 100" color="primary" />
      </div>

      <!-- Step 0: Welcome -->
      <div v-if="currentStep === 0" class="space-y-6">
        <div class="text-center py-6">
          <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-primary-100 dark:bg-primary-900/20 mb-4">
            <UIcon name="i-heroicons-rocket-launch" class="h-12 w-12 text-primary-600" />
          </div>
          <h4 class="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Bienvenue dans Budget Tracker! 🎉
          </h4>
          <p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
            Prenez le contrôle de vos finances en quelques étapes simples.
            Ce guide rapide vous aidera à configurer votre application en moins de 2 minutes.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div class="flex items-center gap-3 mb-2">
              <UIcon name="i-heroicons-building-library" class="h-6 w-6 text-blue-600" />
              <span class="font-semibold text-gray-900 dark:text-white">Vos comptes</span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Ajoutez vos comptes bancaires pour suivre vos soldes
            </p>
          </div>

          <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div class="flex items-center gap-3 mb-2">
              <UIcon name="i-heroicons-tag" class="h-6 w-6 text-green-600" />
              <span class="font-semibold text-gray-900 dark:text-white">Catégories</span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Organisez vos dépenses et revenus par catégories
            </p>
          </div>

          <div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div class="flex items-center gap-3 mb-2">
              <UIcon name="i-heroicons-arrows-right-left" class="h-6 w-6 text-purple-600" />
              <span class="font-semibold text-gray-900 dark:text-white">Transactions</span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Enregistrez vos dépenses et revenus facilement
            </p>
          </div>
        </div>
      </div>

      <!-- Step 1: Create first account -->
      <div v-else-if="currentStep === 1" class="space-y-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
          <div class="flex items-start gap-3">
            <UIcon name="i-heroicons-information-circle" class="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div class="text-sm text-blue-700 dark:text-blue-400">
              <p class="font-medium mb-1">Pourquoi créer un compte?</p>
              <p>Un compte représente votre compte bancaire, portefeuille ou carte de crédit. Il vous permet de suivre où va votre argent.</p>
            </div>
          </div>
        </div>

        <UFormGroup label="Nom du compte" required>
          <UInput
            v-model="accountForm.name"
            placeholder="Ex: Compte Courant PostFinance"
            icon="i-heroicons-building-library"
          />
        </UFormGroup>

        <UFormGroup label="Type de compte" required>
          <USelectMenu
            v-model="accountForm.account_type"
            :options="accountTypes"
            value-attribute="value"
            option-attribute="label"
          />
        </UFormGroup>

        <UFormGroup :label="`Solde actuel (${currency})`" required>
          <UInput
            v-model="accountForm.balance"
            type="number"
            step="0.01"
            placeholder="1500.00"
            icon="i-heroicons-banknotes"
          />
          <template #help>
            <span class="text-xs text-gray-500">Le solde actuel de votre compte</span>
          </template>
        </UFormGroup>
      </div>

      <!-- Step 2: Setup categories -->
      <div v-else-if="currentStep === 2" class="space-y-4">
        <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-4">
          <div class="flex items-start gap-3">
            <UIcon name="i-heroicons-sparkles" class="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div class="text-sm text-green-700 dark:text-green-400">
              <p class="font-medium mb-1">Bonne nouvelle!</p>
              <p>Nous avons créé des catégories par défaut pour vous. Vous pourrez les personnaliser plus tard dans Configuration → Catégories.</p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <UIcon name="i-heroicons-arrow-trending-up" class="h-5 w-5 text-green-600" />
              <span class="font-medium text-sm text-gray-900 dark:text-white">Revenus</span>
            </div>
            <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Salaire</li>
              <li>• Bonus</li>
              <li>• Freelance</li>
              <li>• Autres revenus</li>
            </ul>
          </div>

          <div class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div class="flex items-center gap-2 mb-2">
              <UIcon name="i-heroicons-arrow-trending-down" class="h-5 w-5 text-red-600" />
              <span class="font-medium text-sm text-gray-900 dark:text-white">Dépenses</span>
            </div>
            <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Alimentation</li>
              <li>• Transport</li>
              <li>• Logement</li>
              <li>• Loisirs</li>
              <li>• Santé</li>
              <li>• + 5 autres</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Step 3: Congratulations -->
      <div v-else-if="currentStep === 3" class="space-y-6">
        <div class="text-center py-6">
          <div class="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 dark:bg-green-900/20 mb-4">
            <UIcon name="i-heroicons-check-circle" class="h-12 w-12 text-green-600" />
          </div>
          <h4 class="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Tout est prêt! 🎊
          </h4>
          <p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
            Votre compte a été créé et les catégories sont configurées.
            Vous pouvez maintenant commencer à enregistrer vos transactions!
          </p>
        </div>

        <div class="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4">
          <h5 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <UIcon name="i-heroicons-light-bulb" class="h-5 w-5 text-primary-600" />
            Astuces pour bien démarrer
          </h5>
          <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li class="flex items-start gap-2">
              <UIcon name="i-heroicons-check" class="h-4 w-4 text-primary-600 mt-0.5 flex-shrink-0" />
              <span>Utilisez <UKbd>{{ isMac ? '⌘' : 'Ctrl' }}</UKbd> <UKbd>N</UKbd> pour créer rapidement une transaction</span>
            </li>
            <li class="flex items-start gap-2">
              <UIcon name="i-heroicons-check" class="h-4 w-4 text-primary-600 mt-0.5 flex-shrink-0" />
              <span>Créez des budgets pour suivre vos dépenses mensuelles</span>
            </li>
            <li class="flex items-start gap-2">
              <UIcon name="i-heroicons-check" class="h-4 w-4 text-primary-600 mt-0.5 flex-shrink-0" />
              <span>Consultez le dashboard pour avoir une vue d'ensemble de vos finances</span>
            </li>
          </ul>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center">
          <UButton
            v-if="currentStep > 0 && currentStep < 3"
            color="gray"
            variant="ghost"
            @click="previousStep"
          >
            Retour
          </UButton>
          <div v-else></div>

          <UButton
            v-if="currentStep < 3"
            :loading="loading"
            @click="nextStep"
          >
            {{ currentStep === 0 ? 'Commencer' : 'Suivant' }}
          </UButton>
          <UButton
            v-else
            color="primary"
            @click="finishOnboarding"
          >
            Terminer et commencer
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
/**
 * OnboardingWizard Component
 *
 * Guide interactif de première utilisation qui accompagne l'utilisateur
 * dans la configuration initiale de l'application:
 * 1. Bienvenue et présentation
 * 2. Création du premier compte
 * 3. Configuration des catégories (auto)
 * 4. Félicitations et astuces
 *
 * @emits complete - Émis quand l'onboarding est terminé
 * @emits skip - Émis quand l'utilisateur passe l'onboarding
 */

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  complete: []
  skip: []
}>()

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const currentStep = ref(0)
const loading = ref(false)
const isMac = process.client && navigator.platform.toUpperCase().indexOf('MAC') >= 0

const steps = [
  { title: 'Bienvenue', description: 'Découvrez Budget Tracker' },
  { title: 'Créez votre premier compte', description: 'Configuration initiale' },
  { title: 'Catégories configurées', description: 'Organisation automatique' },
  { title: 'Tout est prêt!', description: 'Commencez à utiliser l\'application' }
]

const accountTypes = [
  { value: 'checking', label: 'Compte Courant' },
  { value: 'savings', label: 'Compte Épargne' },
  { value: 'credit_card', label: 'Carte de Crédit' },
  { value: 'cash', label: 'Espèces' }
]

const { currency } = useUserProfile()

const accountForm = ref({
  name: '',
  account_type: 'checking',
  balance: '0.00',
  currency: currency.value || 'CHF'
})

const { createAccount } = useAccounts()
const toast = useToast()

/**
 * Passe à l'étape suivante du wizard
 * Valide et sauvegarde les données si nécessaire
 */
const nextStep = async () => {
  // Step 1: Créer le compte
  if (currentStep.value === 1) {
    if (!accountForm.value.name || !accountForm.value.balance) {
      toast.add({
        title: 'Champs requis',
        description: 'Veuillez remplir tous les champs',
        color: 'red'
      })
      return
    }

    loading.value = true
    const result = await createAccount(accountForm.value)
    loading.value = false

    if (!result.success) {
      toast.add({
        title: 'Erreur',
        description: 'Impossible de créer le compte',
        color: 'red'
      })
      return
    }
  }

  currentStep.value++
}

/**
 * Retour à l'étape précédente
 */
const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

/**
 * Termine l'onboarding et ferme le wizard
 */
const finishOnboarding = () => {
  // Sauvegarder dans localStorage que l'onboarding est terminé
  if (process.client) {
    localStorage.setItem('onboarding_completed', 'true')
  }
  isOpen.value = false
  emit('complete')
}

/**
 * Passe l'onboarding
 */
const skipOnboarding = () => {
  if (process.client) {
    localStorage.setItem('onboarding_completed', 'true')
  }
  isOpen.value = false
  emit('skip')
}
</script>
