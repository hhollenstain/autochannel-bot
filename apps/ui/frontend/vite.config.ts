import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// In dev the Flask API runs on :5000; proxy everything that isn't the SPA to it so the
// session cookie stays same-origin.
const api = process.env.API_URL ?? 'http://localhost:5000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': api,
      '/login': api,
      '/logout': api,
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
});
