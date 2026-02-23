/**
 * Currency formatting utilities
 */

// Mapping of currency codes to their appropriate locales
const CURRENCY_LOCALE_MAP: Record<string, string> = {
  CHF: 'fr-CH',
  EUR: 'fr-FR',
  USD: 'en-US',
  GBP: 'en-GB',
}

/**
 * Format a number as currency
 * @param amount - The amount to format
 * @param currency - The currency code (CHF, EUR, USD, GBP). If not provided, uses the user's profile currency
 * @returns Formatted currency string
 */
export function formatCurrency(amount: number, currency?: string): string {
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

  // Format using Intl.NumberFormat
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
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
