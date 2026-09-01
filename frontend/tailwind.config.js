/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Dark charcoal / brown navigation
        charcoal: {
          DEFAULT: '#2b2117',
          light: '#3a2c1f',
          dark: '#1d160f',
        },
        // Warm ivory / cream backgrounds
        ivory: {
          DEFAULT: '#f7f1e3',
          deep: '#efe6d2',
          card: '#fffdf7',
        },
        // Muted antique-gold accents
        gold: {
          DEFAULT: '#b08d36',
          light: '#c9a85a',
          dark: '#8a6d28',
        },
        ink: '#2b2117',
        stone: '#7a6f5d',
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Georgia', 'Cambria', '"Times New Roman"', 'serif'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 8px 30px rgba(43, 33, 23, 0.08)',
        card: '0 2px 18px rgba(43, 33, 23, 0.06)',
      },
      backgroundImage: {
        'temple-fade': 'linear-gradient(180deg, rgba(43,33,23,0.0) 0%, rgba(43,33,23,0.55) 100%)',
      },
      keyframes: {
        fadeup: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        fadeup: 'fadeup 0.6s ease-out both',
      },
    },
  },
  plugins: [],
}
