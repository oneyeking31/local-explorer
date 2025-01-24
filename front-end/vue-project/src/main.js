import { createApp } from 'vue';
import App from './App.vue';
import VueGoogleMaps from '@fawmi/vue-google-maps'; // Correct import

const app = createApp(App);

// Initialize vue-google-maps
app.use(VueGoogleMaps, {
  load: {
    key: process.env.GOOGLE_MAPS_API_KEY, // Replace with your actual API key
    libraries: 'places', // Optional: Add additional libraries if needed
  },
});

app.mount('#app');
