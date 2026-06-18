import time
from datetime import datetime

# --- Configuration ---
# NOTE: In a real application, you would replace this with a valid API 
Key from a service like OpenWeatherMap.
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
CITY = "London"  # Change this to your desired city
RAIN_THRESHOLD = 5  # Rain level (in mm/hour or similar metric) that 
triggers the alert

def fetch_weather(city: str, api_key: str) -> dict:
    """
    Fetches mock weather data for a given city.
    
    *** REAL-WORLD NOTE: Replace this mock function with actual requests 
to a Weather API. ***
    """
    print(f"Attempting to fetch weather data for {city}...")
    
    # --- MOCK DATA IMPLEMENTATION (For demonstration purposes) ---
    if city == "London":
        # Simulate rain sometimes, simulate dry sometimes
        import random
        if random.choice([True, False]):
            temp = round(random.uniform(5.0, 15.0), 1)
            rainfall = round(random.uniform(0.0, 10.0), 2) # Simulate 
rain detection
            condition = "Rainy" if rainfall >= RAIN_THRESHOLD else 
"Cloudy"
        else:
            temp = round(random.uniform(15.0, 25.0), 1)
            rainfall = round(random.uniform(0.1, 4.9), 2) # Simulate dry 
conditions
            condition = "Clear"
    else:
        # Default mock data for other cities
        temp = round(random.uniform(10.0, 20.0), 1)
        rainfall = round(random.uniform(0.0, 5.0), 2)
        condition = "Cloudy"

    return {
        "city": city,
        "temperature": temp,
        "rainfall": rainfall,
        "condition": condition
    }


def notify_rain(data: dict):
    """
    Generates and prints a notification when the rain threshold is met.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "="*50)
    print(f"🚨 RAIN ALERT! NOTIFICATION SENT at {timestamp} 🚨")
    print(f"Location: {data['city']}")
    print(f"Condition: {data['condition']}")
    print(f"Current Rainfall: {data['rainfall']} mm/hr (Threshold is 
{RAIN_THRESHOLD} mm/hr)")
    print("--------------------------------------------------\n")


def run_notifier():
    """
    Main function to continuously monitor the weather and notify the 
user.
    """
    if API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        print("ERROR: Please configure your API_KEY in the script before 
running.")
        return

    print(f"--- Rain Notifier Initialized ---")
    print(f"Monitoring City: {CITY}")
    print(f"Rain Trigger Threshold: {RAIN_THRESHOLD} mm/hr\n")

    while True:
        try:
            # 1. Fetch the weather data
            weather_data = fetch_weather(CITY, API_KEY)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Weather 
Update:")
            print(f"  Temperature: {weather_data['temperature']}°C")
            print(f"  Rainfall Rate: {weather_data['rainfall']} mm/hr")
            print(f"  Current Condition: {weather_data['condition']}")

            # 2. Check the condition and notify
            if weather_data['rainfall'] >= RAIN_THRESHOLD:
                notify_rain(weather_data)
            
            # 3. Wait for a specified time before checking again (Polling 
interval)
            sleep_time = 60  # Check every 60 seconds
            print(f"\nWaiting for {sleep_time} seconds...\n")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n\nRain Notifier stopped by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            # Wait longer before retrying if an API connection fails
            time.sleep(300) 


if __name__ == "__main__":
    runNotifier()