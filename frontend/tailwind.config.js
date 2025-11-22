/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Outfit', 'sans-serif'],
      },
      colors: {
        background: '#0f172a', // Slate 900
        surface: '#1e293b',    // Slate 800
        primary: {
          DEFAULT: '#6366f1',  // Indigo 500
          hover: '#4f46e5',    // Indigo 600
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#ec4899',  // Pink 500
          hover: '#db2777',    // Pink 600
          foreground: '#ffffff',
        },
        accent: {
          DEFAULT: '#8b5cf6',  // Violet 500
          foreground: '#ffffff',
        },
        muted: {
          DEFAULT: '#94a3b8',  // Slate 400
          foreground: '#cbd5e1', // Slate 300
        },
        border: '#334155',     // Slate 700
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
