<template>
  <UModal
    :model-value="modelValue"
    :ui="{
      width: 'w-full sm:max-w-lg',
      container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
      base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
      padding: 'p-0',
      background: '',
      ring: '',
      shadow: '',
    }"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="modal-panel">

      <!-- Drag handle mobile -->
      <div class="modal-handle sm-hide" aria-hidden />

      <!-- Header -->
      <div class="modal-header">
        <div class="modal-header-icon">
          <UIcon
            :name="editingTransaction ? 'i-heroicons-pencil' : 'i-heroicons-plus'"
            style="width:16px;height:16px;"
          />
        </div>
        <h3 class="modal-title">{{ editingTransaction ? 'Modifier la transaction' : 'Nouvelle transaction' }}</h3>
        <button class="modal-close" aria-label="Fermer" @click="close">
          <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
        </button>
      </div>

      <!-- Form -->
      <form class="modal-body" @submit.prevent="handleSubmit">

        <!-- Type tabs -->
        <div class="type-tabs">
          <button
            v-for="t in typeOptions"
            :key="t.value"
            type="button"
            class="type-tab"
            :class="form.type === t.value ? `type-tab--active type-tab--${t.value}` : ''"
            @click="form.type = t.value; form.category = ''; form.refund_budget = null"
          >
            <UIcon :name="t.icon" style="width:14px;height:14px;" />
            {{ t.label }}
          </button>
        </div>

        <!-- Montant -->
        <div class="field-group">
          <label class="field-label">Montant ({{ currency }}) <span class="field-required">*</span></label>
          <div class="field-wrap" :class="{ 'field-error': formErrors.amount }">
            <UIcon name="i-heroicons-banknotes" class="field-icon" />
            <input
              v-model="form.amount"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              required
              inputmode="decimal"
              class="field-input"
              @blur="validateAmount"
              @input="formErrors.amount = ''"
            >
          </div>
          <p v-if="formErrors.amount" class="field-err">{{ formErrors.amount }}</p>
        </div>

        <!-- Compte -->
        <div class="field-group">
          <label class="field-label">Compte <span class="field-required">*</span></label>
          <USelectMenu
            v-model="form.account"
            :options="accounts"
            option-attribute="name"
            value-attribute="id"
            placeholder="Sélectionner un compte"
            size="lg"
            @update:model-value="formErrors.account = ''"
          />
          <p v-if="formErrors.account" class="field-err">{{ formErrors.account }}</p>
        </div>

        <!-- Compte destination (transfert) -->
        <div v-if="form.type === 'transfer'" class="field-group">
          <label class="field-label">Compte destination <span class="field-required">*</span></label>
          <USelectMenu
            v-model="form.destination_account"
            :options="accounts.filter(a => a.id !== Number(form.account))"
            option-attribute="name"
            value-attribute="id"
            placeholder="Sélectionner le compte de destination"
            size="lg"
          />
          <p v-if="formErrors.destination_account" class="field-err">{{ formErrors.destination_account }}</p>
        </div>

        <!-- Catégorie -->
        <div v-if="form.type !== 'transfer'" class="field-group">
          <label class="field-label">Catégorie <span class="field-required">*</span></label>
          <USelectMenu
            v-model="form.category"
            :options="filteredCategories"
            option-attribute="name"
            value-attribute="id"
            placeholder="Sélectionner une catégorie"
            size="lg"
          />
          <p v-if="formErrors.category" class="field-err">{{ formErrors.category }}</p>
        </div>

        <!-- Rembourse enveloppe (revenus uniquement) -->
        <div v-if="form.type === 'income'" class="field-group">
          <label class="field-label">Rembourse une enveloppe <span class="field-optional">(optionnel)</span></label>
          <USelectMenu
            v-model="form.refund_budget"
            :options="[{ id: null, name: '— Aucune —' }, ...spendingBudgets]"
            option-attribute="name"
            value-attribute="id"
            placeholder="— Aucune —"
            size="lg"
          />
          <p v-if="form.refund_budget" class="field-hint">
            <UIcon name="i-heroicons-arrow-uturn-left" style="width:12px;height:12px;vertical-align:middle;" />
            Ce revenu sera déduit des dépenses de l'enveloppe sélectionnée
          </p>
        </div>

        <!-- Description -->
        <div class="field-group">
          <label class="field-label">Description</label>
          <div class="field-wrap" :class="{ 'field-error': formErrors.description }">
            <UIcon name="i-heroicons-pencil-square" class="field-icon" />
            <input
              v-model="form.description"
              type="text"
              placeholder="Ex: Courses Migros"
              class="field-input"
              @input="formErrors.description = ''"
            >
          </div>
        </div>

        <!-- Date -->
        <div class="field-group">
          <label class="field-label">Date <span class="field-required">*</span></label>
          <div class="field-wrap" :class="{ 'field-error': formErrors.date }">
            <UIcon name="i-heroicons-calendar-days" class="field-icon" />
            <input
              v-model="form.date"
              type="date"
              required
              class="field-input"
            >
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" class="ds-btn ds-btn-ghost" @click="close">Annuler</button>
          <button type="submit" class="ds-btn ds-btn-primary" :disabled="loading">
            <span v-if="loading" class="btn-spinner" />
            <span v-else>{{ editingTransaction ? 'Mettre à jour' : 'Créer' }}</span>
          </button>
        </div>

      </form>
    </div>
  </UModal>
</template>

<script setup lang="ts">
import type { Account, Category } from '~/types';

const props = defineProps<{
  modelValue: boolean;
  accounts: Account[];
  categories: Category[];
  initialAccount?: number | string;
  editingTransaction?: any;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'success': [];
}>();

const { createTransaction, updateTransaction } = useTransactions();
const { getBudgets } = useBudgets();
const { currency } = useUserProfile();
const { formatForToast } = useErrorHandler();
const toast = useToast();

const spendingBudgets = ref<{ id: number; name: string }[]>([]);
onMounted(async () => {
  const result = await getBudgets({ is_active: true });
  if (result.data?.results) {
    spendingBudgets.value = result.data.results
      .filter(b => !b.is_savings_goal)
      .map(b => ({ id: b.id, name: b.name }));
  }
});

const loading = ref(false);
const formErrors = ref<Record<string, string>>({});

const typeOptions = [
  { value: 'expense', label: 'Dépense', icon: 'i-heroicons-arrow-trending-down' },
  { value: 'income',  label: 'Revenu',  icon: 'i-heroicons-arrow-trending-up' },
  { value: 'transfer',label: 'Transfert', icon: 'i-heroicons-arrow-path' },
];

const defaultForm = () => ({
  type: 'expense',
  amount: '',
  account: props.initialAccount ?? '' as string | number,
  destination_account: '' as string | number,
  category: '' as string | number,
  refund_budget: null as number | null,
  description: '',
  date: new Date().toISOString().split('T')[0],
});

const form = ref(defaultForm());

watch(() => props.modelValue, (open) => {
  if (open) {
    if (props.editingTransaction) {
      form.value = {
        type: props.editingTransaction.type,
        amount: props.editingTransaction.amount,
        account: props.editingTransaction.account,
        destination_account: props.editingTransaction.destination_account ?? '',
        category: props.editingTransaction.category ?? '',
        refund_budget: props.editingTransaction.refund_budget ?? null,
        description: props.editingTransaction.description ?? '',
        date: props.editingTransaction.date,
      };
    } else {
      form.value = defaultForm();
    }
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

const close = () => emit('update:modelValue', false);

const handleSubmit = async () => {
  loading.value = true;
  formErrors.value = {};

  const data: any = {
    type: form.value.type,
    amount: form.value.amount,
    account: Number(form.value.account),
    description: form.value.description,
    date: form.value.date,
  };
  if (form.value.type !== 'transfer') {
    // Toujours envoyer category explicitement (null pour vider l'ancienne valeur si type a changé)
    data.category = form.value.category ? Number(form.value.category) : null;
  }
  if (form.value.type === 'transfer' && form.value.destination_account) {
    data.destination_account = Number(form.value.destination_account);
  }
  if (form.value.type === 'income') {
    data.refund_budget = form.value.refund_budget ?? null;
  } else {
    data.refund_budget = null;
  }

  const result = props.editingTransaction
    ? await updateTransaction(props.editingTransaction.id, data)
    : await createTransaction(data);

  loading.value = false;

  if (result.success) {
    toast.add({ title: 'Succès', description: props.editingTransaction ? 'Transaction mise à jour' : 'Transaction créée', color: 'green' });
    close();
    emit('success');
  } else if (result.error?.details) {
    const errors = result.error.details;
    Object.keys(errors).forEach(key => {
      formErrors.value[key] = Array.isArray(errors[key]) ? errors[key][0] : String(errors[key]);
    });
    toast.add({ title: 'Erreur de validation', description: Object.values(formErrors.value)[0] || 'Vérifiez les champs', color: 'red' });
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de sauvegarder la transaction', color: 'red' });
  }
};
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }

.modal-panel {
  background: var(--surface);
  border: 1px solid var(--line);
  display: flex;
  flex-direction: column;
}

.modal-handle {
  width: 36px;
  height: 4px;
  border-radius: 999px;
  background: var(--line-strong);
  margin: 10px auto 0;
}
@media (min-width: 640px) { .modal-handle { display: none; } }

.modal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}
.modal-header-icon {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  background: var(--accent-soft);
  color: var(--accent);
  display: grid; place-items: center;
}
.modal-title {
  flex: 1;
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.2px;
}
.modal-close {
  background: transparent; border: none; cursor: pointer; padding: 4px;
  color: var(--ink-4); display: grid; place-items: center;
  border-radius: var(--radius-sm); transition: color 0.15s, background 0.15s;
}
.modal-close:hover { color: var(--ink-2); background: var(--surface-2); }

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  max-height: 70vh;
}
@media (min-width: 640px) { .modal-body { max-height: none; } }

/* Type tabs */
.type-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 4px;
}
.type-tab {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  height: 34px; border-radius: 6px; border: none;
  font-size: 13px; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.15s;
  background: transparent; color: var(--ink-3);
}
.type-tab:hover:not(.type-tab--active) { color: var(--ink-2); background: var(--surface); }
.type-tab--active { color: white; box-shadow: var(--shadow-sm); }
.type-tab--expense.type-tab--active  { background: var(--danger); }
.type-tab--income.type-tab--active   { background: var(--success); }
.type-tab--transfer.type-tab--active { background: var(--accent); }

/* Fields */
.field-group { display: flex; flex-direction: column; gap: 5px; }
.field-label { font-size: 13px; font-weight: 500; color: var(--ink-2); }
.field-required { color: var(--accent); }

.field-wrap {
  display: flex; align-items: center; gap: 10px;
  height: 44px; padding: 0 12px;
  background: var(--surface); border: 1px solid var(--line-strong);
  border-radius: var(--radius); box-shadow: var(--shadow-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.field-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--ring);
}
.field-wrap.field-error { border-color: var(--danger); }

.field-icon { width: 16px; height: 16px; flex-shrink: 0; color: var(--ink-4); }
.field-input {
  flex: 1; font-size: 14px; background: transparent; border: none; outline: none;
  color: var(--ink); font-family: inherit;
}
.field-input::placeholder { color: var(--ink-4); }
.field-err { margin: 0; font-size: 12px; color: var(--danger); }
.field-optional { color: var(--ink-4); font-weight: 400; }
.field-hint { margin: 0; font-size: 12px; color: var(--success); display: flex; align-items: center; gap: 4px; }

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 4px;
  border-top: 1px solid var(--line);
  margin-top: 4px;
}

/* Buttons */
.ds-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  height: 38px; padding: 0 16px; border-radius: var(--radius);
  font-size: 13.5px; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: background 0.15s, color 0.15s;
  border: 1px solid transparent;
}
.ds-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.ds-btn-primary {
  background: var(--accent); color: white;
  box-shadow: 0 1px 0 rgba(255,255,255,.15) inset, 0 4px 10px -6px rgba(37,99,235,.4);
}
.ds-btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
.ds-btn-ghost {
  background: transparent; color: var(--ink-3);
  border-color: var(--line-strong);
}
.ds-btn-ghost:hover { background: var(--surface-2); color: var(--ink-2); }

.btn-spinner {
  width: 16px; height: 16px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,.3); border-top-color: white;
  animation: spin .7s linear infinite;
}
</style>
