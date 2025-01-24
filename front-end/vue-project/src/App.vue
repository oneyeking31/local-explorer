<template>
  <div class="app">
    <h1 class="app-title">Local Explorer</h1>
    <!-- Loading Message -->
    <div v-if="isLoading" class="loading">
      <p>Loading your location, weather, and suggestions...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="content">
      <!-- User Preferences -->
      <div class="preferences">
        <h3>Preferences</h3>
        <button @click="fetchSuggestions">Update Suggestions</button>
      </div>

      <!-- Swiper for Activity Suggestions -->
      <swiper class="swiper" :options="swiperOptions">
        <swiper-slide v-for="(activity, index) in activities" :key="index">
          <div class="activity-card">
            <h3>{{ activity.name }}</h3>
            <p>{{ activity.description }}</p>
          </div>
        </swiper-slide>
      </swiper>

      <!-- Google Map -->
      <div class="map-section">
        <GMapMap
          :center="mapCenter"
          :zoom="14"
          :options="{ googleMapsApiKey }"
          style="width: 100%; height: 50vh"
          ref="gMap"
        >
          <!-- User Location Marker -->
          <GMapMarker
            :position="mapCenter"
            title="Your Location"
            icon="https://maps.google.com/mapfiles/ms/icons/blue-dot.png"
          />

          <!-- Activity Markers -->
          <GMapMarker
            v-for="(place, index) in places"
            :key="index"
            :position="place.position"
            :title="place.name"
            icon="https://maps.google.com/mapfiles/ms/icons/red-dot.png"
            @click="openInfoWindow(place)"
          >
            <!-- Info Window -->
            <GMapInfoWindow
              :opened="place.infoWindowOpen"
              @closeclick="place.infoWindowOpen = false"
            >
              <div class="info-window">
                <h3>{{ place.name }}</h3>
                <p>{{ place.address }}</p>
                <img v-if="place.photo" :src="place.photo" alt="Place Photo" class="place-photo" />
                <p v-if="place.rating">Rating: {{ place.rating }} ⭐</p>
                <a
                  v-if="place.position"
                  :href="`https://www.google.com/maps/dir/?api=1&destination=${place.position.lat},${place.position.lng}`"
                  target="_blank"
                  class="directions-link"
                >
                  Get Directions
                </a>
              </div>
            </GMapInfoWindow>
          </GMapMarker>
        </GMapMap>
      </div>

      <!-- Weather Information -->
      <div v-if="currentWeather" class="weather-info">
        <h2 class="section-title">Weather in Your Location</h2>
        <div class="weather-details">
          <div class="weather-item">
            <span class="weather-label">Temperature:</span>
            <span class="weather-value">{{ currentWeather.temperature }}°C</span>
          </div>
          <div class="weather-item">
            <span class="weather-label">Time:</span>
            <span class="weather-value">{{ formatTimestamp(currentWeather.time) }}</span>
          </div>
          <div class="weather-item">
            <span class="weather-label">Condition:</span>
            <span class="weather-value">{{ currentWeather.condition }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
import { Swiper, SwiperSlide } from 'swiper/vue';
import 'swiper/swiper-bundle.css';

export default {
  components: {
    Swiper,
    SwiperSlide,
  },
  data() {
    return {
      mapCenter: { lat: 40.7128, lng: -74.0060 }, // Default to New York
      error: null,
      googleMapsApiKey: 'AIzaSyCad5HsS1V6EbBp69iJHpT9PAAlr1Nmvkc', // Replace with your actual API key
      isLoading: true,
      currentWeather: null, // Store current weather data
      suggestions: null, // Store AI-generated suggestions
      activities: [], // Store parsed activity suggestions
      places: [], // Store nearby places
      swiperOptions: {
        slidesPerView: 1,
        spaceBetween: 10,
        navigation: true,
      },
    };
  },
  async mounted() {
    await this.fetchUserLocation();
  },
  methods: {
    async fetchUserLocation() {
      try {
        const position = await this.getUserLocation();
        this.mapCenter = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        await this.fetchWeather(position.coords.latitude, position.coords.longitude);
        await this.fetchSuggestions();
      } catch (err) {
        console.error('Error fetching user location:', err);
        this.error = this.getLocationError(err);
      } finally {
        this.isLoading = false;
      }
    },
    getUserLocation() {
      return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000 });
        } else {
          reject(new Error('Geolocation is not supported by this browser.'));
        }
      });
    },
    async fetchWeather(lat, lon) {
      try {
        const response = await axios.get('http://localhost:5000/weather', {
          params: { lat, lon },
        });
        this.currentWeather = response.data.current_weather;
      } catch (error) {
        console.error('Error fetching weather data:', error);
        this.error = 'Failed to fetch weather data.';
      }
    },
    async fetchSuggestions() {
      try {
        // Clear existing places
        this.places = [];

        // Fetch new suggestions
        const response = await axios.get('http://localhost:5000/suggestions', {
          params: {
            lat: this.mapCenter.lat,
            lon: this.mapCenter.lng,
          },
        });
        this.suggestions = response.data.suggestions;
        console.log("Suggestions:", this.suggestions); // Log suggestions
        this.activities = this.parseSuggestions(this.suggestions);

        // Fetch nearby places based on suggestions
        await this.fetchNearbyPlaces();
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        this.error = 'Failed to fetch suggestions.';
      }
    },
    parseSuggestions(suggestions) {
      return suggestions.split('\n').map((line) => ({
        name: line.split('. ')[1] || line,
        description: line,
      }));
    },
    async fetchNearbyPlaces() {
      try {
        // Extract place names or keywords from suggestions
        const placeKeywords = this.extractPlaceKeywords(this.suggestions);

        // Fetch nearby places for each keyword
        for (const keyword of placeKeywords) {
          const places = await this.searchNearbyPlaces(keyword);
          this.places.push(...places);
        }

        console.log("Places to be marked on the map:", this.places); // Log places data

        // Force the map to update by re-rendering the markers
        this.$nextTick(() => {
          if (this.$refs.gMap) {
            this.$refs.gMap.$mapPromise.then((map) => {
              map.panTo(this.mapCenter); // Optional: Re-center the map
            });
          }
        });
      } catch (error) {
        console.error('Error fetching nearby places:', error);
        this.error = 'Failed to fetch nearby places.';
      }
    },
    extractPlaceKeywords(suggestions) {
      // Extract place names or keywords from suggestions
      const keywords = [];

      // List of outdoor activity keywords
      const outdoorKeywords = [
        "park",
        "cinema",
        "hiking trail",
        "beach",
        "lake",
        "playground",
        "garden",
        "zoo",
        "park",
        "cofe",
        "sports",
        "gym",
        "picnic area",
        "camping site",
        "nature reserve",
        "restaurant",
        "botanical garden",
        "skate park",
        "bike trail",
        "fishing spot",
        "market",
        "historical site",
      ];

      // Check if suggestions contain any of the outdoor keywords
      outdoorKeywords.forEach((keyword) => {
        if (suggestions.toLowerCase().includes(keyword)) {
          keywords.push(keyword);
        }
      });

      console.log("Extracted Keywords:", keywords); // Log extracted keywords
      return keywords;
    },
    async searchNearbyPlaces(keyword) {
      try {
        const response = await axios.get('http://localhost:5000/api/places', {
          params: {
            location: `${this.mapCenter.lat},${this.mapCenter.lng}`,
            radius: 5000,
            keyword: keyword, // Use keyword for general search
            type: this.getPlaceType(keyword), // Add the type parameter
            key: this.googleMapsApiKey,
          },
        });
        console.log("Google Places API Response for", keyword, ":", response.data); // Log API response
        return response.data.results.map((place) => ({
          name: place.name,
          address: place.vicinity,
          position: {
            lat: place.geometry.location.lat,
            lng: place.geometry.location.lng,
          },
          photo: place.photos
            ? `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${place.photos[0].photo_reference}&key=${this.googleMapsApiKey}`
            : null,
          rating: place.rating || 'No rating',
          infoWindowOpen: false,
        }));
      } catch (error) {
        console.error('Error searching nearby places:', error);
        return [];
      }
    },
    getPlaceType(keyword) {
      // Map keywords to Google Places API types
      switch (keyword.toLowerCase()) {
        case "park":
          return "park";
        case "movie theater":
          return "movie_theater";
        case "hiking trail":
          return "natural_feature";
        case "beach":
          return "natural_feature";
        case "lake":
          return "natural_feature";
        case "playground":
          return "park";
        case "garden":
          return "park";
        case "zoo":
          return "zoo";
        case "amusement park":
          return "amusement_park";
        case "sports":
          return "stadium";
        case "gym":
          return "gym";
        case "picnic area":
          return "park";
        case "camping site":
          return "campground";
        case "nature reserve":
          return "natural_feature";
        case "botanical garden":
          return "park";
        case "skate park":
          return "park";
        case "bike trail":
          return "route";
        case "fishing spot":
          return "natural_feature";
        case "market":
          return "shopping_mall";
        case "historical site":
          return "tourist_attraction";
        default:
          return ""; // No specific type
      }
    },
    openInfoWindow(place) {
      this.places.forEach((p) => (p.infoWindowOpen = false));
      place.infoWindowOpen = true;
    },
    formatTimestamp(isoTimestamp) {
      const date = new Date(isoTimestamp);
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return date.toLocaleString('en-US', options);
    },
    getLocationError(err) {
      switch (err.code) {
        case err.PERMISSION_DENIED:
          return 'Permission denied. Please enable location access in your browser settings.';
        case err.POSITION_UNAVAILABLE:
          return 'Location information is unavailable.';
        case err.TIMEOUT:
          return 'The request to get your location timed out.';
        default:
          return `Failed to fetch location: ${err.message}`;
      }
    },
  },
};
</script>
<style scoped>
.app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  text-align: center;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.app-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.loading,
.error {
  margin-top: 20px;
  font-size: 1.2rem;
  padding: 15px;
  border-radius: 8px;
}

.loading {
  color: #555;
  background-color: #f0f0f0;
}

.error {
  color: #fff;
  background-color: #ff6b6b;
}

.swiper {
  width: 100%;
  height: 200px;
  margin-bottom: 20px;
}

.activity-card {
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.activity-card h3 {
  margin: 0 0 10px;
  font-size: 1.2rem;
  color: #2c3e50;
}

.activity-card p {
  margin: 0;
  font-size: 1rem;
  color: #555;
}

.map-section {
  margin-top: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.weather-info {
  margin-top: 30px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 1.8rem;
  color: #34495e;
  margin-bottom: 15px;
}

.weather-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.weather-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.weather-label {
  font-weight: 600;
  color: #555;
}

.weather-value {
  font-weight: 500;
  color: #2c3e50;
}

.info-window {
  max-width: 200px;
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-window h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.info-window p {
  margin: 5px 0 0;
  font-size: 1rem;
  color: #555;
}

.place-photo {
  width: 100%;
  border-radius: 8px;
  margin-top: 10px;
}

.directions-link {
  display: inline-block;
  margin-top: 10px;
  color: #2c3e50;
  text-decoration: none;
  font-weight: bold;
}

.directions-link:hover {
  text-decoration: underline;
}
</style>