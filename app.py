from datetime import datetime
from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'api_key'


# 🔍 Helper: Get 3-day forecast from lat/lon or city
def get_three_day_forecast(api_key, query_param, is_coords=False):
    if is_coords:
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={query_param[0]}&lon={query_param[1]}&appid={api_key}&units=metric'
    else:
        url = f'https://api.openweathermap.org/data/2.5/forecast?q={query_param}&appid={api_key}&units=metric'

    response = requests.get(url)
    forecast = []

    if response.status_code == 200:
        data = response.json()
        daily_data = {}
        today = datetime.now().date()

        for item in data['list']:
            date_str = item['dt_txt'].split(' ')[0]
            time_str = item['dt_txt'].split(' ')[1]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            if date_obj > today:
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'temp_max': [],
                        'temp_min': [],
                        'humidity': [],
                        'wind': [],
                        'icon': None
                    }

                daily_data[date_str]['temp_max'].append(item['main']['temp_max'])
                daily_data[date_str]['temp_min'].append(item['main']['temp_min'])
                daily_data[date_str]['humidity'].append(item['main']['humidity'])
                daily_data[date_str]['wind'].append(item['wind']['speed'])

                # Use icon from 12:00 if available
                if time_str.startswith('12') and not daily_data[date_str]['icon']:
                    daily_data[date_str]['icon'] = item['weather'][0]['icon']

        count = 0
        for date_str in sorted(daily_data.keys()):
            if count == 3:
                break
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_data = daily_data[date_str]
            forecast.append({
                'date': date_str,
                'weekday': date_obj.strftime('%a'),  # Mon, Tue, etc.
                'temp': f"{round(max(day_data['temp_max']))}°/{round(min(day_data['temp_min']))}°",
                'humidity': round(sum(day_data['humidity']) / len(day_data['humidity'])),
                'wind': round(sum(day_data['wind']) / len(day_data['wind']), 2),
                'icon': day_data['icon'] or "01d"  # fallback icon
            })
            count += 1

    return forecast


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', weather=None)


@app.route('/search', methods=['POST'])
def search_city_weather():
    city = request.form.get('city')

    # Current weather
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return render_template('index.html', weather={'error': 'City not found'})

    weather_data = weather_response.json()

    # Get 3-day forecast
    forecast_grouped = get_three_day_forecast(API_KEY, city)

    # Use first day forecast as current day's max/min
    if forecast_grouped:
        current_day_temp = forecast_grouped[0]['temp']
    else:
        # fallback if no forecast data
        current_day_temp = f"{round(weather_data['main']['temp_max'])}°/{round(weather_data['main']['temp_min'])}°"

    weather = {
        'city': weather_data['name'],
        'temperature_current': round(weather_data['main']['temp']),
        'temperature': current_day_temp,
        'humidity': weather_data['main']['humidity'],
        'wind': weather_data['wind']['speed'],
        'description': weather_data['weather'][0]['description'],
        'icon': weather_data['weather'][0]['icon'],
        'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
        'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M'),
        'forecast': forecast_grouped
    }

    return render_template('index.html', weather=weather)


@app.route('/weather', methods=['POST'])
def get_weather_by_coords():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')

    if lat and lon:
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        response = requests.get(url)

        if response.status_code == 200:
            weather_data = response.json()
            forecast = get_three_day_forecast(API_KEY, (lat, lon), is_coords=True)

            if forecast:
                current_day_temp = forecast[0]['temp']
            else:
                current_day_temp = f"{round(weather_data['main']['temp_max'])}°/{round(weather_data['main']['temp_min'])}°"

            return jsonify({
                'city': weather_data['name'],
                'temperature_current': round(weather_data['main']['temp']),
                'temperature': current_day_temp,
                'humidity': weather_data['main']['humidity'],
                'wind': weather_data['wind']['speed'],
                'description': weather_data['weather'][0]['description'],
                'icon': weather_data['weather'][0]['icon'],
                'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M'),
                'forecast': forecast
            })
        else:
            return jsonify({'error': 'Weather not found'}), 404

    return jsonify({'error': 'Invalid coordinates'}), 400


if __name__ == '__main__':
    app.run(debug=True)
