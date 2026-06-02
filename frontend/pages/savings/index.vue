<template>
  <div class="page-root fade-up">

    <!-- ── Page header ──────────────────────────────────────── -->
    <PageHeader title="Épargne" subtitle="Suivez vos objectifs d'épargne et votre progression.">
      <template #actions>
        <!-- Sort control -->
        <div class="sort-control">
          <button
            v-for="(opt, i) in sortOptions"
            :key="opt.value"
            class="sort-btn"
            :class="{ 'sort-btn--active': sortMode === opt.value }"
            @click="sortMode = opt.value"
          >{{ opt.label }}</button>
        </div>
        <button class="ds-btn ds-btn-primary" style="height:36px;padding:0 14px;font-size:13px;" @click="openAddModal">
          <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
          <span class="hidden sm:inline">Nouvel objectif</span>
        </button>
      </template>
    </PageHeader>

    <!-- ── Loading ───────────────────────────────────────────── -->
    <div v-if="loading" class="goals-grid">
      <div v-for="i in 3" :key="i" class="skeleton-block" style="height:240px;border-radius:14px;" />
    </div>

    <!-- ── Error ─────────────────────────────────────────────── -->
    <div v-else-if="loadError" class="section-card" style="padding:32px;text-align:center;">
      <UIcon name="i-heroicons-exclamation-circle" style="width:40px;height:40px;color:var(--danger);margin-bottom:8px;" />
      <p style="color:var(--ink-2);font-size:14px;">Impossible de charger les objectifs.</p>
      <button class="ds-btn ds-btn-secondary" style="margin-top:12px;" @click="fetchGoals">Réessayer</button>
    </div>

    <template v-else>

      <!-- ── Savings Hero ──────────────────────────────────────── -->
      <div v-if="goals.length > 0" class="hero-root">
        <div class="hero-grid">

          <!-- Left: totals + composition bar -->
          <div class="hero-left">
            <div class="hero-label">
              <UIcon name="i-heroicons-banknotes" style="width:14px;height:14px;color:var(--ink-4);" />
              Total épargné
            </div>
            <div class="hero-total-row">
              <span class="mono hero-total">{{ fmtCHF(totalSaved) }}</span>
              <span class="mono hero-of-total" style="color:var(--ink-3);">/ {{ fmtCHF(totalTarget) }}</span>
            </div>
            <div class="hero-subtitle">
              {{ overallPct.toFixed(0) }}% de l'objectif global atteint · {{ fmtCHF(totalMonthlyRate) }} / mois
            </div>

            <!-- Stacked composition bar -->
            <div class="hero-bar-wrap">
              <div class="hero-bar">
                <div
                  v-for="goal in activeGoals"
                  :key="goal.id"
                  :style="{
                    width: totalSaved > 0 ? `${(parseFloat(goal.current_amount) / totalSaved) * 100}%` : '0%',
                    background: goal.color,
                    transition: 'width 0.4s ease'
                  }"
                />
              </div>
              <div class="hero-legend">
                <div
                  v-for="goal in activeGoals.slice(0, 4)"
                  :key="goal.id"
                  class="hero-legend-item"
                >
                  <span class="hero-legend-dot" :style="{ background: goal.color }" />
                  <div>
                    <div class="hero-legend-label">{{ goal.label }}</div>
                    <div class="mono hero-legend-value">{{ fmtCHF(parseFloat(goal.current_amount)) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: cumulative 12-month chart -->
          <div class="hero-right">
            <div class="hero-chart-header">
              <span class="hero-chart-label">Évolution cumulée · 12 mois</span>
              <span v-if="heroHistory.length >= 2" class="mono hero-chart-range">
                {{ fmtShort(heroMin) }} – {{ fmtShort(heroMax) }}
              </span>
            </div>
            <svg
              v-if="heroHistory.length >= 2"
              :viewBox="`0 0 ${HW} ${HH}`"
              style="width:100%;height:auto;display:block;"
              preserveAspectRatio="none"
            >
              <defs>
                <linearGradient id="herograd" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stop-color="var(--accent)" stop-opacity="0.22" />
                  <stop offset="1" stop-color="var(--accent)" stop-opacity="0" />
                </linearGradient>
              </defs>
              <path :d="heroAreaPath" fill="url(#herograd)" />
              <path :d="heroLinePath" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />
              <circle
                :cx="heroXs(heroHistory.length - 1)"
                :cy="heroYs(heroHistory[heroHistory.length - 1])"
                r="4"
                fill="var(--accent)"
                stroke="var(--surface)"
                stroke-width="2"
              />
            </svg>
            <div v-else class="hero-chart-empty">Pas encore de données</div>
          </div>
        </div>
      </div>

      <!-- ── Goals grid ────────────────────────────────────────── -->
      <div class="goals-grid">
        <button
          v-for="goal in sortedGoals"
          :key="goal.id"
          class="goal-card"
          :class="{ 'goal-card--selected': selectedGoalId === goal.id }"
          :style="selectedGoalId === goal.id
            ? { border: `1px solid ${goal.color}`, boxShadow: `0 0 0 3px color-mix(in oklab, ${goal.color} 18%, transparent), var(--shadow-md)` }
            : {}"
          @click="handleCardClick(goal.id)"
        >
          <!-- Top stripe -->
          <div class="goal-card-stripe" :style="{ background: goal.color, opacity: selectedGoalId === goal.id ? '1' : '0.7' }" />

          <!-- Header: ring + icon + name -->
          <div class="goal-card-header">
            <!-- Progress ring -->
            <div class="goal-ring-wrap">
              <svg :width="64" :height="64" viewBox="0 0 64 64">
                <!-- Track -->
                <circle
                  cx="32" cy="32"
                  :r="ringR(64, 6)"
                  fill="none"
                  stroke="var(--line)"
                  stroke-width="6"
                />
                <!-- Progress arc -->
                <circle
                  cx="32" cy="32"
                  :r="ringR(64, 6)"
                  fill="none"
                  :stroke="goal.color"
                  stroke-width="6"
                  :stroke-dasharray="ringC(64, 6)"
                  :stroke-dashoffset="ringOffset(64, 6, goalPct(goal))"
                  stroke-linecap="round"
                  transform="rotate(-90 32 32)"
                />
                <!-- Icon badge in center -->
                <foreignObject x="16" y="16" width="32" height="32">
                  <div style="display:flex;align-items:center;justify-content:center;width:32px;height:32px;">
                    <UIcon :name="getGoalIcon(goal.icon)" style="width:16px;height:16px;" :style="{ color: goal.color }" />
                  </div>
                </foreignObject>
              </svg>
            </div>

            <div style="flex:1;min-width:0;">
              <div class="goal-name">{{ goal.label }}</div>
              <div v-if="goal.note" class="goal-note">{{ goal.note }}</div>
            </div>
            <span
              class="goal-pct-badge"
              :style="{ background: `color-mix(in oklab, ${goal.color} 12%, var(--surface))`, color: goal.color }"
            >{{ goalPct(goal).toFixed(0) }}%</span>
          </div>

          <!-- Balance -->
          <div>
            <div class="mono goal-balance">{{ fmtCHF(parseFloat(goal.current_amount)) }}</div>
            <div class="goal-balance-label">sur {{ fmtCHF(parseFloat(goal.target_amount)) }}</div>
          </div>

          <!-- Remaining or done -->
          <div class="goal-remaining" :style="{ color: goalPct(goal) >= 100 ? 'var(--success)' : 'var(--ink-3)' }">
            <template v-if="goalPct(goal) >= 100">
              Objectif atteint ✓
            </template>
            <template v-else>
              Il reste {{ fmtCHF(parseFloat(goal.target_amount) - parseFloat(goal.current_amount)) }}
            </template>
          </div>

          <!-- Sparkline area chart -->
          <div style="margin-top:auto;padding-top:8px;">
            <svg width="100%" height="40" viewBox="0 0 240 40" preserveAspectRatio="none" style="display:block;">
              <defs>
                <linearGradient :id="`sparkgrad-${goal.id}`" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" :stop-color="goal.color" stop-opacity="0.25" />
                  <stop offset="1" :stop-color="goal.color" stop-opacity="0" />
                </linearGradient>
              </defs>
              <!-- Target dashed line -->
              <line
                x1="0" :y1="sparkTargetY(goal)" x2="240" :y2="sparkTargetY(goal)"
                :stroke="goal.color" stroke-width="1" stroke-dasharray="4 3" opacity="0.4"
              />
              <!-- Area + line -->
              <path :d="sparkAreaPath(goal)" :fill="`url(#sparkgrad-${goal.id})`" />
              <path :d="sparkLinePath(goal)" fill="none" :stroke="goal.color" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" />
            </svg>
          </div>

          <!-- Footer: deadline + track status -->
          <div class="goal-footer">
            <span v-if="goal.target_date" class="ds-badge ds-badge-neutral">
              <UIcon name="i-heroicons-calendar" style="width:10px;height:10px;" />
              {{ fmtDeadline(goal.target_date) }}
            </span>
            <span v-else class="ds-badge ds-badge-neutral">Pas de date limite</span>
            <span
              class="ds-badge"
              :class="isOnTrack(goal) ? 'ds-badge-success' : 'ds-badge-danger'"
            >
              <UIcon :name="isOnTrack(goal) ? 'i-heroicons-check' : 'i-heroicons-clock'" style="width:10px;height:10px;" />
              {{ isOnTrack(goal) ? 'Dans les temps' : 'En retard' }}
            </span>
          </div>
        </button>

        <!-- Add goal tile -->
        <button class="goal-add-tile" @click="openAddModal">
          <div class="goal-add-icon">
            <UIcon name="i-heroicons-plus" style="width:22px;height:22px;" />
          </div>
          <div class="goal-add-label">Nouvel objectif</div>
          <div class="goal-add-hint">Maison, voyage, achat…</div>
        </button>

        <!-- Empty state -->
        <div v-if="goals.length === 0" style="grid-column:1/-1;padding:48px;text-align:center;">
          <UIcon name="i-heroicons-banknotes" style="width:48px;height:48px;color:var(--ink-4);margin-bottom:12px;" />
          <p style="font-size:15px;font-weight:500;color:var(--ink-2);margin:0;">Créez votre premier objectif d'épargne</p>
          <p style="font-size:13px;color:var(--ink-3);margin:4px 0 16px;">Définissez un objectif et suivez votre progression.</p>
          <button class="ds-btn ds-btn-primary" @click="openAddModal">Créer un objectif</button>
        </div>
      </div>

      <!-- ── Goal detail panel ──────────────────────────────────── -->
      <div v-if="selectedGoal" class="detail-panel slide-in-right">

        <!-- Gradient header -->
        <div
          class="detail-header"
          :style="{
            background: `linear-gradient(135deg, color-mix(in oklab, ${selectedGoal.color} 10%, var(--surface)) 0%, var(--surface) 60%)`,
          }"
        >
          <div class="detail-header-left">
            <div
              class="detail-goal-icon"
              :style="{
                background: `color-mix(in oklab, ${selectedGoal.color} 14%, var(--surface))`,
                color: selectedGoal.color,
                border: `1px solid color-mix(in oklab, ${selectedGoal.color} 22%, transparent)`,
              }"
            >
              <UIcon :name="getGoalIcon(selectedGoal.icon)" style="width:22px;height:22px;" />
            </div>
            <div>
              <div class="detail-goal-name">{{ selectedGoal.label }}</div>
              <div v-if="selectedGoal.note" class="detail-goal-sub">{{ selectedGoal.note }}</div>
              <div v-else class="detail-goal-sub">Objectif d'épargne</div>
            </div>
          </div>
          <div class="detail-header-actions">
            <button class="detail-action-btn" @click="openApportModal">
              <UIcon name="i-heroicons-plus-circle" style="width:13px;height:13px;" />
              <span class="hidden sm:inline">Apport</span>
            </button>
            <button class="detail-action-btn" @click="openEditModal(selectedGoal)">
              <UIcon name="i-heroicons-pencil" style="width:13px;height:13px;" />
              <span class="hidden sm:inline">Modifier</span>
            </button>
            <button class="detail-action-btn detail-action-btn--danger" @click="confirmDelete(selectedGoal)">
              <UIcon name="i-heroicons-trash" style="width:13px;height:13px;" />
            </button>
          </div>
        </div>

        <!-- Stats row -->
        <div class="detail-stats">
          <!-- Progress ring (large) -->
          <div class="detail-ring-wrap">
            <svg width="104" height="104" viewBox="0 0 104 104">
              <circle cx="52" cy="52" :r="ringR(104, 9)" fill="none" stroke="var(--line)" stroke-width="9" />
              <circle
                cx="52" cy="52"
                :r="ringR(104, 9)"
                fill="none"
                :stroke="selectedGoal.color"
                stroke-width="9"
                :stroke-dasharray="ringC(104, 9)"
                :stroke-dashoffset="ringOffset(104, 9, goalPct(selectedGoal))"
                stroke-linecap="round"
                transform="rotate(-90 52 52)"
              />
              <text x="52" y="48" text-anchor="middle" font-family="Geist Mono, ui-monospace, monospace" font-size="16" font-weight="600" :fill="selectedGoal.color">
                {{ goalPct(selectedGoal).toFixed(0) }}%
              </text>
              <text x="52" y="64" text-anchor="middle" font-family="Geist, ui-sans-serif, sans-serif" font-size="9" fill="var(--ink-3)">atteint</text>
            </svg>
          </div>

          <!-- 4 stat boxes -->
          <div class="detail-stat-grid">
            <div class="detail-stat">
              <div class="detail-stat-label">Mis de côté</div>
              <div class="mono detail-stat-value" :style="{ color: selectedGoal.color }">{{ fmtCHF(parseFloat(selectedGoal.current_amount)) }}</div>
              <div class="detail-stat-sub">sur {{ fmtCHF(parseFloat(selectedGoal.target_amount)) }}</div>
            </div>
            <div class="detail-stat">
              <div class="detail-stat-label">Reste à épargner</div>
              <div class="mono detail-stat-value">{{ fmtCHF(Math.max(0, parseFloat(selectedGoal.target_amount) - parseFloat(selectedGoal.current_amount))) }}</div>
              <div v-if="projectedCompletionDate" class="detail-stat-sub">≈ {{ projectedCompletionDate }}</div>
            </div>
            <div class="detail-stat">
              <div class="detail-stat-label">Rythme actuel</div>
              <div class="mono detail-stat-value">{{ fmtCHF(monthlyRate) }}</div>
              <div class="detail-stat-sub">/ mois</div>
            </div>
            <div class="detail-stat">
              <div class="detail-stat-label">
                {{ selectedGoal.target_date ? 'Pour tenir l\'échéance' : 'Au rythme actuel' }}
              </div>
              <div class="mono detail-stat-value">
                {{ selectedGoal.target_date ? fmtCHF(requiredMonthly) : monthsNeeded + ' mois' }}
              </div>
              <div class="detail-stat-sub" :style="{ color: isOnTrack(selectedGoal) ? 'var(--success)' : 'var(--danger)' }">
                {{ isOnTrack(selectedGoal) ? 'Dans les temps' : 'En retard' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Cumulative chart -->
        <div class="detail-chart-section">
          <div class="detail-section-header">
            <span class="detail-section-title">Progression cumulée</span>
            <span v-if="detailHistory.length >= 2" class="mono detail-chart-range" style="font-size:11px;color:var(--ink-3);">
              {{ fmtShort(Math.min(...detailHistory)) }} – {{ fmtShort(Math.max(...detailHistory)) }}
            </span>
          </div>

          <svg
            v-if="detailHistory.length >= 2"
            :viewBox="`0 0 ${DW} ${DH}`"
            style="width:100%;height:auto;display:block;"
            @mousemove="onDetailChartMove"
            @mouseleave="detailHoverIdx = -1"
          >
            <defs>
              <linearGradient :id="`detailgrad`" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" :stop-color="selectedGoal.color" stop-opacity="0.18" />
                <stop offset="1" :stop-color="selectedGoal.color" stop-opacity="0" />
              </linearGradient>
            </defs>

            <!-- Grid lines -->
            <line
              v-for="(g, i) in [0.25, 0.5, 0.75]"
              :key="i"
              :x1="DP.l" :y1="DP.t + g * (DH - DP.t - DP.b)"
              :x2="DW - DP.r" :y2="DP.t + g * (DH - DP.t - DP.b)"
              stroke="var(--line)" stroke-width="1" stroke-dasharray="2 3"
            />

            <!-- Y-axis labels -->
            <text
              v-for="(g, i) in [0, 0.5, 1]"
              :key="`y${i}`"
              :x="DP.l - 6"
              :y="DP.t + (1 - g) * (DH - DP.t - DP.b) + 4"
              text-anchor="end"
              font-family="Geist Mono, ui-monospace, monospace"
              font-size="9"
              fill="var(--ink-4)"
            >{{ fmtShort(detailMin + g * (detailMax - detailMin)) }}</text>

            <!-- X-axis month labels -->
            <text
              v-for="(label, i) in detailMonthLabels"
              :key="`x${i}`"
              :x="detailXs(i)"
              :y="DH - 4"
              text-anchor="middle"
              font-family="Geist Mono, ui-monospace, monospace"
              font-size="9"
              fill="var(--ink-4)"
            >{{ label }}</text>

            <!-- Target dashed line -->
            <line
              :x1="DP.l" :y1="detailYs(parseFloat(selectedGoal.target_amount))"
              :x2="DW - DP.r" :y2="detailYs(parseFloat(selectedGoal.target_amount))"
              :stroke="selectedGoal.color" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.5"
            />
            <text
              :x="DW - DP.r - 4"
              :y="detailYs(parseFloat(selectedGoal.target_amount)) - 4"
              text-anchor="end"
              font-family="Geist Mono, ui-monospace, monospace"
              font-size="9"
              :fill="selectedGoal.color"
              opacity="0.7"
            >Objectif</text>

            <!-- Actual area + line -->
            <path :d="detailAreaPath" :fill="`url(#detailgrad)`" />
            <path :d="detailLinePath" fill="none" :stroke="selectedGoal.color" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />

            <!-- Projection dashed line from last actual to target -->
            <line
              v-if="projectedEndX !== null"
              :x1="detailXs(detailHistory.length - 1)"
              :y1="detailYs(detailHistory[detailHistory.length - 1])"
              :x2="projectedEndX"
              :y2="detailYs(parseFloat(selectedGoal.target_amount))"
              :stroke="selectedGoal.color" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.5"
            />

            <!-- Hover elements -->
            <template v-if="detailHoverIdx >= 0 && detailHoverIdx < detailHistory.length">
              <line
                :x1="detailXs(detailHoverIdx)" :y1="DP.t"
                :x2="detailXs(detailHoverIdx)" :y2="DH - DP.b"
                stroke="var(--line-strong)" stroke-width="1"
              />
              <circle
                :cx="detailXs(detailHoverIdx)"
                :cy="detailYs(detailHistory[detailHoverIdx])"
                r="4.5"
                :fill="selectedGoal.color"
                stroke="var(--surface)"
                stroke-width="2"
              />
            </template>
          </svg>

          <!-- Hover tooltip below chart -->
          <div v-if="detailHoverIdx >= 0 && detailHoverIdx < detailHistory.length" class="detail-chart-tooltip">
            <span class="detail-chart-tooltip-label">{{ detailMonthLabels[detailHoverIdx] }}</span>
            <span class="mono detail-chart-tooltip-value" :style="{ color: selectedGoal.color }">{{ fmtCHF(detailHistory[detailHoverIdx]) }}</span>
          </div>
        </div>

      </div>

    </template>

    <!-- ── Confirm delete modal ────────────────────────────────── -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer l'objectif"
      :message="`Êtes-vous sûr de vouloir supprimer l'objectif « ${goalToDelete?.label} » ?`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- ── Apport ponctuel modal ──────────────────────────────── -->
    <UModal
      v-model="showApportModal"
      :ui="{
        width: 'w-full sm:max-w-sm',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon" style="background:var(--success-soft);color:var(--success);">
            <UIcon name="i-heroicons-plus-circle" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">Apport ponctuel</h3>
          <button class="modal-close" type="button" @click="showApportModal = false">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleApport">
          <p style="font-size:13.5px;color:var(--ink-2);margin:0;">
            Ajouter un montant à <strong>{{ selectedGoal?.label }}</strong>.
            Montant actuel : <span class="mono">{{ fmtCHF(parseFloat(selectedGoal?.current_amount ?? '0')) }}</span>
          </p>
          <div class="field-group">
            <label class="field-label">Montant à ajouter (CHF) <span class="field-required">*</span></label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-banknotes" class="field-icon" />
              <input v-model="apportAmount" type="number" step="0.01" min="0.01" placeholder="0.00" class="field-input" inputmode="decimal" required />
            </div>
          </div>
          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="showApportModal = false">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="submitting" style="background:var(--success);border-color:var(--success);">
              <span v-if="submitting" class="btn-spinner" />
              <span v-else>Ajouter</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

    <!-- ── Add / Edit goal modal ──────────────────────────────── -->
    <UModal
      v-model="showModal"
      :ui="{
        width: 'w-full sm:max-w-lg',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon">
            <UIcon :name="editingGoal ? 'i-heroicons-pencil' : 'i-heroicons-sparkles'" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">{{ editingGoal ? 'Modifier' : 'Nouvel' }} objectif</h3>
          <button class="modal-close" type="button" @click="showModal = false">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleSubmit">

          <!-- Nom -->
          <div class="field-group">
            <label class="field-label">Nom de l'objectif <span class="field-required">*</span></label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-flag" class="field-icon" />
              <input v-model="form.label" type="text" placeholder="Ex: Fonds d'urgence" class="field-input" required />
            </div>
          </div>

          <!-- Montants (2 colonnes) -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="field-group">
              <label class="field-label">Montant cible <span class="field-required">*</span></label>
              <div class="field-wrap">
                <input v-model="form.target_amount" type="number" step="0.01" min="1" placeholder="5000" class="field-input" inputmode="decimal" required />
              </div>
            </div>
            <div class="field-group">
              <label class="field-label">Déjà épargné</label>
              <div class="field-wrap">
                <input v-model="form.current_amount" type="number" step="0.01" min="0" placeholder="0" class="field-input" inputmode="decimal" />
              </div>
            </div>
          </div>

          <!-- Épargne + date (2 colonnes) -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="field-group">
              <label class="field-label">Épargne / mois</label>
              <div class="field-wrap">
                <input v-model="form.saving_amount" type="number" step="0.01" min="0" placeholder="200" class="field-input" inputmode="decimal" />
              </div>
            </div>
            <div class="field-group">
              <label class="field-label">Date limite</label>
              <div class="field-wrap">
                <input v-model="form.target_date" type="date" class="field-input" />
              </div>
            </div>
          </div>

          <!-- Note -->
          <div class="field-group">
            <label class="field-label">Note (optionnel)</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-pencil-square" class="field-icon" />
              <input v-model="form.note" type="text" placeholder="Description courte…" class="field-input" />
            </div>
          </div>

          <!-- Couleur -->
          <div class="field-group">
            <label class="field-label">Couleur</label>
            <div class="color-picker">
              <button
                v-for="color in GOAL_COLORS"
                :key="color"
                type="button"
                class="color-swatch"
                :class="{ 'color-swatch--active': form.color === color }"
                :style="{ background: color }"
                @click="form.color = color"
              />
            </div>
          </div>

          <!-- Icône -->
          <div class="field-group">
            <label class="field-label">Icône</label>
            <div class="icon-picker">
              <button
                v-for="iconOpt in GOAL_ICONS"
                :key="iconOpt.value"
                type="button"
                class="icon-option"
                :class="{ 'icon-option--active': form.icon === iconOpt.value }"
                :style="form.icon === iconOpt.value ? { borderColor: form.color, color: form.color, background: `color-mix(in oklab, ${form.color} 10%, var(--surface))` } : {}"
                @click="form.icon = iconOpt.value"
              >
                <UIcon :name="getGoalIcon(iconOpt.value)" style="width:18px;height:18px;" />
                <span>{{ iconOpt.label }}</span>
              </button>
            </div>
          </div>

          <!-- Priorité -->
          <div class="field-group">
            <label class="field-label">Priorité</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-bars-3-bottom-right" class="field-icon" />
              <input v-model="form.priority" type="number" min="0" placeholder="0 = défaut" class="field-input" />
            </div>
          </div>

          <p v-if="formError" style="font-size:13px;color:var(--danger);margin:0;">{{ formError }}</p>

          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="showModal = false">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="submitting">
              <span v-if="submitting" class="btn-spinner" />
              <span v-else>{{ editingGoal ? 'Modifier' : 'Créer' }}</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

  </div>
</template>

<script setup lang="ts">
import type { SavingsGoal } from '~/types';

definePageMeta({ middleware: 'auth' });

/* ─── Composables ─────────────────────────────────────────── */
const { getSavingsGoals, createSavingsGoal, updateSavingsGoal, deleteSavingsGoal } = useSavingsGoals();
const toast = useToast();

/* ─── Constants ───────────────────────────────────────────── */
const GOAL_COLORS = ['#2563eb', '#16a34a', '#f97316', '#7c3aed', '#ea580c', '#64748b'];

const GOAL_ICONS = [
  { value: 'banknotes', label: 'Épargne' },
  { value: 'shield',    label: 'Protection' },
  { value: 'flag',      label: 'Objectif' },
  { value: 'house',     label: 'Immobilier' },
  { value: 'sparkles',  label: 'Achat' },
  { value: 'plane',     label: 'Voyage' },
];

const goalIconMap: Record<string, string> = {
  banknotes: 'i-heroicons-banknotes',
  shield:    'i-heroicons-shield-check',
  flag:      'i-heroicons-flag',
  sparkles:  'i-heroicons-sparkles',
  house:     'i-heroicons-home',
  cart:      'i-heroicons-shopping-cart',
  car:       'i-heroicons-truck',
  plane:     'i-heroicons-paper-airplane',
};

/** Map an icon slug to a Heroicons class name. */
const getGoalIcon = (icon: string) => goalIconMap[icon] ?? 'i-heroicons-banknotes';

/* ─── Hero chart dimensions ───────────────────────────────── */
const HW = 760; const HH = 150;
const HP = { l: 36, r: 12, t: 18, b: 22 };

/* ─── Detail chart dimensions ─────────────────────────────── */
const DW = 720; const DH = 220;
const DP = { l: 44, r: 14, t: 24, b: 30 };

/* ─── Sort options ────────────────────────────────────────── */
const sortOptions = [
  { value: 'priority',    label: 'Priorité' },
  { value: 'progression', label: 'Progression' },
  { value: 'deadline',    label: 'Échéance' },
];

/* ─── Month labels ────────────────────────────────────────── */
const MONTH_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];

/* ─── State ────────────────────────────────────────────────── */
const goals         = ref<SavingsGoal[]>([]);
const loading       = ref(false);
const loadError     = ref(false);
const sortMode      = ref<string>('priority');
const selectedGoalId = ref<number | null>(null);

const showModal     = ref(false);
const editingGoal   = ref<SavingsGoal | null>(null);
const submitting    = ref(false);
const formError     = ref('');

const showConfirmDelete = ref(false);
const goalToDelete  = ref<SavingsGoal | null>(null);

const showApportModal = ref(false);
const apportAmount  = ref('');

const detailHoverIdx = ref(-1);

const defaultForm = () => ({
  label: '',
  target_amount: '',
  current_amount: '0',
  saving_amount: '',
  target_date: '',
  note: '',
  color: GOAL_COLORS[0],
  icon: 'banknotes',
  priority: 0,
});
const form = ref(defaultForm());

/* ─── Derived ──────────────────────────────────────────────── */
/** Only active goals for hero aggregation. */
const activeGoals = computed(() => goals.value.filter(g => g.status === 'active'));

const sortedGoals = computed(() => {
  const arr = [...goals.value];
  if (sortMode.value === 'priority') {
    arr.sort((a, b) => b.priority - a.priority || a.label.localeCompare(b.label));
  } else if (sortMode.value === 'progression') {
    arr.sort((a, b) => goalPct(b) - goalPct(a));
  } else {
    // deadline: goals with a date first (soonest first), then no-date goals
    arr.sort((a, b) => {
      if (a.target_date && b.target_date) return a.target_date.localeCompare(b.target_date);
      if (a.target_date) return -1;
      if (b.target_date) return 1;
      return 0;
    });
  }
  return arr;
});

const selectedGoal = computed<SavingsGoal | null>(() =>
  goals.value.find(g => g.id === selectedGoalId.value) ?? null
);

/* ─── Hero aggregates ──────────────────────────────────────── */
const totalSaved = computed(() =>
  activeGoals.value.reduce((s, g) => s + parseFloat(g.current_amount), 0)
);
const totalTarget = computed(() =>
  activeGoals.value.reduce((s, g) => s + parseFloat(g.target_amount), 0)
);
const overallPct = computed(() =>
  totalTarget.value > 0 ? Math.min(100, (totalSaved.value / totalTarget.value) * 100) : 0
);
const totalMonthlyRate = computed(() =>
  activeGoals.value.reduce((s, g) => {
    const sa = parseFloat(g.saving_amount ?? '0');
    if (!sa) return s;
    if (g.saving_frequency === 'monthly') return s + sa;
    if (g.saving_frequency === 'weekly')  return s + sa * 52 / 12;
    if (g.saving_frequency === 'daily')   return s + sa * 365 / 12;
    if (g.saving_frequency === 'yearly')  return s + sa / 12;
    return s;
  }, 0)
);

/* ─── Hero chart ───────────────────────────────────────────── */
/**
 * Build 12 monthly cumulative data points across all active goals.
 * Each point is the sum of each goal's interpolated history at that month.
 */
const heroHistory = computed<number[]>(() => {
  if (activeGoals.value.length === 0) return [];
  const combined: number[] = Array(12).fill(0);
  for (const g of activeGoals.value) {
    const h = buildGoalHistory(g);
    for (let i = 0; i < 12; i++) combined[i] += h[i];
  }
  return combined;
});

const heroMin = computed(() => Math.min(...heroHistory.value));
const heroMax = computed(() => Math.max(...heroHistory.value, 1));

/** Map month index to X coordinate in hero SVG. */
const heroXs = (i: number) =>
  HP.l + (i / (heroHistory.value.length - 1)) * (HW - HP.l - HP.r);

/** Map value to Y coordinate in hero SVG. */
const heroYs = (v: number) =>
  HP.t + (1 - (v - heroMin.value) / Math.max(1, heroMax.value - heroMin.value)) * (HH - HP.t - HP.b);

const heroLinePath = computed(() => {
  if (heroHistory.value.length < 2) return '';
  return heroHistory.value
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${heroXs(i)},${heroYs(v)}`)
    .join(' ');
});

const heroAreaPath = computed(() => {
  if (heroHistory.value.length < 2) return '';
  const last = heroHistory.value.length - 1;
  return `${heroLinePath.value} L${heroXs(last)},${HH - HP.b} L${heroXs(0)},${HH - HP.b} Z`;
});

/* ─── Detail panel computed ────────────────────────────────── */
/** The 12-month history for the selected goal. */
const detailHistory = computed<number[]>(() =>
  selectedGoal.value ? buildGoalHistory(selectedGoal.value) : []
);

const detailMin = computed(() => 0);
const detailMax = computed(() =>
  Math.max(
    parseFloat(selectedGoal.value?.target_amount ?? '0'),
    ...detailHistory.value,
    1
  )
);

const detailMonthLabels = computed<string[]>(() => {
  const now = new Date();
  return Array.from({ length: 12 }, (_, i) => {
    const d = new Date(now);
    d.setMonth(d.getMonth() - (11 - i));
    return MONTH_FR[d.getMonth()];
  });
});

/** Map month index to X in detail SVG. */
const detailXs = (i: number) =>
  DP.l + (i / Math.max(1, detailHistory.value.length - 1)) * (DW - DP.l - DP.r);

/** Map value to Y in detail SVG. */
const detailYs = (v: number) =>
  DP.t + (1 - (v - detailMin.value) / Math.max(1, detailMax.value - detailMin.value)) * (DH - DP.t - DP.b);

const detailLinePath = computed(() => {
  if (detailHistory.value.length < 2) return '';
  return detailHistory.value
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${detailXs(i)},${detailYs(v)}`)
    .join(' ');
});

const detailAreaPath = computed(() => {
  if (detailHistory.value.length < 2) return '';
  const last = detailHistory.value.length - 1;
  return `${detailLinePath.value} L${detailXs(last)},${DH - DP.b} L${detailXs(0)},${DH - DP.b} Z`;
});

/**
 * Projected X position where the linear projection from current point
 * reaches the target line, clamped within the chart width.
 */
const projectedEndX = computed<number | null>(() => {
  if (!selectedGoal.value) return null;
  const target = parseFloat(selectedGoal.value.target_amount);
  const current = parseFloat(selectedGoal.value.current_amount);
  if (current >= target || monthlyRate.value <= 0) return null;
  // Months needed from now to reach target at current rate
  const monthsLeft = (target - current) / monthlyRate.value;
  // Each month = one step in 12-month chart; last index = now
  const lastX = detailXs(detailHistory.value.length - 1);
  const stepW = (DW - DP.l - DP.r) / Math.max(1, detailHistory.value.length - 1);
  const projX = lastX + monthsLeft * stepW;
  return Math.min(projX, DW - DP.r);
});

/* ─── Monthly rate & projection ───────────────────────────── */
/**
 * Effective monthly savings rate for the selected goal,
 * normalised from any frequency to monthly.
 */
const monthlyRate = computed<number>(() => {
  if (!selectedGoal.value) return 0;
  const sa = parseFloat(selectedGoal.value.saving_amount ?? '0');
  if (!sa) return 0;
  const freq = selectedGoal.value.saving_frequency;
  if (freq === 'monthly') return sa;
  if (freq === 'weekly')  return sa * 52 / 12;
  if (freq === 'daily')   return sa * 365 / 12;
  if (freq === 'yearly')  return sa / 12;
  return sa;
});

const monthsNeeded = computed<number>(() => {
  if (!selectedGoal.value || monthlyRate.value <= 0) return 0;
  const remaining = parseFloat(selectedGoal.value.target_amount) - parseFloat(selectedGoal.value.current_amount);
  return Math.ceil(Math.max(0, remaining) / monthlyRate.value);
});

/** Required monthly amount to hit the target_date deadline. */
const requiredMonthly = computed<number>(() => {
  if (!selectedGoal.value?.target_date) return 0;
  const remaining = parseFloat(selectedGoal.value.target_amount) - parseFloat(selectedGoal.value.current_amount);
  if (remaining <= 0) return 0;
  const months = monthsBetween(new Date().toISOString().slice(0, 10), selectedGoal.value.target_date);
  return months > 0 ? remaining / months : remaining;
});

/** Human-readable projected completion date at current monthly rate. */
const projectedCompletionDate = computed<string | null>(() => {
  if (!selectedGoal.value || monthsNeeded.value <= 0) return null;
  const d = new Date();
  d.setMonth(d.getMonth() + monthsNeeded.value);
  return `${MONTH_FR[d.getMonth()]} ${d.getFullYear()}`;
});

/* ─── Helper: progress ring geometry ──────────────────────── */
/** Inner radius of a ring given outer size and stroke width. */
const ringR = (size: number, stroke: number) => (size - stroke) / 2;
/** Circumference for a given ring. */
const ringC = (size: number, stroke: number) => 2 * Math.PI * ringR(size, stroke);
/** Dash-offset for a given completion percentage. */
const ringOffset = (size: number, stroke: number, pct: number) => {
  const c = ringC(size, stroke);
  return c - (Math.min(100, pct) / 100) * c;
};

/* ─── Helper: goal progress percentage ────────────────────── */
const goalPct = (goal: SavingsGoal): number => {
  const target = parseFloat(goal.target_amount);
  if (target <= 0) return 0;
  return Math.min(100, (parseFloat(goal.current_amount) / target) * 100);
};

/* ─── Helper: on-track status ─────────────────────────────── */
/**
 * A goal is "on track" if:
 * - it has no deadline, OR
 * - the projected completion date (at current rate) is before the deadline.
 */
const isOnTrack = (goal: SavingsGoal): boolean => {
  if (!goal.target_date) return true;
  if (goalPct(goal) >= 100) return true;
  const remaining = parseFloat(goal.target_amount) - parseFloat(goal.current_amount);
  if (remaining <= 0) return true;
  const rate = (() => {
    const sa = parseFloat(goal.saving_amount ?? '0');
    if (!sa) return 0;
    const freq = goal.saving_frequency;
    if (freq === 'monthly') return sa;
    if (freq === 'weekly')  return sa * 52 / 12;
    if (freq === 'daily')   return sa * 365 / 12;
    if (freq === 'yearly')  return sa / 12;
    return sa;
  })();
  if (rate <= 0) return false;
  const mNeeded = remaining / rate;
  const mAvailable = monthsBetween(new Date().toISOString().slice(0, 10), goal.target_date);
  return mNeeded <= mAvailable;
};

/* ─── Helper: sparkline for goal card ─────────────────────── */
/** Target line Y position in the 240×40 sparkline. */
const sparkTargetY = (goal: SavingsGoal): number => {
  const hist = buildGoalHistory(goal);
  const maxVal = Math.max(parseFloat(goal.target_amount), ...hist, 1);
  return 40 - (parseFloat(goal.target_amount) / maxVal) * 36;
};

const sparkLinePath = (goal: SavingsGoal): string => {
  const hist = buildGoalHistory(goal);
  const maxVal = Math.max(parseFloat(goal.target_amount), ...hist, 1);
  const xs = (i: number) => (i / (hist.length - 1)) * 240;
  const ys = (v: number) => 40 - (v / maxVal) * 36;
  return hist.map((v, i) => `${i === 0 ? 'M' : 'L'}${xs(i)},${ys(v)}`).join(' ');
};

const sparkAreaPath = (goal: SavingsGoal): string => {
  const hist = buildGoalHistory(goal);
  if (hist.length < 2) return '';
  const line = sparkLinePath(goal);
  const last = hist.length - 1;
  const maxVal = Math.max(parseFloat(goal.target_amount), ...hist, 1);
  const xs = (i: number) => (i / (hist.length - 1)) * 240;
  const ys = (v: number) => 40 - (v / maxVal) * 36;
  return `${line} L${xs(last)},40 L${xs(0)},40 Z`;
};

/* ─── Hover handler for detail chart ──────────────────────── */
const onDetailChartMove = (e: MouseEvent) => {
  const svg = (e.currentTarget as SVGElement);
  const rect = svg.getBoundingClientRect();
  const relX = (e.clientX - rect.left) / rect.width * DW;
  const inner = DW - DP.l - DP.r;
  const step = inner / Math.max(1, detailHistory.value.length - 1);
  const idx = Math.round((relX - DP.l) / step);
  detailHoverIdx.value = Math.max(0, Math.min(detailHistory.value.length - 1, idx));
};

/* ─── Formatters ───────────────────────────────────────────── */
/** Format as CHF with 0 decimals, fr-CH locale. */
const fmtCHF = (n: number): string =>
  new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: 'CHF',
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(n);

/** Compact format: 14820 → "14.8k", 850 → "850". */
const fmtShort = (n: number): string => {
  if (Math.abs(n) >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(Math.round(n));
};

/** Format target_date ISO string as "Mai 2027". */
const fmtDeadline = (iso: string): string => {
  const d = new Date(iso);
  return `${MONTH_FR[d.getMonth()]} ${d.getFullYear()}`;
};

/* ─── Pure helpers ─────────────────────────────────────────── */
/**
 * Build 12 monthly data points for a goal by linear interpolation
 * from 0 at created_at to current_amount at now.
 * Points before created_at are clamped to 0.
 */
const buildGoalHistory = (goal: SavingsGoal): number[] => {
  const createdAt = new Date(goal.created_at);
  const now = new Date();
  const current = parseFloat(goal.current_amount);
  return Array.from({ length: 12 }, (_, i) => {
    const pointDate = new Date(now);
    pointDate.setMonth(pointDate.getMonth() - (11 - i));
    if (pointDate <= createdAt) return 0;
    const totalMs = now.getTime() - createdAt.getTime();
    const pointMs = pointDate.getTime() - createdAt.getTime();
    return Math.min(current, current * (pointMs / totalMs));
  });
};

/**
 * Number of calendar months between two ISO date strings.
 * Positive when b is after a.
 */
const monthsBetween = (a: string, b: string): number => {
  const d1 = new Date(a);
  const d2 = new Date(b);
  return (d2.getFullYear() - d1.getFullYear()) * 12 + (d2.getMonth() - d1.getMonth());
};

/* ─── Data fetching ────────────────────────────────────────── */
const fetchGoals = async () => {
  loading.value = true;
  loadError.value = false;
  const result = await getSavingsGoals();
  if (result.success && result.data) {
    goals.value = result.data.results;
    // Auto-select first goal if none selected
    if (!selectedGoalId.value && goals.value.length > 0) {
      selectedGoalId.value = goals.value[0].id;
    }
  } else {
    loadError.value = true;
  }
  loading.value = false;
};

/* ─── Card click ───────────────────────────────────────────── */
const handleCardClick = (id: number) => {
  if (selectedGoalId.value === id) {
    selectedGoalId.value = null;
  } else {
    selectedGoalId.value = id;
    detailHoverIdx.value = -1;
  }
};

/* ─── CRUD ─────────────────────────────────────────────────── */
const openAddModal = () => {
  editingGoal.value = null;
  form.value = defaultForm();
  formError.value = '';
  showModal.value = true;
};

const openEditModal = (goal: SavingsGoal) => {
  editingGoal.value = goal;
  form.value = {
    label: goal.label,
    target_amount: goal.target_amount,
    current_amount: goal.current_amount,
    saving_amount: goal.saving_amount ?? '',
    target_date: goal.target_date ?? '',
    note: goal.note,
    color: goal.color,
    icon: goal.icon,
    priority: goal.priority,
  };
  formError.value = '';
  showModal.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  formError.value = '';
  const payload: Partial<SavingsGoal> = {
    label: form.value.label,
    target_amount: form.value.target_amount,
    current_amount: form.value.current_amount || '0',
    saving_amount: form.value.saving_amount || null,
    target_date: form.value.target_date || null,
    note: form.value.note,
    color: form.value.color,
    icon: form.value.icon,
    priority: Number(form.value.priority),
    status: 'active',
    saving_frequency: 'monthly',
  };
  try {
    const result = editingGoal.value
      ? await updateSavingsGoal(editingGoal.value.id, payload)
      : await createSavingsGoal(payload);
    if (result.success) {
      toast.add({ title: 'Succès', description: editingGoal.value ? 'Objectif modifié.' : 'Objectif créé.', color: 'green' });
      showModal.value = false;
      await fetchGoals();
    } else {
      formError.value = "Une erreur est survenue.";
      toast.add({ title: 'Erreur', description: 'Impossible de sauvegarder.', color: 'red' });
    }
  } catch {
    formError.value = 'Erreur inattendue.';
  } finally {
    submitting.value = false;
  }
};

const confirmDelete = (goal: SavingsGoal) => {
  goalToDelete.value = goal;
  showConfirmDelete.value = true;
};

const executeDelete = async () => {
  if (!goalToDelete.value) return;
  const id = goalToDelete.value.id;
  if (selectedGoalId.value === id) selectedGoalId.value = null;
  const result = await deleteSavingsGoal(id);
  if (result.success) {
    toast.add({ title: 'Succès', description: 'Objectif supprimé.', color: 'green' });
    await fetchGoals();
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de supprimer.', color: 'red' });
  }
  goalToDelete.value = null;
};

/* ─── Apport ponctuel ──────────────────────────────────────── */
const openApportModal = () => {
  apportAmount.value = '';
  showApportModal.value = true;
};

const handleApport = async () => {
  if (!selectedGoal.value) return;
  const added = parseFloat(apportAmount.value);
  if (!added || added <= 0) return;
  submitting.value = true;
  const newAmount = (parseFloat(selectedGoal.value.current_amount) + added).toFixed(2);
  const result = await updateSavingsGoal(selectedGoal.value.id, { current_amount: newAmount } as Partial<SavingsGoal>);
  if (result.success) {
    toast.add({ title: 'Succès', description: `${fmtCHF(added)} ajouté à ${selectedGoal.value.label}.`, color: 'green' });
    showApportModal.value = false;
    await fetchGoals();
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de mettre à jour.', color: 'red' });
  }
  submitting.value = false;
};

/* ─── Lifecycle ────────────────────────────────────────────── */
onMounted(fetchGoals);
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }

/* ── Root ── */
.page-root {
  padding: 20px 24px 48px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
@media (min-width: 1024px) { .page-root { padding: 20px 32px 48px; } }

/* ── Sort control ── */
.sort-control {
  display: inline-flex;
  align-items: center;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}
.sort-btn {
  padding: 0 12px;
  height: 34px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--ink-3);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}
.sort-btn--active {
  background: var(--surface);
  color: var(--ink);
  box-shadow: var(--shadow-sm);
}
.sort-btn:hover:not(.sort-btn--active) {
  background: var(--surface);
  color: var(--ink-2);
}

/* ── Hero ── */
.hero-root {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  padding: 24px;
}
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}
@media (min-width: 768px) { .hero-grid { grid-template-columns: 1fr 1.6fr; } }

.hero-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--ink-3);
  letter-spacing: 0.3px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.hero-total-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 4px;
}
.hero-total {
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -1px;
  color: var(--ink);
  line-height: 1;
}
.hero-of-total {
  font-size: 18px;
  font-weight: 400;
}
.hero-subtitle {
  font-size: 12.5px;
  color: var(--ink-3);
  margin-bottom: 16px;
}
.hero-bar-wrap { display: flex; flex-direction: column; gap: 10px; }
.hero-bar {
  display: flex;
  height: 8px;
  border-radius: 99px;
  overflow: hidden;
  background: var(--line);
}
.hero-legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.hero-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.hero-legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.hero-legend-label { font-size: 12px; color: var(--ink-2); }
.hero-legend-value { font-size: 11px; color: var(--ink-3); }

.hero-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.hero-chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.hero-chart-label {
  font-size: 11.5px;
  font-weight: 500;
  color: var(--ink-3);
  letter-spacing: 0.2px;
  text-transform: uppercase;
}
.hero-chart-range { font-size: 11px; color: var(--ink-4); }
.hero-chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
  color: var(--ink-4);
  font-size: 13px;
}

/* ── Goals grid ── */
.goals-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}
@media (min-width: 640px)  { .goals-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .goals-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1280px) { .goals-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); } }

/* ── Goal card ── */
.goal-card {
  text-align: left;
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.18s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-family: inherit;
  min-height: 220px;
}
.goal-card:hover:not(.goal-card--selected) {
  border-color: var(--line-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.goal-card-stripe {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  transition: opacity 0.18s ease;
}
.goal-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}
.goal-ring-wrap { flex-shrink: 0; }
.goal-name { font-size: 14px; font-weight: 600; color: var(--ink); letter-spacing: -0.2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.goal-note { font-size: 11.5px; color: var(--ink-3); margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.goal-pct-badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  font-family: 'Geist Mono', ui-monospace, monospace;
}
.goal-balance { font-size: 24px; font-weight: 500; color: var(--ink); letter-spacing: -0.8px; line-height: 1; }
.goal-balance-label { font-size: 11.5px; color: var(--ink-3); margin-top: 2px; }
.goal-remaining { font-size: 12.5px; }
.goal-footer { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: auto; }

/* ── Add tile ── */
.goal-add-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  background: transparent;
  border: 2px dashed var(--line-strong);
  border-radius: 14px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, color 0.15s;
  font-family: inherit;
  color: var(--ink-3);
  min-height: 140px;
}
.goal-add-tile:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
}
.goal-add-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  transition: background 0.15s;
}
.goal-add-tile:hover .goal-add-icon { background: var(--accent-soft); border-color: var(--accent); }
.goal-add-label { font-size: 14px; font-weight: 600; }
.goal-add-hint  { font-size: 12px; color: var(--ink-4); }
.goal-add-tile:hover .goal-add-hint { color: var(--accent); }

/* ── Detail panel ── */
.detail-panel {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  gap: 12px;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--line);
}
.detail-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.detail-goal-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.detail-goal-name { font-size: 17px; font-weight: 600; color: var(--ink); letter-spacing: -0.3px; }
.detail-goal-sub  { font-size: 12.5px; color: var(--ink-3); margin-top: 2px; }

.detail-header-actions { display: flex; align-items: center; gap: 6px; }
.detail-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 12px;
  border-radius: var(--radius);
  font-size: 12.5px;
  font-weight: 500;
  color: var(--ink-2);
  background: var(--surface-2);
  border: 1px solid var(--line);
  cursor: pointer;
  transition: background 0.12s;
  font-family: inherit;
}
.detail-action-btn:hover { background: var(--line); }
.detail-action-btn--danger { color: var(--danger); background: var(--danger-soft); border-color: color-mix(in oklab, var(--danger) 25%, transparent); }
.detail-action-btn--danger:hover { background: color-mix(in oklab, var(--danger) 18%, var(--surface)); }

/* ── Stats row ── */
.detail-stats {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
}
.detail-ring-wrap { flex-shrink: 0; }
.detail-stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  flex: 1;
  min-width: 200px;
}
@media (min-width: 768px) { .detail-stat-grid { grid-template-columns: repeat(4, 1fr); } }
.detail-stat {
  padding: 12px;
  background: var(--surface-2);
  border-radius: var(--radius);
  border: 1px solid var(--line);
}
.detail-stat-label { font-size: 10.5px; color: var(--ink-3); text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }
.detail-stat-value { font-size: 18px; font-weight: 600; color: var(--ink); letter-spacing: -0.5px; }
.detail-stat-sub   { font-size: 11px; color: var(--ink-3); margin-top: 2px; }

/* ── Chart section ── */
.detail-chart-section {
  padding: 20px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.detail-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.detail-section-title { font-size: 12.5px; font-weight: 600; color: var(--ink-2); text-transform: uppercase; letter-spacing: 0.4px; }
.detail-chart-range   { font-size: 11px; color: var(--ink-4); }
.detail-chart-tooltip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: var(--surface-2);
  border-radius: var(--radius);
  border: 1px solid var(--line);
}
.detail-chart-tooltip-label { font-size: 12px; color: var(--ink-3); }
.detail-chart-tooltip-value { font-size: 14px; font-weight: 600; }

/* ── Goal form ── */
.goal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.color-picker {
  display: flex;
  gap: 8px;
  align-items: center;
}
.color-swatch {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.12s, border-color 0.12s;
}
.color-swatch--active {
  border-color: var(--ink);
  transform: scale(1.15);
}
.color-swatch:hover:not(.color-swatch--active) { transform: scale(1.08); }

.icon-picker {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.icon-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 10px;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--surface-2);
  color: var(--ink-2);
  cursor: pointer;
  font-size: 11px;
  font-family: inherit;
  transition: all 0.12s;
  min-width: 56px;
}
.icon-option:hover { border-color: var(--line-strong); background: var(--surface); }
.icon-option--active { font-weight: 600; }

/* ── Skeleton ── */
.skeleton-block {
  background: linear-gradient(90deg, var(--surface-2) 25%, var(--line) 50%, var(--surface-2) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: var(--radius);
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
