from flask import Flask, jsonify, request, abort
import requests
from flask_cors import CORS
from datetime import datetime
from openai import OpenAI  # Import the OpenAI client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API Keys
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPENAI_API_KEY =  os.getenv("OPENAI_API_KEY") # Load OpenAI API key from .env
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # Load Google Maps API key from .env


# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)  # Define the client globally

def interpret_weather_code(weather_code):
    """Convert WMO weather code to a human-readable condition."""
    if weather_code == 0:
        return "Clear sky"
    elif weather_code == 1:
        return "Mainly clear"
    elif weather_code == 2:
        return "Partly cloudy"
    elif weather_code == 3:
        return "Overcast"
    elif weather_code in [51, 53]:
        return "Drizzle"
    elif weather_code in [61, 63, 65]:
        return "Rain"
    else:
        return "Unknown"

@app.route('/')
def home():
    return "Welcome to the Local Explorer Backend!"

@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch current hour's weather data for a given latitude and longitude.
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        abort(400, description="Latitude and longitude are required")

    # Parameters for the Open-Meteo API
    params = {
        'latitude': lat,
        'longitude': lon,
        'hourly': ['temperature_2m', 'weather_code'],  # Fetch temperature and weather codes
        'timezone': 'auto'  # Automatically detect the time zone
    }

    try:
        # Make a request to the Open-Meteo API
        response = requests.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Get the current hour in ISO 8601 format (e.g., "2023-10-25T21:00")
        now = datetime.utcnow()
        current_hour_iso = now.strftime("%Y-%m-%dT%H:00")

        # Find the index of the current hour in the time array
        times = data['hourly']['time']
        try:
            current_index = times.index(current_hour_iso)
        except ValueError:
            # If the current hour is not found, use the closest previous hour
            current_index = -1
            for i, time in enumerate(times):
                if time <= current_hour_iso:
                    current_index = i
                else:
                    break
            if current_index == -1:
                abort(404, description="No matching weather data found for the current hour")

        # Extract the current hour's data
        current_weather = {
            "time": times[current_index],
            "temperature": data['hourly']['temperature_2m'][current_index],
            "condition": interpret_weather_code(data['hourly']['weather_code'][current_index]),
        }

        return jsonify({"current_weather": current_weather})
    except requests.exceptions.RequestException as e:
        abort(500, description=f"Failed to fetch weather data: {str(e)}")

@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    """
    Generate AI-based activity suggestions based on the current weather.
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        abort(400, description="Latitude and longitude are required")

    try:
        # Fetch current weather data
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'hourly': ['temperature_2m', 'weather_code'],
            'timezone': 'auto'
        }
        weather_response = requests.get(OPEN_METEO_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Get the current hour's data
        now = datetime.utcnow()
        current_hour_iso = now.strftime("%Y-%m-%dT%H:00")
        times = weather_data['hourly']['time']
        current_index = times.index(current_hour_iso) if current_hour_iso in times else -1

        if current_index == -1:
            abort(404, description="No matching weather data found for the current hour")

        current_temp = weather_data['hourly']['temperature_2m'][current_index]
        current_condition = interpret_weather_code(weather_data['hourly']['weather_code'][current_index])

        # Generate AI suggestions using the new OpenAI API
        prompt = f"Suggest one outdoor fun activitie  for someone in a location with a temperature of {current_temp}°C and {current_condition} weather at {current_hour_iso}. Make the suggestions unique and weather-appropriate, Also, extract  keywords for the suggestion that can be used to search for nearby places."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the GPT-3.5 Turbo model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        suggestions = response.choices[0].message.content.strip()

        return jsonify({"suggestions": suggestions})
    except requests.exceptions.RequestException as e:
        abort(500, description=f"Failed to fetch weather data: {str(e)}")
    except Exception as e:
        abort(500, description=f"Failed to generate suggestions: {str(e)}")

@app.route('/api/places', methods=['GET'])
def get_places():
    """
    Proxy endpoint for Google Places API.
    """
    location = request.args.get('location')  # Format: "lat,lng"
    radius = request.args.get('radius')  # Radius in meters
    keyword = request.args.get('keyword')  # Keyword for search
    type = request.args.get('type')  # Place type (e.g., "park", "movie_theater")
    key = GOOGLE_MAPS_API_KEY  # Use the Google Maps API key from .env

    if not location or not radius or not key:
        abort(400, description="Missing required parameters: location, radius, or key")

    try:
        # Make a request to the Google Places API
        response = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": location,
                "radius": radius,
                "keyword": keyword,  # Optional: Keyword for search
                "type": type,  # Optional: Place type
                "key": key,
            }
        )
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Return the response to the frontend
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        abort(500, description=f"Failed to fetch places: {str(e)}")
if __name__ == '__main__':
    app.run(debug=True)