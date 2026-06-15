// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
}

// Account types
export interface Account {
  id: number;
  user?: number;
  name: string;
  account_type: 'checking' | 'savings' | 'credit_card' | 'cash' | 'investment' | 'loan' | 'other';
  account_type_display?: string;
  balance: string;
  current_balance?: string;
  projected_balance?: string;
  currency: 'CHF' | 'EUR' | 'USD' | 'GBP';
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AccountSummary {
  [currency: string]: {
    total: number;
    count: number;
    by_type: {
      [type: string]: number;
    };
  };
}

// Category types
export interface Category {
  id: number;
  user?: number;
  name: string;
  icon: string;
  color: string;
  type: 'income' | 'expense';
  type_display?: string;
  parent_category?: number;
  is_active: boolean;
  created_at: string;
}

// API Token types
export interface APIToken {
  id: number;
  name: string;
  token?: string; // Seulement présent à la création
  created_at: string;
  last_used: string | null;
  is_active: boolean;
}

// Pending Alert types
export interface PendingAlert {
  id: number;
  type: 'unknown_category';
  payload: {
    transaction_id: number;
    category_name: string;
    amount: string;
    label: string;
  };
  seen: boolean;
  created_at: string;
}

// Transaction types
export interface Transaction {
  id: number;
  user?: number;
  account: number;
  account_name?: string;
  account_details?: {
    id: number;
    name: string;
    account_type: string;
    account_type_display: string;
    balance: string;
    currency: string;
    is_active: boolean;
  };
  category?: number | null;
  category_name?: string | null;
  category_details?: {
    id: number;
    name: string;
    type: string;
    type_display: string;
    icon: string;
    color: string;
    is_active: boolean;
  } | null;
  type: 'income' | 'expense' | 'transfer' | 'adjustment';
  type_display?: string;
  amount: string;
  description: string;
  date: string;
  notes?: string | null;
  destination_account?: number | null;
  destination_account_name?: string | null;
  destination_account_details?: {
    id: number;
    name: string;
    account_type: string;
    account_type_display: string;
    balance: string;
    currency: string;
    is_active: boolean;
  } | null;
  refund_budget?: number | null;
  is_recurring: boolean;
  recurrence_frequency?: string | null;
  recurrence_interval: number;
  recurrence_end_date?: string | null;
  /** UUID partagé entre le template et toutes ses instances générées */
  recurring_series_id?: string | null;
  /** True uniquement pour la transaction maître de la série */
  is_series_template?: boolean;
  source?: 'web' | 'ios' | 'ios_uncategorized';
  source_display?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Représentation d'une série récurrente (retournée par GET /recurring_series/)
 * Contient les métadonnées du template et des statistiques sur ses instances.
 */
export interface RecurringSeries {
  id: number;
  description: string;
  amount: string;
  type: 'income' | 'expense' | 'transfer';
  recurrence_frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
  recurrence_interval: number;
  recurrence_end_date: string | null;
  account: { id: number; name: string; currency: string };
  category: { id: number; name: string; color: string; icon: string } | null;
  /** Prochaine date d'occurrence future (ISO), null si toutes les occurrences sont passées */
  next_occurrence: string | null;
  /** Nombre d'instances générées (hors template) */
  total_instances: number;
  recurring_series_id: string | null;
}

// Recurrence rule types
export interface RecurrenceRule {
  id: number;
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number;
  start_date: string;
  end_date?: string;
  day_of_month?: number;
  day_of_week?: number;
  is_active: boolean;
}

// Budget types
export interface Budget {
  id: number;
  user: number;
  category: number | null;
  category_details?: {
    id: number;
    name: string;
    icon: string;
    color: string;
    type: string;
    is_active: boolean;
  } | null;
  name: string;
  amount: string;
  period: 'weekly' | 'monthly' | 'yearly';
  period_display?: string;
  start_date: string;
  end_date?: string;
  alert_threshold: number;
  is_active: boolean;
  is_savings_goal: boolean;
  is_mandatory_savings?: boolean;
  spent_amount?: number;
  remaining_amount?: number;
  percentage_used?: number;
  is_over_budget?: boolean;
  is_alert_triggered?: boolean;
  projected_amount?: number;
  projected_remaining_amount?: number;
  projected_percentage_used?: number;
  is_projected_over_budget?: boolean;
  created_at: string;
  updated_at: string;
}

// Savings Goal types
export interface SavingsGoal {
  id: number;
  label: string;
  target_amount: string;
  current_amount: string;
  product_url?: string | null;
  product_image_url?: string | null;
  target_date?: string | null;
  saving_amount?: string | null;
  saving_frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
  saving_frequency_display?: string;
  status: 'active' | 'reached' | 'cancelled';
  status_display?: string;
  color: string;
  icon: string;
  note: string;
  priority: number;
  calculated_result?: {
    mode: 'date_calculated' | 'amount_calculated';
    target_date?: string;
    saving_amount?: number;
    periods_needed: number;
  } | null;
  linked_budgets?: Array<{ id: number; name: string; amount: number }>;
  created_at: string;
  updated_at: string;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface WebAuthnCredential {
  id: number;
  user: number;
  credential_id: string;
  public_key: string;
  counter: number;
  created_at: string;
  last_used: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
