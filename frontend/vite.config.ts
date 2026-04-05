import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
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
