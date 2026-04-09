<template>
  <div>
    <div class="mb-6 sm:mb-8 flex justify-between items-center">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          Comptes
        </h1>
        <p class="mt-1 text-sm sm:text-base text-gray-600 dark:text-gray-400 hidden sm:block">
          Gérez vos comptes bancaires et leur solde
        </p>
      </div>
      <UButton icon="i-heroicons-plus" size="lg" class="sm:hidden" aria-label="Nouveau compte" @click="openAddModal" />
      <UButton icon="i-heroicons-plus" size="lg" class="hidden sm:inline-flex" @click="openAddModal">
        Nouveau compte
      </UButton>
    </div>

    <!-- Summary Cards -->
    <div v-if="summary" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <UCard v-for="(data, currency) in summary" :key="currency">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Total {{ currency }}</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ formatCurrency(data.total, currency) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ data.count }} compte{{ data.count > 1 ? 's' : '' }}
          </p>
        </div>
      </UCard>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <SkeletonCard v-for="i in 3" :key="i" :lines="4" show-header show-footer />
    </div>

    <!-- Error State -->
    <div v-else-if="loadError">
      <UCard>
        <EmptyState
          icon="i-heroicons-exclamation-circle"
          color="red"
          title="Impossible de charger les comptes"
          description="Vérifiez votre connexion internet et réessayez."
          button-text="Réessayer"
          button-icon="i-heroicons-arrow-path"
          @action="fetchAccounts(); fetchSummary()"
        />
      </UCard>
    </div>

    <!-- Accounts Grid -->
    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <UCard
        v-for="account in accounts"
        :key="account.id"
        class="hover:shadow-lg transition-shadow"
      >
        <template #header>
          <div class="flex justify-between items-start">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ account.name }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ account.account_type_display }}
              </p>
            </div>
            <UBadge
              :color="account.is_active ? 'green' : 'gray'"
              variant="subtle"
            >
              {{ account.is_active ? 'Actif' : 'Inactif' }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <div>
            <UTooltip text="Votre solde actuel, sans compter les transactions futures planifiées">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400 cursor-help">Solde actuel</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">
                  {{ formatCurrency(parseFloat(account.current_balance), account.currency) }}
                </p>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  (Excluant les transactions futures)
                </p>
              </div>
            </UTooltip>
          </div>

          <UTooltip v-if="account.projected_balance !== account.current_balance" text="Votre solde futur estimé en incluant toutes les transactions planifiées">
            <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 cursor-help">
              <p class="text-sm text-gray-600 dark:text-gray-400">Solde projeté</p>
              <p class="text-lg font-semibold text-blue-600 dark:text-blue-400">
                {{ formatCurrency(parseFloat(account.projected_balance), account.currency) }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                (Incluant les transactions futures)
              </p>
            </div>
          </UTooltip>

          <div v-if="account.description" class="text-sm text-gray-600 dark:text-gray-400">
            {{ account.description }}
          </div>

          <div class="flex gap-2">
            <UButton
              size="sm"
              variant="soft"
              icon="i-heroicons-pencil"
              @click="openEditModal(account)"
            >
              Modifier
            </UButton>
            <UButton
              size="sm"
              variant="soft"
              :color="account.is_active ? 'orange' : 'green'"
              icon="i-heroicons-power"
              @click="toggleActive(account)"
            >
              {{ account.is_active ? 'Désactiver' : 'Activer' }}
            </UButton>
            <UButton
              size="sm"
              variant="soft"
              color="red"
              icon="i-heroicons-trash"
              @click="confirmDelete(account)"
            >
              Supprimer
            </UButton>
          </div>
        </div>
      </UCard>

      <div v-if="accounts.length === 0 && !loading" class="col-span-full">
        <UCard>
          <EmptyState
            icon="i-heroicons-banknotes"
            color="blue"
            title="Créez votre premier compte 💳"
            description="Les comptes vous permettent de gérer votre argent de manière organisée. Ajoutez votre compte courant, épargne ou carte de crédit pour commencer!"
            button-text="Créer un compte"
            @action="openAddModal"
          />
        </UCard>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer le compte"
      :message="`Êtes-vous sûr de vouloir supprimer le compte « ${accountToDelete?.name} » ?`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- Add/Edit Modal -->
    <UModal v-model="showModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ editingAccount ? 'Modifier' : 'Ajouter' }} un compte
          </h3>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <UFormGroup label="Nom du compte" required>
            <UInput
              v-model="form.name"
              placeholder="Ex: Compte courant principal"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'name')" />
          </UFormGroup>

          <UFormGroup label="Type de compte" required>
            <USelectMenu
              v-model="form.account_type"
              :options="accountTypes"
              value-attribute="value"
              option-attribute="label"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'account_type')" />
          </UFormGroup>

          <UFormGroup :label="editingAccount ? 'Solde actuel' : 'Solde initial'" required>
            <UInput
              v-model="form.balance"
              type="number"
              step="0.01"
              placeholder="0.00"
            />
            <template #help>
              <span v-if="!editingAccount" class="text-xs text-gray-500">Le solde initial de votre compte</span>
              <span v-else class="text-xs text-gray-500">Modifiez le solde pour créer automatiquement une transaction d'ajustement. Cet ajustement n'affectera pas vos budgets ni vos statistiques.</span>
            </template>
            <FormFieldError :error="getErrorForField(formErrors, 'balance')" />
          </UFormGroup>

          <UFormGroup label="Devise" required>
            <USelectMenu
              v-model="form.currency"
              :options="currencies"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'currency')" />
          </UFormGroup>

          <UFormGroup label="Description">
            <UTextarea
              v-model="form.description"
              placeholder="Description optionnelle"
              :rows="3"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'description')" />
          </UFormGroup>

          <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">
            {{ error }}
          </div>

          <div class="flex justify-end gap-2">
            <UButton
              type="button"
              variant="soft"
              @click="showModal = false"
            >
              Annuler
            </UButton>
            <UButton
              type="submit"
              :loading="submitting"
            >
              {{ editingAccount ? 'Modifier' : 'Créer' }}
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { Account, AccountSummary } from '~/types';
import type { StandardError } from '~/types/errors';

definePageMeta({
  middleware: 'auth'
});

const { getAccounts, createAccount, updateAccount, deleteAccount: apiDeleteAccount, getAccountsSummary, toggleAccountActive } = useAccounts();
const { getErrorForField, formatForToast } = useErrorHandler();
const { currency, ensureProfileLoaded } = useUserProfile();
const toast = useToast();

const accounts = ref<Account[]>([]);
const summary = ref<AccountSummary | null>(null);
const loading = ref(false);
const loadError = ref(false);
const showModal = ref(false);
const submitting = ref(false);
const error = ref('');
const formErrors = ref<StandardError | null>(null);
const editingAccount = ref<Account | null>(null);

const form = ref({
  name: '',
  account_type: 'checking',
  balance: '0.00',
  currency: 'CHF',
  description: '',
});

const accountTypes = [
  { value: 'checking', label: 'Compte Courant' },
  { value: 'savings', label: 'Compte Épargne' },
  { value: 'credit_card', label: 'Carte de Crédit' },
  { value: 'cash', label: 'Espèces' },
  { value: 'investment', label: 'Investissement' },
  { value: 'loan', label: 'Prêt' },
  { value: 'other', label: 'Autre' },
];

const currencies = ['CHF', 'EUR', 'USD', 'GBP'];

const fetchAccounts = async () => {
  loading.value = true;
  loadError.value = false;
  const result = await getAccounts();
  if (result.success && result.data) {
    accounts.value = result.data.results;
  } else {
    loadError.value = true;
  }
  loading.value = false;
};

const fetchSummary = async () => {
  const result = await getAccountsSummary();
  if (result.success && result.data) {
    summary.value = result.data;
  }
};

const openAddModal = () => {
  editingAccount.value = null;
  form.value = {
    name: '',
    account_type: 'checking',
    balance: '0.00',
    currency: 'CHF',
    description: '',
  };
  error.value = '';
  formErrors.value = null;
  showModal.value = true;
};

const openEditModal = (account: Account) => {
  editingAccount.value = account;
  form.value = {
    name: account.name,
    account_type: account.account_type,
    balance: account.current_balance.toString(),
    currency: account.currency,
    description: account.description || '',
  };
  error.value = '';
  formErrors.value = null;
  showModal.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  error.value = '';
  formErrors.value = null;

  try {
    let result;
    if (editingAccount.value) {
      // Lors de la modification, envoyer tous les champs y compris balance
      result = await updateAccount(editingAccount.value.id, form.value);
    } else {
      result = await createAccount(form.value);
    }

    if (result.success) {
      toast.add({
        title: 'Succès',
        description: editingAccount.value ? 'Compte modifié avec succès' : 'Compte créé avec succès',
        color: 'green',
      });
      showModal.value = false;
      await fetchAccounts();
      await fetchSummary();
    } else if (result.error) {
      // Capturer les erreurs pour affichage au niveau des champs
      formErrors.value = result.error;

      // Afficher un toast avec les erreurs formatées
      const errorMessage = formatForToast(result.error);
      error.value = errorMessage;
      toast.add({
        title: 'Erreur',
        description: errorMessage,
        color: 'red',
      });
    } else {
      error.value = 'Une erreur est survenue';
      toast.add({
        title: 'Erreur',
        description: error.value,
        color: 'red',
      });
    }
  } catch (err) {
    error.value = 'Une erreur inattendue est survenue';
    toast.add({
      title: 'Erreur',
      description: error.value,
      color: 'red',
    });
  } finally {
    submitting.value = false;
  }
};

const toggleActive = async (account: Account) => {
  const result = await toggleAccountActive(account.id);
  if (result.success) {
    toast.add({
      title: 'Succès',
      description: `Compte ${result.data?.is_active ? 'activé' : 'désactivé'}`,
      color: 'green',
    });
    await fetchAccounts();
    await fetchSummary();
  } else {
    toast.add({
      title: 'Erreur',
      description: result.error || 'Impossible de modifier le statut',
      color: 'red',
    });
  }
};

// Confirm modal state
const showConfirmDelete = ref(false);
const accountToDelete = ref<Account | null>(null);

const confirmDelete = (account: Account) => {
  accountToDelete.value = account;
  showConfirmDelete.value = true;
};

const executeDelete = () => {
  if (accountToDelete.value) {
    deleteAccountHandler(accountToDelete.value.id);
    accountToDelete.value = null;
  }
};

const deleteAccountHandler = async (id: number) => {
  const result = await apiDeleteAccount(id);
  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Compte supprimé avec succès',
      color: 'green',
    });
    await fetchAccounts();
    await fetchSummary();
  } else {
    toast.add({
      title: 'Erreur',
      description: result.error || 'Impossible de supprimer le compte',
      color: 'red',
    });
  }
};

onMounted(async () => {
  await ensureProfileLoaded();
  fetchAccounts();
  fetchSummary();
});
</script>
