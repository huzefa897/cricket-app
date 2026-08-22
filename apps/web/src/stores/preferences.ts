import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { DEFAULT_THEME_ID, isThemeId } from '../designs/registry'

// User preferences, persisted to localStorage. There are no user accounts yet,
// so everything lives under the 'app' scope and is shared app-wide. Once auth
// exists, pass the signed-in user id to storageKey() and each user keeps their
// own preferences on their device — nothing else here needs to change.
const APP_SCOPE = 'app'

function storageKey(scope: string = APP_SCOPE): string {
  return `howzatt:prefs:${scope}`
}

interface Prefs {
  theme: string
}

function load(scope: string): Prefs {
  try {
    const raw = localStorage.getItem(storageKey(scope))
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<Prefs>
      if (isThemeId(parsed.theme)) return { theme: parsed.theme }
    }
  } catch {
    // Malformed JSON or storage blocked (private mode) — fall back to defaults.
  }
  return { theme: DEFAULT_THEME_ID }
}

export const usePreferencesStore = defineStore('preferences', () => {
  // Reserved for the future: set this to the signed-in user's id.
  const scope = ref(APP_SCOPE)

  const theme = ref(load(scope.value).theme)

  // Persist on every change (and re-load if the scope/user ever changes).
  watch([theme, scope], ([t, s]) => {
    try {
      localStorage.setItem(storageKey(s), JSON.stringify({ theme: t }))
    } catch {
      // Storage unavailable — preference stays in-memory for this session.
    }
  })

  function setTheme(id: string) {
    if (isThemeId(id)) theme.value = id
  }

  return { scope, theme, setTheme }
})
