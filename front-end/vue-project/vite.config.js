import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools'; // Import Vue DevTools plugin

export default defineConfig({
  plugins: [
    vue(), // Vue plugin
    vueDevTools(), // Add Vue DevTools plugin
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',  // Your Flask backend URL
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  optimizeDeps: {
    include: ['fast-deep-equal'], // Explicitly include problematic modules
  },
  resolve: {
    alias: {
      'vue-google-maps': '@fawmi/vue-google-maps',
      // Add any necessary aliases here
    },
  },
});