import type { Component } from 'vue'
import ClassicDashboard from './ClassicDashboard.vue'
import FrostedConsole from './FrostedConsole.vue'

// An app theme = a global skin (applied via data-theme on <html>, styled in
// style.css) PLUS the scoring dashboard it ships with. To add a theme:
//   1. add its CSS under a `:root[data-theme='<id>']` block in style.css
//   2. build its dashboard component (same contract as the others)
//   3. add an entry here — it appears in Settings automatically.
export interface Theme {
  id: string
  name: string
  description: string
  dashboard: Component
}

export const THEMES: Theme[] = [
  {
    id: 'frosted',
    name: 'Frosted',
    description: 'Dark violet gradient with frosted-glass panels and bold, high-contrast controls.',
    dashboard: FrostedConsole,
  },
  {
    id: 'classic',
    name: 'Classic Light',
    description: 'Clean white cards on a soft canvas. Calm, bright, and easy to print.',
    dashboard: ClassicDashboard,
  },
]

export const DEFAULT_THEME_ID = 'frosted'

export function isThemeId(id: unknown): id is string {
  return typeof id === 'string' && THEMES.some((t) => t.id === id)
}

export function themeById(id: string): Theme {
  return THEMES.find((t) => t.id === id) ?? THEMES[0]
}
