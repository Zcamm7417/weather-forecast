from configparser import ConfigParser
import argparse, pprint, json, sys, os
from urllib import parse, request, error
from module_api import _api_key


def _get_api_key():
    return _api_key()


def read_user_cli_args():
    """Handles the CLI user interactions.

    Returns:
        argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description = 'get weather and temperature information for a city'
    )
    parser.add_argument(
        'city', nargs='+', type=str, help='enter the city name' 
    )
    parser.add_argument(
        '-i',
        '--imperial',
        action='store_true',
        help='display the temperature in imperial units',
    )
    return parser.parse_args(input('Enter city_name: '))

BASE_WEATHER_API_URL ='https://api.openweathermap.org/data/2.5/weather'

def build_weather_query(city_input, imperial=False):
    api_key = _get_api_key()
    city_name = ''.join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = 'imperial' if  imperial else 'metric'
    url = (
        f'{BASE_WEATHER_API_URL}?q={url_encoded_city_name}'
        f'&units={units}&appid={api_key}'
    )
    return url

def get_weather_data(query_url):
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  #unauthorized
            sys.exit('Access denield. Check your API key.')
        elif http_error.code == 404:   #not found
            sys.exit('Can not find weather data for this city.')
        elif http_error.code == 11004:
            sys.exit('No internet connection')
        else:
            sys.exit(f'somethiing went wrong...({http_error.code})')#({http_error.code})')
    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit('Could not read the server response.')

def display_weather_info(weather_data, imperial=False):
    city = weather_data['name']
    weather_id = weather_data['weather'][0]['id']
    country = weather_data['sys']['country']
    weather_description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    clouds = weather_data['clouds']['all']

    print(f'City: {city}', end='\n')
    print(f'Country: {country}', end='\n')
    print(f'Weather status: {weather_description.capitalize()}', end='\n')
    print(f"Temperature: ({temperature} degree {'F' if imperial else 'C'})")
    print(f'Humidity: {humidity}', end = '\n')
    print(f'Clouds: {clouds}', end = '\n')

if __name__== '__main__':
    user_args=read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)
