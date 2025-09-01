import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.[jt]sx?$/,
    exclude: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
      },
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0', // Allow external connections in Docker
    proxy: {
      '/api': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV 
          ? 'http://backend:8000'  // Docker environment
          : 'http://localhost:8000', // Local development
        changeOrigin: true,
      },
      '/ws': {
        target: process.env.NODE_ENV === 'development' && process.env.DOCKER_ENV
          ? 'ws://backend:8000'    // Docker environment
          : 'ws://localhost:8000', // Local development
        ws: true,
      },
    },
  },
  build: {
    outDir: 'build',
    sourcemap: true,
  },
})
