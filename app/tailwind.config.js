/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#0B1929",
        dark: "#1E293B",
        seg: {
          tech: "#4F8EF7",
          budget: "#F87171",
          core: "#34C97A",
          family: "#A78BFA",
          pet: "#F59E0B",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
}
