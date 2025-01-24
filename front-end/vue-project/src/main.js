import { createApp } from 'vue';
import App from './App.vue';
import VueGoogleMaps from '@fawmi/vue-google-maps'; // Correct import

const app = createApp(App);

// Initialize vue-google-maps
app.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyCad5HsS1V6EbBp69iJHpT9PAAlr1Nmvkc', // Replace with your actual API key
    libraries: 'places', // Optional: Add additional libraries if needed
  },
});

app.mount('#app');