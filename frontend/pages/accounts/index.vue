<template>
  <div>
    <div class="mb-8 flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Comptes
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Gérez vos comptes bancaires et leur solde
        </p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        size="lg"
        @click="openAddModal"
      >
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
    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-400" />
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
            <p class="text-sm text-gray-500 dark:text-gray-400">Solde actuel</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ formatCurrency(parseFloat(account.current_balance), account.currency) }}
            </p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
              (Excluant les transactions futures)
            </p>
          </div>

          <div v-if="account.projected_balance !== account.current_balance" class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p class="text-sm text-gray-600 dark:text-gray-400">Solde projeté</p>
            <p class="text-lg font-semibold text-blue-600 dark:text-blue-400">
              {{ formatCurrency(parseFloat(account.projected_balance), account.currency) }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              (Incluant les transactions futures)
            </p>
          </div>

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
          <div class="text-center py-12">
            <UIcon name="i-heroicons-banknotes" class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              Aucun compte
            </h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Commencez par créer votre premier compte bancaire
            </p>
            <div class="mt-6">
              <UButton @click="openAddModal">
                <UIcon name="i-heroicons-plus" class="mr-2" />
                Nouveau compte
              </UButton>
            </div>
          </div>
        </UCard>
      </div>
    </div>

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
          </UFormGroup>

          <UFormGroup label="Type de compte" required>
            <USelectMenu
              v-model="form.account_type"
              :options="accountTypes"
              value-attribute="value"
              option-attribute="label"
            />
          </UFormGroup>

          <UFormGroup v-if="!editingAccount" label="Solde initial" required>
            <UInput
              v-model="form.balance"
              type="number"
              step="0.01"
              placeholder="0.00"
            />
            <template #help>
              <span class="text-xs text-gray-500">Le solde initial de votre compte</span>
            </template>
          </UFormGroup>

          <UFormGroup v-else label="Solde actuel">
            <UInput
              :model-value="formatCurrency(parseFloat(form.balance), form.currency)"
              disabled
            />
            <template #help>
              <span class="text-xs text-gray-500">Le solde est calculé automatiquement à partir des transactions. Pour l'ajuster, créez une transaction de type revenu ou dépense.</span>
            </template>
          </UFormGroup>

          <UFormGroup label="Devise" required>
            <USelectMenu
              v-model="form.currency"
              :options="currencies"
            />
          </UFormGroup>

          <UFormGroup label="Description">
            <UTextarea
              v-model="form.description"
              placeholder="Description optionnelle"
              :rows="3"
            />
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

definePageMeta({
  middleware: 'auth'
});

const { getAccounts, createAccount, updateAccount, deleteAccount: apiDeleteAccount, getAccountsSummary, toggleAccountActive } = useAccounts();
const toast = useToast();

const accounts = ref<Account[]>([]);
const summary = ref<AccountSummary | null>(null);
const loading = ref(false);
const showModal = ref(false);
const submitting = ref(false);
const error = ref('');
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
  const result = await getAccounts();
  if (result.success && result.data) {
    accounts.value = result.data.results;
  } else {
    toast.add({
      title: 'Erreur',
      description: result.error || 'Impossible de charger les comptes',
      color: 'red',
    });
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
  showModal.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  error.value = '';

  try {
    let result;
    if (editingAccount.value) {
      // Lors de la modification, ne pas envoyer le champ balance
      const { balance, ...accountData } = form.value;
      result = await updateAccount(editingAccount.value.id, accountData);
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
    } else {
      error.value = result.error || 'Une erreur est survenue';
    }
  } catch (err) {
    error.value = 'Une erreur inattendue est survenue';
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

const confirmDelete = (account: Account) => {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le compte "${account.name}" ?`)) {
    deleteAccountHandler(account.id);
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

const formatCurrency = (amount: number, currency: string = 'CHF') => {
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

onMounted(() => {
  fetchAccounts();
  fetchSummary();
});
</script>
