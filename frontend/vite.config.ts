import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/postcss'
import autoprefixer from 'autoprefixer'

export default defineConfig({
  plugins: [react()],
  css: {
    postcss: {
      plugins: [tailwindcss(), autoprefixer],
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/recommend': {
        target: 'http://localhost:8005',
        changeOrigin: true,
      },
      '/songs': {
        target: 'http://localhost:8005',
        changeOrigin: true,
      },
    },
  },
})
