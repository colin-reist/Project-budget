<template>
  <UModal
    :model-value="modelValue"
    :ui="{
      width: 'w-full sm:max-w-lg',
      container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
      base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
      padding: 'p-0'
    }"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <UCard>
      <template #header>
        <div class="sm:hidden flex justify-center py-2 -mt-2 mb-2">
          <div class="w-10 h-1 rounded-full bg-gray-300 dark:bg-gray-600"></div>
        </div>
        <h3 class="text-lg font-semibold">Nouvelle transaction</h3>
      </template>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Type -->
        <UFormGroup label="Type" required :error="formErrors.type">
          <USelectMenu
            v-model="form.type"
            :options="[
              { label: 'Revenu', value: 'income', icon: 'i-heroicons-arrow-trending-up' },
              { label: 'Dépense', value: 'expense', icon: 'i-heroicons-arrow-trending-down' },
              { label: 'Transfert', value: 'transfer', icon: 'i-heroicons-arrow-path' }
            ]"
            option-attribute="label"
            value-attribute="value"
            size="lg"
          />
        </UFormGroup>

        <!-- Amount -->
        <UFormGroup :label="`Montant (${currency})`" required :error="formErrors.amount">
          <UInput
            v-model="form.amount"
            type="number"
            step="0.01"
            placeholder="0.00"
            required
            size="lg"
            inputmode="decimal"
            @blur="validateAmount"
            @input="formErrors.amount = ''"
          />
        </UFormGroup>

        <!-- Account -->
        <UFormGroup label="Compte" required :error="formErrors.account">
          <USelectMenu
            v-model="form.account"
            :options="accounts"
            option-attribute="name"
            value-attribute="id"
            placeholder="Sélectionner un compte"
            size="lg"
            @update:model-value="formErrors.account = ''"
          />
        </UFormGroup>

        <!-- Destination Account (only for transfers) -->
        <UFormGroup v-if="form.type === 'transfer'" label="Compte destination" required :error="formErrors.destination_account">
          <USelectMenu
            v-model="form.destination_account"
            :options="accounts.filter(a => a.id !== Number(form.account))"
            option-attribute="name"
            value-attribute="id"
            placeholder="Sélectionner le compte de destination"
            size="lg"
          />
        </UFormGroup>

        <!-- Category (only for income/expense) -->
        <UFormGroup v-if="form.type !== 'transfer'" label="Catégorie" required :error="formErrors.category">
          <USelectMenu
            v-model="form.category"
            :options="filteredCategories"
            option-attribute="name"
            value-attribute="id"
            placeholder="Sélectionner une catégorie"
            size="lg"
          />
        </UFormGroup>

        <!-- Description -->
        <UFormGroup label="Description" :error="formErrors.description">
          <UInput
            v-model="form.description"
            placeholder="Ex: Courses Migros"
            size="lg"
            @input="formErrors.description = ''"
          />
        </UFormGroup>

        <!-- Date -->
        <UFormGroup label="Date" required :error="formErrors.date">
          <UInput
            v-model="form.date"
            type="date"
            required
            size="lg"
          />
        </UFormGroup>

        <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 pt-4">
          <UButton block color="gray" variant="ghost" class="sm:w-auto" @click="close">
            Annuler
          </UButton>
          <UButton block type="submit" class="sm:w-auto" :loading="loading">
            Créer
          </UButton>
        </div>
      </form>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
import type { Account, Category } from '~/types';

const props = defineProps<{
  modelValue: boolean;
  accounts: Account[];
  categories: Category[];
  initialAccount?: number | string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'success': [];
}>();

const { createTransaction } = useTransactions();
const { currency } = useUserProfile();
const { formatForToast } = useErrorHandler();
const toast = useToast();

const loading = ref(false);
const formErrors = ref<Record<string, string>>({});

const defaultForm = () => ({
  type: 'expense',
  amount: '',
  account: props.initialAccount ?? '' as string | number,
  destination_account: '' as string | number,
  category: '' as string | number,
  description: '',
  date: new Date().toISOString().split('T')[0],
});

const form = ref(defaultForm());

watch(() => props.modelValue, (open) => {
  if (open) {
    form.value = defaultForm();
    formErrors.value = {};
  }
});

watch(() => props.initialAccount, (id) => {
  if (id !== undefined) form.value.account = id;
});

const filteredCategories = computed(() =>
  props.categories.filter(cat => {
    if (form.value.type === 'income') return cat.type === 'income';
    if (form.value.type === 'expense') return cat.type === 'expense';
    return false;
  })
);

const validateAmount = () => {
  const amount = parseFloat(form.value.amount);
  if (!form.value.amount) {
    formErrors.value.amount = 'Le montant est requis';
  } else if (isNaN(amount) || amount <= 0) {
    formErrors.value.amount = 'Le montant doit être supérieur à 0';
  } else {
    formErrors.value.amount = '';
  }
};

const close = () => {
  emit('update:modelValue', false);
};

const handleSubmit = async () => {
  loading.value = true;
  formErrors.value = {};

  const transactionData: any = {
    type: form.value.type,
    amount: form.value.amount,
    account: Number(form.value.account),
    description: form.value.description,
    date: form.value.date,
  };

  if (form.value.type !== 'transfer' && form.value.category) {
    transactionData.category = Number(form.value.category);
  }
  if (form.value.type === 'transfer' && form.value.destination_account) {
    transactionData.destination_account = Number(form.value.destination_account);
  }

  const result = await createTransaction(transactionData);
  loading.value = false;

  if (result.success) {
    toast.add({ title: 'Succès', description: 'Transaction créée avec succès', color: 'green' });
    close();
    emit('success');
  } else if (result.error?.details) {
    const errors = result.error.details;
    Object.keys(errors).forEach(key => {
      formErrors.value[key] = Array.isArray(errors[key]) ? errors[key][0] : String(errors[key]);
    });
    const firstError = Object.values(formErrors.value)[0];
    toast.add({ title: 'Erreur de validation', description: firstError || 'Veuillez vérifier les champs', color: 'red' });
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de créer la transaction', color: 'red' });
  }
};
</script>
