<template>
  <div class="settings-page">

    <!-- ── Mobile pill tabs ──────────────────────────────────── -->
    <div class="settings-tabs-mobile">
      <div class="settings-tabs-scroll">
        <button
          v-for="s in SECTIONS"
          :key="s.id"
          class="settings-tab-pill"
          :class="{ active: activeSection === s.id }"
          @click="activeSection = s.id"
        >
          <UIcon :name="s.icon" class="w-3.5 h-3.5" />
          <span>{{ s.label }}</span>
        </button>
      </div>
    </div>

    <!-- ── Main two-column layout ─────────────────────────────── -->
    <div class="settings-layout">

      <!-- Left sidebar nav (desktop) -->
      <aside class="settings-sidebar">
        <div class="settings-sidebar-label">Paramètres</div>
        <button
          v-for="s in SECTIONS"
          :key="s.id"
          class="settings-nav-item"
          :class="{ active: activeSection === s.id }"
          @click="activeSection = s.id"
        >
          <UIcon :name="s.icon" class="settings-nav-icon" />
          <span>{{ s.label }}</span>
        </button>
      </aside>

      <!-- Right content area -->
      <div class="settings-content">

        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-16">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin h-7 w-7" style="color:var(--ink-4)" />
        </div>

        <template v-else>
          <!-- Section heading -->
          <div class="settings-section-heading">
            <div class="settings-section-title">{{ currentSection.label }}</div>
            <div class="settings-section-desc">{{ currentSection.desc }}</div>
          </div>

          <!-- ─── PROFIL ──────────────────────────────────────── -->
          <div v-if="activeSection === 'profile'" class="settings-section-body">

            <!-- Hero card: avatar + identity summary -->
            <div class="settings-card">
              <div class="hero-card-inner">
                <div class="avatar-wrap">
                  <div class="avatar-circle">{{ avatarInitials }}</div>
                  <button class="avatar-edit-btn" title="Changer la photo">
                    <UIcon name="i-heroicons-camera" style="width:13px;height:13px;" />
                  </button>
                </div>
                <div class="hero-info">
                  <div class="hero-name">{{ profileForm.first_name }} {{ profileForm.last_name }}</div>
                  <div class="hero-sub">
                    <UIcon name="i-heroicons-envelope" style="width:12px;height:12px;color:var(--ink-4)" />
                    <span>{{ profileForm.email }}</span>
                    <span style="color:var(--line-strong)">·</span>
                    <span>Membre depuis {{ formatJoinDate }}</span>
                  </div>
                </div>
                <div class="hero-actions">
                  <button class="ds-btn ds-btn-secondary" style="height:32px;padding:0 12px;font-size:12px;">
                    <UIcon name="i-heroicons-trash" style="width:13px;height:13px;" />
                    Retirer la photo
                  </button>
                  <button class="ds-btn ds-btn-primary" style="height:32px;padding:0 12px;font-size:12px;">
                    <UIcon name="i-heroicons-arrow-up-tray" style="width:13px;height:13px;" />
                    Charger une photo
                  </button>
                </div>
              </div>
            </div>

            <!-- Identity card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Identité</div>
                <div class="card-desc">Ces informations apparaissent sur vos rapports et exports.</div>
              </div>
              <div class="card-fields-grid">
                <div class="form-field">
                  <label class="field-label-sm">Prénom</label>
                  <div class="ds-input-wrap">
                    <input v-model="profileForm.first_name" class="ds-input" placeholder="Prénom" />
                  </div>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Nom</label>
                  <div class="ds-input-wrap">
                    <input v-model="profileForm.last_name" class="ds-input" placeholder="Nom de famille" />
                  </div>
                </div>
                <div class="form-field" style="grid-column:span 2">
                  <label class="field-label-sm">Adresse email</label>
                  <div class="ds-input-wrap" style="background:var(--surface-2)">
                    <UIcon name="i-heroicons-envelope" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
                    <input :value="profileForm.email" readonly class="ds-input" style="cursor:default;color:var(--ink-2)" />
                    <span class="ds-badge ds-badge-success" style="flex-shrink:0;">
                      <UIcon name="i-heroicons-check" style="width:10px;height:10px;" />
                      Vérifié
                    </span>
                  </div>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Téléphone</label>
                  <div class="ds-input-wrap">
                    <UIcon name="i-heroicons-phone" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
                    <input v-model="profileForm.phone" class="ds-input" placeholder="+41 78 000 00 00" type="tel" />
                  </div>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Date de naissance</label>
                  <div class="ds-input-wrap">
                    <input v-model="profileForm.birth_date" class="ds-input" type="date" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Localisation card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Localisation &amp; langue</div>
                <div class="card-desc">Adapte les formats de date, de nombre et la devise par défaut.</div>
              </div>
              <div class="card-fields-grid">
                <div class="form-field">
                  <label class="field-label-sm">Langue de l'interface</label>
                  <div class="ds-input-wrap" style="padding:0 12px 0 0;">
                    <select v-model="profileForm.language" class="ds-select">
                      <option value="fr-CH">Français (Suisse)</option>
                      <option value="fr-FR">Français (France)</option>
                      <option value="en-GB">English (UK)</option>
                      <option value="de-CH">Deutsch (Schweiz)</option>
                      <option value="it-CH">Italiano (Svizzera)</option>
                    </select>
                  </div>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Devise principale</label>
                  <div class="ds-input-wrap" style="padding:0 12px 0 0;">
                    <select v-model="profileForm.currency" class="ds-select">
                      <option value="CHF">CHF — Franc suisse</option>
                      <option value="EUR">EUR — Euro</option>
                      <option value="USD">USD — Dollar US</option>
                      <option value="GBP">GBP — Livre sterling</option>
                    </select>
                  </div>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Fuseau horaire</label>
                  <div class="ds-input-wrap" style="padding:0 12px 0 0;">
                    <select v-model="profileForm.timezone_pref" class="ds-select">
                      <option value="Europe/Zurich">Europe / Zurich (GMT+1)</option>
                      <option value="Europe/Paris">Europe / Paris (GMT+1)</option>
                      <option value="Europe/London">Europe / Londres (GMT)</option>
                      <option value="America/New_York">Amérique / New York (GMT−5)</option>
                    </select>
                  </div>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Pays de résidence</label>
                  <div class="ds-input-wrap" style="padding:0 12px 0 0;">
                    <select v-model="profileForm.country" class="ds-select">
                      <option value="CH">Suisse</option>
                      <option value="FR">France</option>
                      <option value="BE">Belgique</option>
                      <option value="DE">Allemagne</option>
                    </select>
                  </div>
                </div>
                <div class="form-field" style="grid-column:span 2">
                  <label class="field-label-sm">Ville</label>
                  <div class="ds-input-wrap">
                    <UIcon name="i-heroicons-map-pin" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
                    <input v-model="profileForm.city" class="ds-input" placeholder="Genève" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Profile save bar -->
            <Transition name="savebar">
              <div v-if="isProfileDirty" class="save-bar-sticky">
                <div class="save-bar-left">
                  <span class="save-bar-dot" />
                  <span>Vous avez des modifications non enregistrées.</span>
                </div>
                <div class="save-bar-actions">
                  <button class="ds-btn ds-btn-ghost" style="height:32px;font-size:12px;" @click="resetProfileForm">Annuler</button>
                  <button class="ds-btn ds-btn-primary" style="height:32px;font-size:12px;" :disabled="submitting" @click="handleProfileUpdate">
                    <span v-if="submitting" class="btn-spinner" />
                    <template v-else>
                      <UIcon name="i-heroicons-check" style="width:13px;height:13px;" />
                      Enregistrer
                    </template>
                  </button>
                </div>
              </div>
            </Transition>
          </div>

          <!-- ─── SÉCURITÉ ────────────────────────────────────── -->
          <div v-else-if="activeSection === 'security'" class="settings-section-body">

            <!-- Password card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Mot de passe</div>
                <div class="card-desc">Choisissez un mot de passe fort, unique à cette application.</div>
              </div>
              <div class="card-fields-grid">
                <div class="form-field">
                  <label class="field-label-sm">Mot de passe actuel <span style="color:var(--accent)">*</span></label>
                  <div class="ds-input-wrap" :class="{ error: passwordErrors.current_password }">
                    <UIcon name="i-heroicons-lock-closed" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
                    <input v-model="passwordForm.current_password" class="ds-input" type="password" placeholder="••••••••" />
                  </div>
                  <p v-if="passwordErrors.current_password" class="ds-field-error">{{ passwordErrors.current_password }}</p>
                </div>
                <div />
                <div class="form-field">
                  <label class="field-label-sm">Nouveau mot de passe <span style="color:var(--accent)">*</span></label>
                  <div class="ds-input-wrap" :class="{ error: passwordErrors.new_password }">
                    <UIcon name="i-heroicons-lock-closed" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
                    <input v-model="passwordForm.new_password" class="ds-input" type="password" placeholder="Min. 8 caractères" />
                  </div>
                  <p v-if="passwordErrors.new_password" class="ds-field-error">{{ passwordErrors.new_password }}</p>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Confirmer le nouveau mot de passe <span style="color:var(--accent)">*</span></label>
                  <div class="ds-input-wrap" :class="{ error: passwordErrors.confirm_password }">
                    <UIcon name="i-heroicons-lock-closed" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
                    <input v-model="passwordForm.confirm_password" class="ds-input" type="password" placeholder="••••••••" />
                  </div>
                  <p v-if="passwordErrors.confirm_password" class="ds-field-error">{{ passwordErrors.confirm_password }}</p>
                </div>
                <div style="grid-column:span 2;display:flex;justify-content:flex-end;gap:8px;padding-top:4px;">
                  <button class="ds-btn ds-btn-ghost" @click="cancelPasswordChange">Annuler</button>
                  <button class="ds-btn ds-btn-primary" :disabled="submitting" @click="handlePasswordChange">
                    <span v-if="submitting" class="btn-spinner" />
                    <template v-else>
                      <UIcon name="i-heroicons-check" style="width:13px;height:13px;" />
                      Mettre à jour
                    </template>
                  </button>
                </div>
              </div>
            </div>

            <!-- Passkeys card -->
            <div class="settings-card">
              <div class="card-header">
                <div>
                  <div class="card-title">Passkeys</div>
                  <div class="card-desc">Authentification sans mot de passe, sécurisée par votre appareil.</div>
                </div>
                <button class="ds-btn ds-btn-primary" style="height:32px;padding:0 12px;font-size:12px;flex-shrink:0;" :disabled="addingPasskey" @click="handleAddPasskey">
                  <span v-if="addingPasskey" class="btn-spinner" style="border-top-color:#fff;" />
                  <template v-else>
                    <UIcon name="i-heroicons-plus" style="width:13px;height:13px;" />
                    Ajouter une Passkey
                  </template>
                </button>
              </div>
              <div v-if="loadingCredentials" class="flex justify-center py-8">
                <UIcon name="i-heroicons-arrow-path" class="animate-spin h-5 w-5" style="color:var(--ink-4)" />
              </div>
              <div v-else-if="credentials.length === 0" class="empty-state">
                <UIcon name="i-heroicons-finger-print" style="width:40px;height:40px;color:var(--ink-4);margin-bottom:10px;" />
                <p>Aucune passkey enregistrée. Ajoutez-en une pour vous connecter rapidement et en toute sécurité.</p>
              </div>
              <template v-else>
                <div
                  v-for="(credential, i) in credentials"
                  :key="credential.id"
                  class="card-row"
                  :style="i === credentials.length - 1 ? 'border-bottom:none' : ''"
                >
                  <div class="row-icon-wrap">
                    <UIcon name="i-heroicons-finger-print" style="width:17px;height:17px;color:var(--accent)" />
                  </div>
                  <div class="row-text">
                    <div class="row-label">{{ credential.device_name || 'Passkey sans nom' }}</div>
                    <div class="row-desc">
                      Créée le {{ formatDate(credential.created_at) }}
                      <template v-if="credential.last_used"> · Dernière utilisation: {{ formatDate(credential.last_used) }}</template>
                    </div>
                  </div>
                  <button
                    class="ds-btn-icon"
                    style="color:var(--danger);border-color:color-mix(in oklab,var(--danger) 25%,var(--line))"
                    :disabled="deletingCredentialId === credential.id"
                    @click="confirmDeleteCredential(credential.id)"
                  >
                    <UIcon name="i-heroicons-trash" style="width:14px;height:14px;" />
                  </button>
                </div>
              </template>
            </div>

            <!-- API Tokens card -->
            <div class="settings-card">
              <div class="card-header">
                <div>
                  <div class="card-title">Tokens API</div>
                  <div class="card-desc">Pour l'intégration avec iOS Shortcuts.</div>
                </div>
                <button class="ds-btn ds-btn-primary" style="height:32px;padding:0 12px;font-size:12px;flex-shrink:0;" @click="showTokenModal = true">
                  <UIcon name="i-heroicons-plus" style="width:13px;height:13px;" />
                  Générer un token
                </button>
              </div>
              <div v-if="loadingTokens" class="flex justify-center py-8">
                <UIcon name="i-heroicons-arrow-path" class="animate-spin h-5 w-5" style="color:var(--ink-4)" />
              </div>
              <div v-else-if="apiTokens.length === 0" class="empty-state">
                <UIcon name="i-heroicons-device-phone-mobile" style="width:40px;height:40px;color:var(--ink-4);margin-bottom:10px;" />
                <p>Aucun token API. Créez-en un pour envoyer des transactions depuis iOS Shortcuts.</p>
              </div>
              <template v-else>
                <div
                  v-for="(token, i) in apiTokens"
                  :key="token.id"
                  class="card-row"
                  :style="i === apiTokens.length - 1 ? 'border-bottom:none' : ''"
                >
                  <div class="row-icon-wrap">
                    <UIcon name="i-heroicons-key" style="width:17px;height:17px;color:var(--accent)" />
                  </div>
                  <div class="row-text">
                    <div class="row-label">{{ token.name }}</div>
                    <div class="row-desc">
                      Créé le {{ formatDate(token.created_at) }}
                      <template v-if="token.last_used"> · Dernier usage: {{ formatDate(token.last_used) }}</template>
                    </div>
                  </div>
                  <button
                    class="ds-btn-icon"
                    style="color:var(--danger);border-color:color-mix(in oklab,var(--danger) 25%,var(--line))"
                    :disabled="deletingTokenId === token.id"
                    @click="confirmDeleteToken(token.id)"
                  >
                    <UIcon name="i-heroicons-trash" style="width:14px;height:14px;" />
                  </button>
                </div>
              </template>
            </div>
          </div>

          <!-- ─── PRÉFÉRENCES BUDGET ──────────────────────────── -->
          <div v-else-if="activeSection === 'budget'" class="settings-section-body">

            <!-- Cycle budgétaire -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Cycle budgétaire</div>
                <div class="card-desc">Définit quand un nouveau mois budgétaire démarre dans l'app.</div>
              </div>
              <div class="card-fields-grid" style="padding:20px 22px">
                <div class="form-field">
                  <label class="field-label-sm">Début du mois budgétaire</label>
                  <div class="ds-input-wrap" style="padding:0 12px 0 0;">
                    <select v-model.number="budgetForm.budget_start_day" class="ds-select">
                      <option :value="1">Le 1er du mois calendaire</option>
                      <option :value="15">Le 15 du mois</option>
                      <option :value="20">Le 20 du mois</option>
                      <option :value="25">Le 25 du mois</option>
                    </select>
                  </div>
                  <p class="field-hint">Souvent calé sur la date de votre salaire.</p>
                </div>
                <div class="form-field">
                  <label class="field-label-sm">Premier jour de la semaine</label>
                  <div class="ds-input-wrap" style="padding:0 12px 0 0;">
                    <select class="ds-select">
                      <option value="mon">Lundi</option>
                      <option value="sun">Dimanche</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Reporter les soldes d'enveloppes</div>
                  <div class="row-desc">Le solde non dépensé d'une enveloppe se reporte au mois suivant.</div>
                </div>
                <button class="settings-switch" :class="{ on: budgetForm.budget_rollover }" @click="budgetForm.budget_rollover = !budgetForm.budget_rollover">
                  <span class="switch-thumb" />
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Catégoriser automatiquement les nouvelles dépenses</div>
                  <div class="row-desc">Suggère une enveloppe en se basant sur les transactions passées.</div>
                </div>
                <button class="settings-switch on" disabled>
                  <span class="switch-thumb" />
                </button>
              </div>
            </div>

            <!-- Arrondi automatique -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Arrondi automatique</div>
                <div class="card-desc">Chaque dépense est arrondie et la différence versée à votre épargne.</div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Activer l'arrondi</div>
                  <div class="row-desc">{{ budgetForm.budget_roundup ? 'Vers le fonds d\'urgence' : 'Désactivé' }}</div>
                </div>
                <button class="settings-switch" :class="{ on: budgetForm.budget_roundup }" @click="budgetForm.budget_roundup = !budgetForm.budget_roundup">
                  <span class="switch-thumb" />
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Arrondir au</div>
                  <div class="row-desc">Plus le palier est élevé, plus vous épargnez vite.</div>
                </div>
                <div class="roundup-segmented" :class="{ disabled: !budgetForm.budget_roundup }">
                  <button
                    v-for="v in ['0.5', '1', '2', '5']"
                    :key="v"
                    class="roundup-opt"
                    :class="{ active: budgetForm.budget_roundup_amount === v && budgetForm.budget_roundup }"
                    :disabled="!budgetForm.budget_roundup"
                    @click="budgetForm.budget_roundup_amount = v"
                  >
                    CHF {{ v }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Affichage des montants -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Affichage des montants</div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Afficher les centimes</div>
                  <div class="row-desc">Désactivez pour ne voir que les francs entiers (CHF 12 au lieu de CHF 12.50).</div>
                </div>
                <button class="settings-switch" :class="{ on: budgetForm.show_cents }" @click="budgetForm.show_cents = !budgetForm.show_cents">
                  <span class="switch-thumb" />
                </button>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Masquer les montants par défaut</div>
                  <div class="row-desc">Active automatiquement le mode confidentiel à chaque ouverture.</div>
                </div>
                <button class="settings-switch" disabled>
                  <span class="switch-thumb" />
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Mettre en évidence les dépassements</div>
                  <div class="row-desc">Les enveloppes au-dessus de 100 % sont surlignées en rouge.</div>
                </div>
                <button class="settings-switch on" disabled>
                  <span class="switch-thumb" />
                </button>
              </div>
            </div>

            <!-- Budget save bar -->
            <Transition name="savebar">
              <div v-if="isBudgetDirty" class="save-bar-sticky">
                <div class="save-bar-left">
                  <span class="save-bar-dot" />
                  <span>Vous avez des modifications non enregistrées.</span>
                </div>
                <div class="save-bar-actions">
                  <button class="ds-btn ds-btn-ghost" style="height:32px;font-size:12px;" @click="resetBudgetForm">Annuler</button>
                  <button class="ds-btn ds-btn-primary" style="height:32px;font-size:12px;" :disabled="submitting" @click="handleBudgetUpdate">
                    <span v-if="submitting" class="btn-spinner" />
                    <template v-else>
                      <UIcon name="i-heroicons-check" style="width:13px;height:13px;" />
                      Enregistrer
                    </template>
                  </button>
                </div>
              </div>
            </Transition>
          </div>

          <!-- ─── NOTIFICATIONS ──────────────────────────────── -->
          <div v-else-if="activeSection === 'notifs'" class="settings-section-body">

            <!-- Channels card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Canaux de notification</div>
                <div class="card-desc">Choisissez où vous recevez vos alertes.</div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Email</div>
                  <div class="row-desc">{{ profile?.email }}</div>
                </div>
                <span class="ds-badge ds-badge-success">
                  <UIcon name="i-heroicons-check" style="width:10px;height:10px;" />
                  Actif
                </span>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Notifications push</div>
                  <div class="row-desc">Cet appareil</div>
                </div>
                <span class="ds-badge ds-badge-success">
                  <UIcon name="i-heroicons-check" style="width:10px;height:10px;" />
                  Actif
                </span>
              </div>
            </div>

            <!-- Events matrix card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Événements</div>
                <div class="card-desc">Cochez ce que vous souhaitez recevoir, et par quel canal.</div>
              </div>
              <!-- Header row -->
              <div class="notif-matrix-header">
                <span>Événement</span>
                <span style="text-align:center">Email</span>
                <span style="text-align:center">Push</span>
              </div>
              <!-- Event rows -->
              <div
                v-for="(evt, i) in NOTIF_EVENTS"
                :key="evt.id"
                class="notif-matrix-row"
                :style="i === NOTIF_EVENTS.length - 1 ? 'border-bottom:none' : ''"
              >
                <div>
                  <div class="row-label">{{ evt.label }}</div>
                  <div class="row-desc" style="font-size:11.5px;margin-top:2px">{{ evt.desc }}</div>
                </div>
                <div style="display:flex;justify-content:center">
                  <button
                    class="settings-switch settings-switch-sm"
                    :class="{ on: notifMatrix[evt.id].email }"
                    @click="toggleNotif(evt.id, 'email')"
                  >
                    <span class="switch-thumb" />
                  </button>
                </div>
                <div style="display:flex;justify-content:center">
                  <button
                    class="settings-switch settings-switch-sm"
                    :class="{ on: notifMatrix[evt.id].push }"
                    @click="toggleNotif(evt.id, 'push')"
                  >
                    <span class="switch-thumb" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Quiet hours -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Heures de calme</div>
                <div class="card-desc">Pas de notifications push pendant cette plage horaire.</div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Activer les heures de calme</div>
                </div>
                <button class="settings-switch on" disabled>
                  <span class="switch-thumb" />
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">De — à</div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-family:'Geist Mono',monospace;font-size:13px">
                  <span class="quiet-time-badge">22:00</span>
                  <span style="color:var(--ink-4)">—</span>
                  <span class="quiet-time-badge">07:30</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ─── DONNÉES ─────────────────────────────────────── -->
          <div v-else-if="activeSection === 'data'" class="settings-section-body">

            <!-- Export card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Exporter vos données</div>
                <div class="card-desc">Téléchargez l'ensemble de votre historique financier.</div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Toutes les transactions</div>
                  <div class="row-desc">Format CSV</div>
                </div>
                <button class="ds-btn ds-btn-secondary" style="height:32px;padding:0 12px;font-size:12px;">
                  <UIcon name="i-heroicons-arrow-down-tray" style="width:13px;height:13px;" />
                  Télécharger CSV
                </button>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Rapport mensuel détaillé</div>
                  <div class="row-desc">Format PDF</div>
                </div>
                <button class="ds-btn ds-btn-secondary" style="height:32px;padding:0 12px;font-size:12px;">
                  <UIcon name="i-heroicons-arrow-down-tray" style="width:13px;height:13px;" />
                  Télécharger PDF
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Sauvegarde complète</div>
                  <div class="row-desc">Toutes vos données (profil, transactions, enveloppes) · Format JSON</div>
                </div>
                <button class="ds-btn ds-btn-secondary" style="height:32px;padding:0 12px;font-size:12px;">
                  <UIcon name="i-heroicons-archive-box" style="width:13px;height:13px;" />
                  Générer l'archive
                </button>
              </div>
            </div>

            <!-- Import card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Importer des données</div>
                <div class="card-desc">Ajoutez des transactions depuis votre banque ou un autre outil.</div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Relevé bancaire</div>
                  <div class="row-desc">Formats supportés : CAMT.053, MT940, OFX, QIF, CSV personnalisé</div>
                </div>
                <button class="ds-btn ds-btn-primary" style="height:32px;padding:0 12px;font-size:12px;">
                  <UIcon name="i-heroicons-arrow-up-tray" style="width:13px;height:13px;" />
                  Importer un fichier
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Synchronisation bancaire</div>
                  <div class="row-desc">Reliez directement PostFinance, Raiffeisen, Swissquote… via Open Banking</div>
                </div>
                <span class="ds-badge" style="background:color-mix(in oklab,#f59e0b 12%,transparent);color:#b45309;border:1px solid color-mix(in oklab,#f59e0b 28%,transparent);">
                  Bientôt
                </span>
              </div>
            </div>

            <!-- Danger zone card -->
            <div class="settings-card" style="border-color:color-mix(in oklab,var(--danger) 25%,var(--line))">
              <div class="card-header" style="border-bottom-color:color-mix(in oklab,var(--danger) 15%,var(--line))">
                <div>
                  <div class="card-title" style="color:var(--danger)">Zone dangereuse</div>
                  <div class="card-desc">Ces actions sont irréversibles. Procédez avec précaution.</div>
                </div>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Remettre le profil à zéro</div>
                  <div class="row-desc">Remet le revenu mensuel à 0. Les transactions et comptes ne sont pas affectés.</div>
                </div>
                <button
                  class="ds-btn"
                  style="height:32px;padding:0 12px;font-size:12px;font-weight:500;background:transparent;color:var(--danger);border:1px solid color-mix(in oklab,var(--danger) 30%,var(--line));border-radius:7px;"
                  @click="showConfirmResetProfile = true"
                >
                  Remettre à zéro
                </button>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Réinitialiser toutes les enveloppes</div>
                  <div class="row-desc">Supprime les budgets et l'historique de répartition. Vos transactions sont conservées.</div>
                </div>
                <button
                  class="ds-btn"
                  style="height:32px;padding:0 12px;font-size:12px;font-weight:500;background:transparent;color:var(--danger);border:1px solid color-mix(in oklab,var(--danger) 30%,var(--line));border-radius:7px;"
                  @click="showConfirmResetBudgets = true"
                >
                  Réinitialiser
                </button>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-text">
                  <div class="row-label">Supprimer définitivement le compte</div>
                  <div class="row-desc">Supprime votre compte et toutes vos données. Cette action est irréversible.</div>
                </div>
                <button
                  class="ds-btn ds-btn-danger"
                  style="height:32px;padding:0 12px;font-size:12px;"
                  @click="confirmDeleteAccount"
                >
                  <UIcon name="i-heroicons-trash" style="width:13px;height:13px;" />
                  Supprimer mon compte
                </button>
              </div>
            </div>
          </div>

          <!-- ─── À PROPOS ────────────────────────────────────── -->
          <div v-else-if="activeSection === 'about'" class="settings-section-body">

            <!-- App info card -->
            <div class="settings-card">
              <div class="card-header">
                <div class="card-title">Application</div>
              </div>
              <div class="card-row">
                <div class="row-label">Version</div>
                <span class="mono" style="font-size:13px;color:var(--ink-2)">1.0.0 · build 1</span>
              </div>
              <div class="card-row">
                <div class="row-label">Compte créé le</div>
                <span style="font-size:13px;color:var(--ink-2)">{{ formatJoinDate }}</span>
              </div>
              <div class="card-row">
                <div class="row-label">Dernière connexion</div>
                <span style="font-size:13px;color:var(--ink-2)">{{ formatLastLogin }}</span>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Centre d'aide</div>
                  <div class="row-desc">Documentation, tutoriels, FAQ</div>
                </div>
                <a href="#" style="font-size:13px;color:var(--accent);font-weight:500;display:inline-flex;align-items:center;gap:4px">
                  Ouvrir
                  <UIcon name="i-heroicons-arrow-top-right-on-square" style="width:12px;height:12px;" />
                </a>
              </div>
              <div class="card-row">
                <div class="row-text">
                  <div class="row-label">Contacter le support</div>
                  <div class="row-desc">Temps de réponse moyen · 6 h</div>
                </div>
                <a href="mailto:support@budget.local" style="font-size:13px;color:var(--accent);font-weight:500">
                  support@budget.local
                </a>
              </div>
              <div class="card-row" style="border-bottom:none">
                <div class="row-label">Mentions légales</div>
                <div style="display:flex;gap:12px;font-size:12.5px">
                  <a href="#" style="color:var(--accent)">CGU</a>
                  <span style="color:var(--ink-4)">·</span>
                  <a href="#" style="color:var(--accent)">Confidentialité</a>
                  <span style="color:var(--ink-4)">·</span>
                  <a href="#" style="color:var(--accent)">Cookies</a>
                </div>
              </div>
            </div>

            <!-- Logout button -->
            <button
              class="ds-btn ds-btn-secondary"
              style="height:40px;padding:0 16px;font-size:13px;"
              @click="logout"
            >
              <UIcon name="i-heroicons-arrow-right-on-rectangle" style="width:14px;height:14px;" />
              Se déconnecter
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- ── Modals ──────────────────────────────────────────────── -->

    <!-- Token Creation Modal -->
    <UModal
      v-model="showTokenModal"
      :ui="{
        width: 'w-full sm:max-w-md',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon">
            <UIcon :name="newTokenValue ? 'i-heroicons-check' : 'i-heroicons-key'" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">{{ newTokenValue ? 'Token créé' : 'Nouveau token API' }}</h3>
          <button class="modal-close" type="button" @click="closeTokenModal">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <!-- Creation Form -->
        <div v-if="!newTokenValue" class="modal-body">
          <div class="field-group">
            <label class="field-label">Nom du token <span class="field-required">*</span></label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-device-phone-mobile" class="field-icon" />
              <input
                v-model="newTokenName"
                type="text"
                placeholder="Ex: iPhone de Reist"
                class="field-input"
                @keyup.enter="handleCreateToken"
              />
            </div>
          </div>
          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="closeTokenModal">Annuler</button>
            <button class="ds-btn ds-btn-primary" :disabled="!newTokenName || creatingToken" @click="handleCreateToken">
              <span v-if="creatingToken" class="btn-spinner" />
              <span v-else>Générer</span>
            </button>
          </div>
        </div>
        <!-- Token Display -->
        <div v-else class="modal-body">
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;background:color-mix(in oklab,#f59e0b 12%,var(--surface));border:1px solid color-mix(in oklab,#f59e0b 30%,transparent);border-radius:var(--radius);">
            <UIcon name="i-heroicons-exclamation-triangle" style="width:16px;height:16px;color:#d97706;flex-shrink:0;margin-top:1px;" />
            <div>
              <p style="font-size:13px;font-weight:600;color:#92400e;margin:0 0 2px;">Copiez ce token maintenant</p>
              <p style="font-size:12.5px;color:#92400e;margin:0;opacity:0.8;">Ce token ne sera plus affiché. Conservez-le dans un endroit sûr.</p>
            </div>
          </div>
          <div class="field-group">
            <label class="field-label">Token</label>
            <div class="field-wrap" style="padding-right:8px;">
              <input :value="newTokenValue" readonly class="field-input mono" style="font-size:12px;" />
              <button type="button" class="ds-btn-icon" style="width:30px;height:30px;flex-shrink:0;" @click="copyToken">
                <UIcon name="i-heroicons-clipboard-document" style="width:14px;height:14px;" />
              </button>
            </div>
          </div>
          <div style="padding:12px;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius);">
            <p style="font-size:12px;font-weight:600;color:var(--ink-2);margin:0 0 8px;">Utilisation dans iOS Shortcuts :</p>
            <code style="font-size:11px;color:var(--ink-3);display:block;word-break:break-all;line-height:1.6;font-family:'Geist Mono',ui-monospace,monospace;">
              POST {{ apiBase }}/api/v1/ios/transaction/<br>
              Authorization: Bearer {{ newTokenValue }}<br>
              Body: { "amount": 12.50, "label": "Courses", "category": "Alimentation" }
            </code>
          </div>
          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button class="ds-btn ds-btn-primary" @click="closeTokenModal">Fermer</button>
          </div>
        </div>
      </div>
    </UModal>

    <!-- Confirm modals -->
    <ConfirmModal
      v-model="showConfirmResetProfile"
      title="Remettre le profil à zéro"
      message="Le revenu mensuel sera remis à 0. Cette action ne supprime pas vos transactions ni vos comptes."
      confirm-label="Remettre à zéro"
      confirm-color="orange"
      icon="i-heroicons-arrow-path"
      @confirm="executeResetProfile"
    />
    <ConfirmModal
      v-model="showConfirmResetBudgets"
      title="Supprimer toutes les enveloppes"
      message="Toutes vos enveloppes budgétaires seront supprimées. Les transactions et catégories ne sont pas affectées. Cette action est irréversible."
      confirm-label="Supprimer les enveloppes"
      confirm-color="orange"
      icon="i-heroicons-inbox"
      @confirm="executeResetBudgets"
    />
    <ConfirmModal
      v-model="showConfirmDeleteCredential"
      title="Supprimer la passkey"
      message="Êtes-vous sûr de vouloir supprimer cette passkey ? Vous ne pourrez plus l'utiliser pour vous connecter."
      confirm-label="Supprimer"
      @confirm="executeDeleteCredential"
    />
    <ConfirmModal
      v-model="showConfirmDeleteToken"
      title="Révoquer le token"
      message="Êtes-vous sûr de vouloir révoquer ce token ? Les raccourcis iOS utilisant ce token ne fonctionneront plus."
      confirm-label="Révoquer"
      confirm-color="red"
      icon="i-heroicons-key"
      @confirm="executeDeleteToken"
    />
    <!-- Delete Account — Step 1 -->
    <ConfirmModal
      v-if="deleteAccountStep === 1"
      v-model="showDeleteAccountModal"
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
    <!-- Delete Account — Step 2 -->
    <ConfirmModal
      v-if="deleteAccountStep === 2"
      v-model="showDeleteAccountModal"
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
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

/* ── Composables ───────────────────────────────────────────── */
const { getProfile, updateProfile, changePassword, deleteAccount, resetProfile, currency, ensureProfileLoaded } = useUserProfile()
const { resetAllBudgets } = useBudgets()
const { logout } = useAuth()
const { registerWebAuthn, listCredentials, deleteCredential } = useWebAuthn()
const { getTokens, createToken, deleteToken } = useApiTokens()
const toast = useToast()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

/* ── Section config ─────────────────────────────────────────── */
const SECTIONS = [
  { id: 'profile',  label: 'Profil',             icon: 'i-heroicons-user',              desc: 'Vos informations personnelles' },
  { id: 'security', label: 'Sécurité',           icon: 'i-heroicons-shield-check',      desc: 'Mot de passe, sessions' },
  { id: 'budget',   label: 'Préférences budget', icon: 'i-heroicons-banknotes',         desc: 'Cycle, arrondis, devise' },
  { id: 'notifs',   label: 'Notifications',      icon: 'i-heroicons-bell',              desc: 'Canaux et alertes' },
  { id: 'data',     label: 'Données',            icon: 'i-heroicons-archive-box',       desc: 'Import, export, suppression' },
  { id: 'about',    label: 'À propos',           icon: 'i-heroicons-information-circle', desc: 'Version, aide, mentions' },
] as const

const NOTIF_EVENTS = [
  { id: 'overspend', label: 'Dépassement d\'enveloppe', desc: 'Quand une enveloppe atteint 90 % ou est dépassée' },
  { id: 'income',    label: 'Salaire reçu',             desc: 'À chaque crédit ≥ CHF 1 000' },
  { id: 'autotr',    label: 'Virement automatique',     desc: 'Confirmation des règles d\'épargne' },
  { id: 'goal',      label: 'Objectif atteint',         desc: 'Quand un objectif d\'épargne est rempli' },
  { id: 'weekly',    label: 'Rapport hebdomadaire',     desc: 'Synthèse chaque lundi matin' },
  { id: 'security',  label: 'Alertes de sécurité',      desc: 'Nouvelle connexion, changement de mot de passe' },
]

/* ── Navigation state ──────────────────────────────────────── */
const activeSection = ref<string>('profile')
const currentSection = computed(() => SECTIONS.find(s => s.id === activeSection.value) || SECTIONS[0])

/* ── Profile state ─────────────────────────────────────────── */
const profile = ref<any>(null)
const loading = ref(true)
const submitting = ref(false)

// Profile form — tracks editable identity + locale fields
const profileForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  birth_date: '' as string | null,
  language: 'fr-CH',
  timezone_pref: 'Europe/Zurich',
  currency: 'CHF',
  city: '',
  country: 'CH',
})
// Snapshot used for dirty detection
const initialProfileForm = ref('')

const isProfileDirty = computed(() =>
  JSON.stringify(profileForm.value) !== initialProfileForm.value
)

/* ── Budget preferences state ──────────────────────────────── */
const budgetForm = ref({
  budget_start_day: 1,
  budget_rollover: true,
  budget_roundup: false,
  budget_roundup_amount: '1',
  show_cents: true,
})
const initialBudgetForm = ref('')
const isBudgetDirty = computed(() =>
  JSON.stringify(budgetForm.value) !== initialBudgetForm.value
)

/* ── Password form ─────────────────────────────────────────── */
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const passwordErrors = ref<Record<string, string>>({})

/* ── Passkeys state ─────────────────────────────────────────── */
const credentials = ref<any[]>([])
const loadingCredentials = ref(false)
const addingPasskey = ref(false)
const deletingCredentialId = ref<number | null>(null)
const showConfirmDeleteCredential = ref(false)
const credentialToDelete = ref<number | null>(null)

/* ── API Tokens state ──────────────────────────────────────── */
const apiTokens = ref<any[]>([])
const loadingTokens = ref(false)
const showTokenModal = ref(false)
const newTokenName = ref('')
const newTokenValue = ref('')
const creatingToken = ref(false)
const deletingTokenId = ref<number | null>(null)
const showConfirmDeleteToken = ref(false)
const tokenToDelete = ref<number | null>(null)

/* ── Notifications local state ─────────────────────────────── */
type NotifId = 'overspend' | 'income' | 'autotr' | 'goal' | 'weekly' | 'security'
const notifMatrix = ref<Record<NotifId, { email: boolean; push: boolean }>>({
  overspend: { email: true,  push: true  },
  income:    { email: false, push: true  },
  autotr:    { email: false, push: false },
  goal:      { email: true,  push: true  },
  weekly:    { email: true,  push: false },
  security:  { email: true,  push: true  },
})

const toggleNotif = (id: string, channel: 'email' | 'push') => {
  const key = id as NotifId
  notifMatrix.value[key][channel] = !notifMatrix.value[key][channel]
}

/* ── Danger zone state ─────────────────────────────────────── */
const showConfirmResetProfile = ref(false)
const showConfirmResetBudgets = ref(false)
const showDeleteAccountModal = ref(false)
const deleteAccountStep = ref<1 | 2>(1)
const deleteAccountPassword = ref('')

/* ── Computed helpers ──────────────────────────────────────── */
const avatarInitials = computed(() => {
  const fn = profileForm.value.first_name?.charAt(0) || ''
  const ln = profileForm.value.last_name?.charAt(0) || ''
  return (fn + ln).toUpperCase() || profileForm.value.email?.charAt(0).toUpperCase() || '?'
})

const formatJoinDate = computed(() => {
  if (!profile.value?.date_joined) return 'N/A'
  return new Date(profile.value.date_joined).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
})

const formatLastLogin = computed(() => {
  if (!profile.value?.last_login) return 'Jamais'
  return new Date(profile.value.last_login).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
})

/* ── Data fetching ─────────────────────────────────────────── */
const fetchProfile = async () => {
  loading.value = true
  const result = await getProfile()
  if (result.success && result.data) {
    profile.value = result.data
    syncFormsFromProfile(result.data)
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de charger le profil', color: 'red' })
  }
  loading.value = false
}

/**
 * Populate both profileForm and budgetForm from API data and snapshot
 * for dirty tracking.
 */
const syncFormsFromProfile = (data: any) => {
  profileForm.value = {
    first_name:    data.first_name    || '',
    last_name:     data.last_name     || '',
    email:         data.email         || '',
    phone:         data.phone         || '',
    birth_date:    data.birth_date    || null,
    language:      data.language      || 'fr-CH',
    timezone_pref: data.timezone_pref || 'Europe/Zurich',
    currency:      data.currency      || 'CHF',
    city:          data.city          || '',
    country:       data.country       || 'CH',
  }
  initialProfileForm.value = JSON.stringify(profileForm.value)

  budgetForm.value = {
    budget_start_day:    data.budget_start_day    ?? 1,
    budget_rollover:     data.budget_rollover     ?? true,
    budget_roundup:      data.budget_roundup      ?? false,
    budget_roundup_amount: String(data.budget_roundup_amount ?? '1'),
    show_cents:          data.show_cents          ?? true,
  }
  initialBudgetForm.value = JSON.stringify(budgetForm.value)
}

const fetchCredentials = async () => {
  loadingCredentials.value = true
  const result = await listCredentials()
  if (result.success) { credentials.value = result.data || [] }
  loadingCredentials.value = false
}

const fetchTokens = async () => {
  loadingTokens.value = true
  const result = await getTokens()
  if (result.success && result.data) { apiTokens.value = result.data }
  loadingTokens.value = false
}

/* ── Profile handlers ──────────────────────────────────────── */
const handleProfileUpdate = async () => {
  submitting.value = true
  const result = await updateProfile({
    first_name:    profileForm.value.first_name,
    last_name:     profileForm.value.last_name,
    phone:         profileForm.value.phone,
    birth_date:    profileForm.value.birth_date || null,
    language:      profileForm.value.language,
    timezone_pref: profileForm.value.timezone_pref,
    currency:      profileForm.value.currency,
    city:          profileForm.value.city,
    country:       profileForm.value.country,
  })
  submitting.value = false
  if (result.success) {
    toast.add({ title: 'Profil mis à jour', color: 'green' })
    await fetchProfile()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de mettre à jour le profil', color: 'red' })
  }
}

const resetProfileForm = () => {
  if (profile.value) syncFormsFromProfile(profile.value)
}

/* ── Budget handlers ───────────────────────────────────────── */
const handleBudgetUpdate = async () => {
  submitting.value = true
  const result = await updateProfile({
    budget_start_day:    budgetForm.value.budget_start_day,
    budget_rollover:     budgetForm.value.budget_rollover,
    budget_roundup:      budgetForm.value.budget_roundup,
    budget_roundup_amount: budgetForm.value.budget_roundup_amount,
    show_cents:          budgetForm.value.show_cents,
  })
  submitting.value = false
  if (result.success) {
    toast.add({ title: 'Préférences enregistrées', color: 'green' })
    await fetchProfile()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de sauvegarder les préférences', color: 'red' })
  }
}

const resetBudgetForm = () => {
  if (profile.value) syncFormsFromProfile(profile.value)
}

/* ── Password handlers ─────────────────────────────────────── */
const handlePasswordChange = async () => {
  passwordErrors.value = {}
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordErrors.value.confirm_password = 'Les mots de passe ne correspondent pas'
    return
  }
  if (passwordForm.value.new_password.length < 8) {
    passwordErrors.value.new_password = 'Le mot de passe doit contenir au moins 8 caractères'
    return
  }
  submitting.value = true
  const result = await changePassword({
    current_password: passwordForm.value.current_password,
    new_password: passwordForm.value.new_password,
  })
  submitting.value = false
  if (result.success) {
    toast.add({ title: 'Mot de passe changé avec succès', color: 'green' })
    cancelPasswordChange()
  } else {
    const msg = result.error?.data?.error || 'Impossible de changer le mot de passe'
    toast.add({ title: 'Erreur', description: msg, color: 'red' })
  }
}

const cancelPasswordChange = () => {
  passwordErrors.value = {}
  passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }
}

/* ── Passkey handlers ──────────────────────────────────────── */
const handleAddPasskey = async () => {
  if (!profile.value) return
  addingPasskey.value = true
  const result = await registerWebAuthn(profile.value.username)
  if (result.success) {
    toast.add({ title: 'Passkey ajoutée avec succès', color: 'green' })
    await fetchCredentials()
  } else {
    toast.add({ title: 'Erreur', description: result.error || 'Impossible d\'ajouter la passkey', color: 'red' })
  }
  addingPasskey.value = false
}

const confirmDeleteCredential = (id: number) => {
  credentialToDelete.value = id
  showConfirmDeleteCredential.value = true
}

const executeDeleteCredential = async () => {
  if (credentialToDelete.value === null) return
  deletingCredentialId.value = credentialToDelete.value
  const result = await deleteCredential(credentialToDelete.value)
  credentialToDelete.value = null
  if (result.success) {
    toast.add({ title: 'Passkey supprimée', color: 'green' })
    await fetchCredentials()
  } else {
    toast.add({ title: 'Erreur', description: result.error || 'Impossible de supprimer la passkey', color: 'red' })
  }
  deletingCredentialId.value = null
}

/* ── Token handlers ─────────────────────────────────────────── */
const handleCreateToken = async () => {
  creatingToken.value = true
  const result = await createToken(newTokenName.value)
  creatingToken.value = false
  if (result.success && result.data) {
    newTokenValue.value = result.data.token || ''
    await fetchTokens()
    toast.add({ title: 'Token créé', description: 'Copiez-le maintenant, il ne sera plus affiché.', color: 'green' })
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de créer le token', color: 'red' })
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
    toast.add({ title: 'Copié', description: 'Token copié dans le presse-papier', color: 'green' })
  } catch {
    toast.add({ title: 'Erreur', description: 'Impossible de copier le token', color: 'red' })
  }
}

const confirmDeleteToken = (id: number) => {
  tokenToDelete.value = id
  showConfirmDeleteToken.value = true
}

const executeDeleteToken = async () => {
  if (tokenToDelete.value === null) return
  deletingTokenId.value = tokenToDelete.value
  const result = await deleteToken(tokenToDelete.value)
  tokenToDelete.value = null
  if (result.success) {
    toast.add({ title: 'Token révoqué', color: 'green' })
    await fetchTokens()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de révoquer le token', color: 'red' })
  }
  deletingTokenId.value = null
}

/* ── Danger zone handlers ──────────────────────────────────── */
const executeResetProfile = async () => {
  const result = await resetProfile()
  if (result.success) {
    toast.add({ title: 'Profil remis à zéro', description: 'Le revenu mensuel a été remis à 0.', color: 'green' })
    await fetchProfile()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de remettre le profil à zéro', color: 'red' })
  }
}

const executeResetBudgets = async () => {
  const result = await resetAllBudgets()
  if (result.success) {
    toast.add({ title: 'Enveloppes supprimées', description: 'Toutes vos enveloppes ont été supprimées.', color: 'green' })
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de supprimer les enveloppes', color: 'red' })
  }
}

const confirmDeleteAccount = () => {
  deleteAccountStep.value = 1
  deleteAccountPassword.value = ''
  showDeleteAccountModal.value = true
}

const handleDeleteAccountStep1 = (inputValue?: string) => {
  if (inputValue) {
    deleteAccountPassword.value = inputValue
    deleteAccountStep.value = 2
    nextTick(() => { showDeleteAccountModal.value = true })
  }
}

const handleDeleteAccountStep2 = async (inputValue?: string) => {
  if (inputValue !== 'DELETE') {
    toast.add({ title: 'Annulé', description: 'Vous devez taper exactement "DELETE"', color: 'gray' })
    return
  }
  const result = await deleteAccount({ password: deleteAccountPassword.value, confirm: inputValue })
  if (result.success) {
    toast.add({ title: 'Compte supprimé', color: 'green' })
    setTimeout(() => logout(), 2000)
  } else {
    const msg = result.error?.data?.error || 'Impossible de supprimer le compte'
    toast.add({ title: 'Erreur', description: msg, color: 'red' })
  }
}

/* ── Utility ────────────────────────────────────────────────── */
const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric'
  })

/* ── Lifecycle ──────────────────────────────────────────────── */
onMounted(async () => {
  await ensureProfileLoaded()
  await fetchProfile()
  fetchCredentials()
  fetchTokens()
})
</script>

<style scoped>
/* ── Page shell ─────────────────────────────────────────────── */
.settings-page {
  min-height: 100vh;
  background: var(--bg);
}

/* ── Mobile pill tabs ───────────────────────────────────────── */
.settings-tabs-mobile {
  display: none;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 20;
}
.settings-tabs-scroll {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  padding: 10px 0;
  scrollbar-width: none;
}
.settings-tabs-scroll::-webkit-scrollbar { display: none; }
.settings-tab-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink-3);
  font-size: 12.5px;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.12s;
  flex-shrink: 0;
}
.settings-tab-pill.active {
  background: var(--accent-soft);
  color: var(--accent);
  border-color: color-mix(in oklab, var(--accent) 22%, transparent);
}

/* ── Layout ─────────────────────────────────────────────────── */
.settings-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 32px 80px;
  align-items: flex-start;
}

/* ── Sidebar ─────────────────────────────────────────────────── */
.settings-sidebar {
  position: sticky;
  top: 24px;
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.settings-sidebar-label {
  font-size: 10.5px;
  color: var(--ink-4);
  text-transform: uppercase;
  letter-spacing: 0.7px;
  font-weight: 500;
  padding: 6px 12px 8px;
}
.settings-nav-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 8px 12px;
  height: 36px;
  border-radius: 8px;
  border: none;
  color: var(--ink-2);
  background: transparent;
  font-size: 13.5px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.12s;
  text-align: left;
  width: 100%;
}
.settings-nav-item:hover { background: var(--surface-2); }
.settings-nav-item.active {
  color: var(--accent);
  background: var(--accent-soft);
  font-weight: 500;
}
.settings-nav-icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  color: var(--ink-3);
}
.settings-nav-item.active .settings-nav-icon {
  color: var(--accent);
}

/* ── Content area ────────────────────────────────────────────── */
.settings-content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.settings-section-heading {
  padding: 6px 0 20px;
}
.settings-section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.3px;
}
.settings-section-desc {
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 3px;
}
.settings-section-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* ── Card ────────────────────────────────────────────────────── */
.settings-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card-header {
  padding: 18px 22px 14px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.card-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.2px;
}
.card-desc {
  font-size: 12.5px;
  color: var(--ink-3);
  margin-top: 3px;
  line-height: 1.5;
}
.card-fields-grid {
  padding: 20px 22px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.field-label-sm {
  font-size: 11.5px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}
.field-hint {
  font-size: 11.5px;
  color: var(--ink-4);
  margin-top: 4px;
}
.ds-select {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 13px;
  color: var(--ink);
  cursor: pointer;
  padding: 0 12px;
  height: 38px;
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
}

/* ── Card row ────────────────────────────────────────────────── */
.card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 22px;
  gap: 24px;
  border-bottom: 1px solid var(--line);
}
.row-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: var(--accent-soft);
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.row-text { flex: 1; min-width: 0; }
.row-label {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink);
}
.row-desc {
  font-size: 12px;
  color: var(--ink-3);
  margin-top: 3px;
  line-height: 1.4;
}

/* ── Switch toggle ───────────────────────────────────────────── */
.settings-switch {
  width: 36px;
  height: 20px;
  border-radius: 999px;
  border: none;
  background: var(--line-strong);
  position: relative;
  cursor: pointer;
  transition: background 0.18s;
  flex-shrink: 0;
}
.settings-switch.on { background: var(--accent); }
.settings-switch:disabled { opacity: 0.5; cursor: not-allowed; }
.switch-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.18);
  transition: left 0.18s;
}
.settings-switch.on .switch-thumb { left: calc(100% - 18px); }

.settings-switch-sm {
  width: 30px;
  height: 18px;
}
.settings-switch-sm .switch-thumb {
  width: 14px;
  height: 14px;
}
.settings-switch-sm.on .switch-thumb { left: calc(100% - 16px); }

/* ── Roundup segmented control ───────────────────────────────── */
.roundup-segmented {
  display: flex;
  gap: 4px;
  padding: 3px;
  background: var(--surface-2);
  border-radius: 8px;
  border: 1px solid var(--line);
}
.roundup-segmented.disabled { opacity: 0.5; }
.roundup-opt {
  height: 28px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 500;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 5px;
  cursor: pointer;
  color: var(--ink-3);
  font-family: 'Geist Mono', monospace;
  transition: all 0.12s;
}
.roundup-opt.active {
  background: var(--surface);
  border-color: var(--line);
  color: var(--ink);
}
.roundup-opt:disabled { cursor: not-allowed; }

/* ── Notifications matrix ────────────────────────────────────── */
.notif-matrix-header {
  display: grid;
  grid-template-columns: 1fr 90px 90px;
  align-items: center;
  gap: 16px;
  padding: 12px 22px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--line);
  font-size: 10.5px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}
.notif-matrix-row {
  display: grid;
  grid-template-columns: 1fr 90px 90px;
  align-items: center;
  gap: 16px;
  padding: 14px 22px;
  border-bottom: 1px solid var(--line);
}

/* ── Quiet hours badge ───────────────────────────────────────── */
.quiet-time-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  padding: 0 12px;
  background: var(--surface);
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  font-family: 'Geist Mono', monospace;
  font-size: 13px;
  color: var(--ink);
  min-width: 80px;
}

/* ── Hero card ───────────────────────────────────────────────── */
.hero-card-inner {
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.avatar-wrap { position: relative; flex-shrink: 0; }
.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -1px;
  box-shadow: 0 8px 24px -8px color-mix(in oklab, var(--accent) 60%, transparent);
}
.avatar-edit-btn {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--surface);
  border: 1px solid var(--line-strong);
  cursor: pointer;
  display: grid;
  place-items: center;
  color: var(--ink-2);
  box-shadow: var(--shadow-sm);
}
.hero-info { flex: 1; min-width: 0; }
.hero-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.4px;
}
.hero-sub {
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
  flex-shrink: 0;
}

/* ── Empty state ─────────────────────────────────────────────── */
.empty-state {
  padding: 32px 22px;
  text-align: center;
  color: var(--ink-3);
  font-size: 13px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* ── Save bar ────────────────────────────────────────────────── */
.save-bar-sticky {
  position: sticky;
  bottom: 16px;
  margin-top: 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px 14px;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  z-index: 10;
}
.save-bar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--ink-2);
}
.save-bar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  flex-shrink: 0;
}
.save-bar-actions { display: flex; gap: 8px; }

/* ── Save bar transition ─────────────────────────────────────── */
.savebar-enter-active,
.savebar-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.savebar-enter-from,
.savebar-leave-to { opacity: 0; transform: translateY(12px); }

/* ── Mobile responsive ───────────────────────────────────────── */
@media (max-width: 767px) {
  .settings-tabs-mobile { display: block; }
  .settings-layout {
    grid-template-columns: 1fr;
    padding: 16px 16px 80px;
    gap: 0;
  }
  .settings-sidebar { display: none; }
  .settings-section-heading { padding: 16px 0 14px; }
  .card-fields-grid { grid-template-columns: 1fr; }
  .form-field[style*="grid-column:span 2"] { grid-column: span 1; }
  .hero-card-inner { flex-direction: column; align-items: flex-start; }
  .hero-actions { flex-direction: row; align-self: stretch; justify-content: flex-start; }
}
</style>
