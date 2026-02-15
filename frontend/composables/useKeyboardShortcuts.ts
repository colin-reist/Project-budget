/**
 * Composable pour gérer les raccourcis clavier globaux
 *
 * Fournit une API simple pour enregistrer et désenregistrer des raccourcis clavier
 * avec support des modificateurs (Ctrl/Cmd, Shift, Alt)
 *
 * @example
 * const { registerShortcut, unregisterShortcut } = useKeyboardShortcuts()
 *
 * onMounted(() => {
 *   registerShortcut('n', () => openModal(), { ctrl: true })
 * })
 */

type ShortcutModifiers = {
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  meta?: boolean
}

type ShortcutCallback = (event: KeyboardEvent) => void

interface ShortcutConfig {
  key: string
  callback: ShortcutCallback
  modifiers?: ShortcutModifiers
  description?: string
}

export const useKeyboardShortcuts = () => {
  const shortcuts = ref<Map<string, ShortcutConfig>>(new Map())

  /**
   * Génère un ID unique pour un raccourci basé sur la touche et les modificateurs
   */
  const getShortcutId = (key: string, modifiers?: ShortcutModifiers): string => {
    const parts = []
    if (modifiers?.ctrl || modifiers?.meta) parts.push('ctrl')
    if (modifiers?.shift) parts.push('shift')
    if (modifiers?.alt) parts.push('alt')
    parts.push(key.toLowerCase())
    return parts.join('+')
  }

  /**
   * Vérifie si un événement clavier correspond aux modificateurs requis
   */
  const matchesModifiers = (event: KeyboardEvent, modifiers?: ShortcutModifiers): boolean => {
    if (!modifiers) return !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey

    const ctrlOrMeta = modifiers.ctrl || modifiers.meta
    const hasCtrlOrMeta = event.ctrlKey || event.metaKey

    return (
      (!ctrlOrMeta || hasCtrlOrMeta) &&
      (!modifiers.shift || event.shiftKey) &&
      (!modifiers.alt || event.altKey) &&
      // S'assurer que les modificateurs non requis ne sont pas pressés
      (ctrlOrMeta || !hasCtrlOrMeta) &&
      (modifiers.shift || !event.shiftKey) &&
      (modifiers.alt || !event.altKey)
    )
  }

  /**
   * Handler global pour les événements clavier
   */
  const handleKeydown = (event: KeyboardEvent) => {
    // Ignorer si on est dans un input, textarea ou select
    const target = event.target as HTMLElement
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.tagName === 'SELECT' ||
      target.isContentEditable
    ) {
      return
    }

    // Vérifier chaque raccourci enregistré
    for (const [id, config] of shortcuts.value) {
      if (
        event.key.toLowerCase() === config.key.toLowerCase() &&
        matchesModifiers(event, config.modifiers)
      ) {
        event.preventDefault()
        config.callback(event)
        break
      }
    }
  }

  /**
   * Enregistre un nouveau raccourci clavier
   *
   * @param key - Touche à surveiller (ex: 'n', 'k', 'Escape')
   * @param callback - Fonction à exécuter quand le raccourci est déclenché
   * @param options - Modificateurs et description optionnels
   */
  const registerShortcut = (
    key: string,
    callback: ShortcutCallback,
    options?: { modifiers?: ShortcutModifiers; description?: string }
  ) => {
    const id = getShortcutId(key, options?.modifiers)

    shortcuts.value.set(id, {
      key,
      callback,
      modifiers: options?.modifiers,
      description: options?.description
    })

    // Ajouter l'event listener si c'est le premier raccourci
    if (shortcuts.value.size === 1 && process.client) {
      window.addEventListener('keydown', handleKeydown)
    }
  }

  /**
   * Désenregistre un raccourci clavier
   *
   * @param key - Touche du raccourci à supprimer
   * @param modifiers - Modificateurs du raccourci (optionnel)
   */
  const unregisterShortcut = (key: string, modifiers?: ShortcutModifiers) => {
    const id = getShortcutId(key, modifiers)
    shortcuts.value.delete(id)

    // Retirer l'event listener si plus aucun raccourci
    if (shortcuts.value.size === 0 && process.client) {
      window.removeEventListener('keydown', handleKeydown)
    }
  }

  /**
   * Nettoie tous les raccourcis enregistrés
   */
  const cleanup = () => {
    shortcuts.value.clear()
    if (process.client) {
      window.removeEventListener('keydown', handleKeydown)
    }
  }

  /**
   * Retourne une représentation textuelle d'un raccourci pour l'affichage
   * Ex: { ctrl: true, key: 'n' } => 'Ctrl+N' ou '⌘N' sur Mac
   */
  const getShortcutLabel = (key: string, modifiers?: ShortcutModifiers): string => {
    const isMac = process.client && navigator.platform.toUpperCase().indexOf('MAC') >= 0
    const parts = []

    if (modifiers?.ctrl || modifiers?.meta) {
      parts.push(isMac ? '⌘' : 'Ctrl')
    }
    if (modifiers?.shift) {
      parts.push(isMac ? '⇧' : 'Shift')
    }
    if (modifiers?.alt) {
      parts.push(isMac ? '⌥' : 'Alt')
    }

    parts.push(key.toUpperCase())

    return parts.join(isMac ? '' : '+')
  }

  // Cleanup automatique quand le composable est détruit
  onBeforeUnmount(() => {
    cleanup()
  })

  return {
    registerShortcut,
    unregisterShortcut,
    getShortcutLabel,
    cleanup
  }
}
