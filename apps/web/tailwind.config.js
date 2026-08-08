/** @type {import('tailwindcss').Config} */
// Functional palette tokens — single source of truth for colors in code.
// See docs/PALETTE.md for the meaning/vibe of each token.
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        canvas: '#F8F9FA', // Off-white app background
        card: '#FFFFFF', // Container / card surfaces
        runs: '#475569', // Dots & singles (0,1,2,3)
        boundary: '#9333EA', // Fours & sixes
        wide: '#D97706', // Wides
        noball: '#0D9488', // No-balls
        bye: '#64748B', // Byes / leg-byes
        wicket: '#A34838', // Wickets & dismissals
        system: '#4A6B5D', // Headers, active tabs, primary actions
      },
    },
  },
  plugins: [],
}
