# Local Explorer 🌍

Local Explorer is a web application that suggests fun outdoor activities based on your current location and weather conditions. It uses real-time weather data, AI-generated suggestions, and an interactive map to help you explore your surroundings.

---

## Features ✨

- **Real-Time Weather Data**: Fetches current weather conditions using the **Open-Meteo API**.
- **AI-Powered Suggestions**: Generates personalized activity suggestions using **OpenAI GPT**.
- **Interactive Map**: Displays nearby places using the **Google Maps API**.
- **User-Friendly Interface**: Simple and intuitive design for a seamless user experience.

---

## Technologies Used 🛠️

- **Backend**: Flask (Python)
- **Frontend**: Vue.js (JavaScript)
- **APIs**:
  - [Open-Meteo API](https://open-meteo.com/) for weather data.
  - [OpenAI GPT](https://platform.openai.com/) for activity suggestions.
  - [Google Maps API](https://developers.google.com/maps) for map integration.

---

## Installation and Setup 🚀

Follow these steps to set up and run the project locally.

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/local-explorer.git
cd local-explorer
```
2. Set Up Environment Variables
Create a .env file in the root directory and add your API keys:
Copy
# .env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

Note: If you're using the .env.example file as a template, rename it to .env and replace the placeholder values with your actual API keys.


Install Python Dependencies
**
🛠️ pip install -r requirements.txt 🛠️

4. Run the Backend Server
flask run

Set Up the Frontend :
cd frontend
npm install

Start the frontend development server:
npm run serve
