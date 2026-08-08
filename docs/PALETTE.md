# COLOR_PALETTE.md

# 1. Design Context & Environment

- **Canvas Background:** Crisp, clean **White / Off-White (`#F8F9FA`)** to ensure maximum readability and eliminate glare under bright outdoor sunlight.
- **Containers & Cards:** Pure **White (`#FFFFFF`)** with soft, delicate shadows to lift structural blocks off the background.
- **Functional Color-Coding:** Every action type and button category is assigned a distinct, harmonious accent color to build instant muscle memory, speed up scoring, and prevent mis-taps.

---

## 2. The All-Accent Functional Color Palette

- **Standard Runs & Defense (`#475569` - Soft Slate Gray)**
    - *Used For:* Dot balls (`0`) and singles (`1`, `2`, `3`).
    - *Vibe:* Calm, neutral, and understated. These are the most frequent taps, so they form the quiet baseline of the board.
- **Boundaries & Explosive Scoring (`#9333EA` - Rich Royal Purple)**
    - *Used For:* Fours (`4`) and Sixes (`6`).
    - *Vibe:* High-energy and modern. Gives a satisfying, celebratory visual pop every time a boundary is struck.
- **Wides (`#D97706` - Warm Ochre / Mustard Gold)**
    - *Used For:* Wide extra deliveries.
    - *Vibe:* A distinct warning tone that clearly separates wide extras from normal runs.
- **No-Balls (`#0D9488` - Teal / Ocean Blue)**
    - *Used For:* No-ball deliveries.
    - *Vibe:* A cool, unique tone designed to immediately flag free-hit and penalty rules.
- **Byes & Leg-Byes (`#64748B` - Muted Slate Blue)**
    - *Used For:* Auxiliary extra types.
    - *Vibe:* Subtle and secondary, reflecting their lower frequency of use.
- **Wickets & Dismissals (`#A34838` - Earthy Terracotta Rust)**
    - *Used For:* The `Wicket!` button and critical dismissal triggers.
    - *Vibe:* Serious and urgent, but matte and earthy rather than blindingly harsh, ensuring safety against accidental taps.
- **System Navigation & Actions (`#4A6B5D` - Deep Sage Green)**
    - *Used For:* Primary brand headers, active tabs, and main confirmation buttons (e.g., `"Start Match"`).
    - *Vibe:* Grounded, professional, and tied to the classic natural aesthetic of cricket fields.

---

## 3. Tailwind Token Mapping

These functional colors are registered as named tokens in `apps/web/tailwind.config.js`
so components use semantic classes (`bg-runs`, `bg-boundary`) instead of raw hex values.
This is the single source of truth for the palette in code.

```js
// apps/web/tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        canvas:    '#F8F9FA', // Off-white app background
        card:      '#FFFFFF', // Container / card surfaces
        runs:      '#475569', // Dots & singles (0,1,2,3)
        boundary:  '#9333EA', // Fours & sixes
        wide:      '#D97706', // Wides
        noball:    '#0D9488', // No-balls
        bye:       '#64748B', // Byes / leg-byes
        wicket:    '#A34838', // Wickets & dismissals
        system:    '#4A6B5D', // Headers, active tabs, primary actions
      },
    },
  },
}
```

Usage example: `<button class="bg-boundary text-white …">4</button>`.