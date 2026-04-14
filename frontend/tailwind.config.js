/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // ── Color tokens — matched to seanwa.com dark theme ──────────────────
      colors: {
        background:  "#0a0e1a",
        foreground:  "#e7eef3",
        card:        "#0f1524",
        surface:     "#141c2e",
        primary: {
          DEFAULT:    "#7577f0",
          foreground: "#0a0e1a",
        },
        secondary: {
          DEFAULT:    "#20283c",
          foreground: "#c5d0e8",
        },
        muted: {
          DEFAULT:    "#1b2232",
          foreground: "#7588a3",
        },
        accent: {
          DEFAULT:    "#1a1a4d",
          foreground: "#9a9cf4",
        },
        border: "#222939",
        input:  "#222939",
        ring:   "#7577f0",
      },
      borderRadius: {
        sm:    "0.375rem",
        md:    "0.625rem",
        lg:    "0.75rem",
        xl:    "1rem",
        "2xl": "1.25rem",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      keyframes: {
        "bounce-dot": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":       { transform: "translateY(-4px)" },
        },
        spin: { to: { transform: "rotate(360deg)" } },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%":       { opacity: "0.3" },
        },
        "aurora-1": {
          "0%":   { transform: "translate(0,0) scale(1)" },
          "100%": { transform: "translate(8%,18%) scale(1.18)" },
        },
        "aurora-2": {
          "0%":   { transform: "translate(0,0) scale(1.05)" },
          "100%": { transform: "translate(-12%,12%) scale(0.92)" },
        },
        "aurora-3": {
          "0%":   { transform: "translate(0,0) scale(0.9)" },
          "100%": { transform: "translate(6%,-22%) scale(1.22)" },
        },
        "fade-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "bounce-dot": "bounce-dot 1s ease-in-out infinite",
        spin:         "spin 0.8s linear infinite",
        pulse:        "pulse 1.5s ease-in-out infinite",
        "aurora-1":   "aurora-1 20s ease-in-out infinite alternate",
        "aurora-2":   "aurora-2 26s ease-in-out infinite alternate",
        "aurora-3":   "aurora-3 18s ease-in-out infinite alternate",
        "fade-in":    "fade-in 0.4s ease forwards",
      },
    },
  },
  plugins: [],
};
