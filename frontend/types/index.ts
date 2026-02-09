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

// Transaction types
export interface Transaction {
  id: number;
  user?: number;
  account: number;
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
  category_details?: {
    id: number;
    name: string;
    type: string;
    type_display: string;
    icon: string;
    color: string;
    is_active: boolean;
  } | null;
  type: 'income' | 'expense' | 'transfer';
  type_display?: string;
  amount: string;
  description: string;
  date: string;
  notes?: string | null;
  destination_account?: number | null;
  destination_account_details?: {
    id: number;
    name: string;
    account_type: string;
    account_type_display: string;
    balance: string;
    currency: string;
    is_active: boolean;
  } | null;
  is_recurring: boolean;
  recurrence_frequency?: string | null;
  recurrence_interval: number;
  recurrence_end_date?: string | null;
  created_at: string;
  updated_at: string;
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
  sign_count: number;
  created_at: string;
  last_used_at: string;
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
