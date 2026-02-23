/**
 * Currency formatting utilities
 * Optimized for mobile with compact notation support
 */

// Mapping of currency codes to their appropriate locales
const CURRENCY_LOCALE_MAP: Record<string, string> = {
  CHF: 'fr-CH',
  EUR: 'fr-FR',
  USD: 'en-US',
  GBP: 'en-GB',
}

// Mapping of currency codes to their emoji flags for better UX
export const CURRENCY_FLAGS: Record<string, string> = {
  CHF: '🇨🇭',
  EUR: '🇪🇺',
  USD: '🇺🇸',
  GBP: '🇬🇧',
}

interface FormatCurrencyOptions {
  /** Use compact notation for large numbers (1K, 1M) on small screens */
  compact?: boolean
  /** Force compact notation regardless of screen size */
  forceCompact?: boolean
  /** Minimum fraction digits (default: 2) */
  minimumFractionDigits?: number
  /** Maximum fraction digits (default: 2) */
  maximumFractionDigits?: number
}

/**
 * Format a number as currency
 * @param amount - The amount to format
 * @param currency - The currency code (CHF, EUR, USD, GBP). If not provided, uses the user's profile currency
 * @param options - Formatting options
 * @returns Formatted currency string
 */
export function formatCurrency(
  amount: number,
  currency?: string,
  options: FormatCurrencyOptions = {}
): string {
  // If currency is not provided, try to get it from user profile
  let currencyCode = currency

  if (!currencyCode) {
    // Access user profile from composable
    const { currency: userCurrency } = useUserProfile()
    currencyCode = unref(userCurrency)
  }

  // Fallback to CHF if still not available
  currencyCode = currencyCode || 'CHF'

  // Get the appropriate locale for the currency
  const locale = CURRENCY_LOCALE_MAP[currencyCode] || 'fr-CH'

  // Determine if we should use compact notation
  const useCompact = options.forceCompact ||
    (options.compact && Math.abs(amount) >= 10000)

  // Format using Intl.NumberFormat
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
    notation: useCompact ? 'compact' : 'standard',
    minimumFractionDigits: useCompact ? 0 : (options.minimumFractionDigits ?? 2),
    maximumFractionDigits: useCompact ? 1 : (options.maximumFractionDigits ?? 2),
  }).format(amount)
}

/**
 * Get currency symbol for a given currency code
 * @param currency - The currency code
 * @returns Currency symbol
 */
export function getCurrencySymbol(currency: string): string {
  const symbols: Record<string, string> = {
    CHF: 'CHF',
    EUR: '€',
    USD: '$',
    GBP: '£',
  }
  return symbols[currency] || currency
}
