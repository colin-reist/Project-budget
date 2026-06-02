<template>
  <UModal
    v-model="isOpen"
    :ui="{
      width: 'w-full sm:max-w-md',
      container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
      base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
      padding: 'p-0',
      background: '',
      ring: '',
      shadow: '',
    }"
  >
    <div class="modal-panel">

      <!-- Drag handle mobile -->
      <div class="modal-handle" aria-hidden />

      <!-- Header -->
      <div class="modal-header">
        <div class="modal-icon" :class="`modal-icon--${confirmColor}`">
          <UIcon :name="icon" style="width:18px;height:18px;" />
        </div>
        <h3 class="modal-title">{{ title }}</h3>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <p class="modal-message">{{ message }}</p>

        <div v-if="requireInput" class="field-group" style="margin-top:12px;">
          <label class="field-label">{{ inputLabel }}</label>
          <div class="field-wrap">
            <input
              v-model="inputValue"
              :type="inputType"
              :placeholder="inputPlaceholder"
              class="field-input"
              @keyup.enter="handleConfirm"
            >
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button class="btn btn-ghost" @click="handleCancel">Annuler</button>
        <button
          class="btn"
          :class="confirmColor === 'primary' ? 'btn-primary' : confirmColor === 'orange' ? 'btn-orange' : 'btn-danger'"
          :disabled="requireInput && !inputValue"
          @click="handleConfirm"
        >
          {{ confirmLabel }}
        </button>
      </div>

    </div>
  </UModal>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  title?: string
  message?: string
  confirmLabel?: string
  confirmColor?: string
  icon?: string
  requireInput?: boolean
  inputLabel?: string
  inputType?: string
  inputPlaceholder?: string
  expectedInput?: string
  loading?: boolean
}>(), {
  title: 'Confirmer',
  message: 'Êtes-vous sûr ?',
  confirmLabel: 'Confirmer',
  confirmColor: 'red',
  icon: 'i-heroicons-exclamation-triangle',
  requireInput: false,
  inputLabel: '',
  inputType: 'text',
  inputPlaceholder: '',
  expectedInput: '',
  loading: false,
})

const emit = defineEmits<{
  confirm: [inputValue?: string]
  cancel: []
}>()

const isOpen = defineModel<boolean>({ default: false })
const inputValue = ref('')

const handleConfirm = () => {
  if (props.requireInput && props.expectedInput && inputValue.value !== props.expectedInput) return
  emit('confirm', inputValue.value)
  isOpen.value = false
  inputValue.value = ''
}

const handleCancel = () => {
  emit('cancel')
  isOpen.value = false
  inputValue.value = ''
}
</script>

<style scoped>
.modal-panel {
  background: var(--surface);
  border: 1px solid var(--line);
  display: flex;
  flex-direction: column;
}

.modal-handle {
  width: 36px; height: 4px; border-radius: 999px;
  background: var(--line-strong);
  margin: 10px auto 0;
}
@media (min-width: 640px) { .modal-handle { display: none; } }

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}
.modal-icon {
  width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0;
  display: grid; place-items: center;
}
.modal-icon--red    { background: var(--danger-soft);  color: var(--danger); }
.modal-icon--primary { background: var(--accent-soft); color: var(--accent); }
.modal-icon--green  { background: var(--success-soft); color: var(--success); }
.modal-icon--orange { background: color-mix(in oklab, #f59e0b 12%, var(--surface)); color: #d97706; }

.modal-title {
  flex: 1; margin: 0;
  font-size: 15px; font-weight: 600; color: var(--ink); letter-spacing: -0.2px;
}

.modal-body { padding: 16px 20px; }
.modal-message { font-size: 14px; color: var(--ink-3); line-height: 1.55; margin: 0; }

/* Field */
.field-group { display: flex; flex-direction: column; gap: 5px; }
.field-label  { font-size: 13px; font-weight: 500; color: var(--ink-2); }
.field-wrap {
  display: flex; align-items: center;
  height: 42px; padding: 0 12px;
  background: var(--surface); border: 1px solid var(--line-strong);
  border-radius: var(--radius); box-shadow: var(--shadow-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.field-wrap:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--ring); }
.field-input {
  flex: 1; font-size: 14px; background: transparent; border: none; outline: none;
  color: var(--ink); font-family: inherit;
}
.field-input::placeholder { color: var(--ink-4); }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 20px 16px;
  border-top: 1px solid var(--line);
}

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  height: 36px; padding: 0 16px; border-radius: var(--radius);
  font-size: 13.5px; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: background 0.15s; border: 1px solid transparent;
}
.btn:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-ghost  { background: transparent; color: var(--ink-3); border-color: var(--line-strong); }
.btn-ghost:hover  { background: var(--surface-2); color: var(--ink-2); }
.btn-danger  { background: var(--danger); color: white; }
.btn-danger:hover:not(:disabled)  { background: #b91c1c; }
.btn-primary { background: var(--accent); color: white; }
.btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
.btn-orange  { background: #d97706; color: white; }
.btn-orange:hover:not(:disabled)  { background: #b45309; }
</style>
