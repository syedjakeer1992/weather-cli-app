import requests
import sqlite3
import schedule
import datetime
import time
import click

# API endpoint and parameters
BASEURL = "http://api.weatherapi.com/v1"
CURRENT_API = BASEURL + "/current.json"
HISTORY_API = BASEURL + "/history.json"

# Connect to SQLite database
conn = sqlite3.connect('weather_data.db')
c = conn.cursor()

# Create table to store weather data
c.execute('''CREATE TABLE IF NOT EXISTS weather
             (id INTEGER PRIMARY KEY, 
              city TEXT, 
              country TEXT,
              latitude REAL,
              longitude REAL,
              temperature REAL, 
              humidity INTEGER, 
              wind_speed REAL, 
              precipitation REAL,
              update_datetime TEXT,                         
              CONSTRAINT ct UNIQUE (city, update_datetime))''')


def weather_api_call(endpoint, params):
    """
     Calls the Weather API endpoint with the given parameters and returns the API response.

     Args:
         endpoint (str): The API endpoint URL.
         params (dict): Dictionary containing the API parameters.

     Returns:
         dict: Dictionary containing the API response data.
     """
    global response
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving weather data: {e}, Status code: {response.status_code}")
    except KeyError as e:
        print(f"Error parsing API response: {e}")
    finally:
        print("Response received from API")


def weather_info_insert(weather_info, conn, c):
    """
    Inserts weather information into the SQLite database.

    Args:
        weather_info (dict): Dictionary containing weather information to be inserted.
        conn (sqlite3.Connection): SQLite database connection object.
        c (sqlite3.Cursor): SQLite database cursor object.
    """
    try:
        c.execute("INSERT INTO weather (city,  country, latitude, longitude, temperature, humidity, wind_speed,"
                  "precipitation, update_datetime)"
                  "VALUES (:city, :country, :latitude, :longitude, :temperature, :humidity, :wind_speed,"
                  ":precipitation, :update_datetime)", weather_info)
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Database already up to date with latest information")
        conn.rollback()
    except sqlite3.Error as e:
        print(f"Error inserting data into database: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error: {e}")


@click.group()
def cli():
    pass


@cli.command()
@click.argument('city')
@click.argument('api_key')
@click.argument('days', type=int)
def get_historic_weather(city, api_key, days):
    """
    Retrieves historic weather data from the Weather API for the given city and stores it in the SQLite database.

    Args:
        city (str): City name for which historic weather data is to be retrieved.
        api_key (str): API key for accessing the Weather API.
        days (int): Number of days of historic data to be retrieved.
    """
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=days)

    """ Loop through each day in the month or year """
    while start_date < end_date:
        # Format the date in the required API parameter format
        startdate = start_date.strftime('%Y-%m-%d')

        params = {'q': city, 'key': api_key, 'dt': startdate}
        print(f"Retrieving historic weather data from API for city: {city}")
        historic_data = weather_api_call(HISTORY_API, params)
        historic_weather_info = {'city': historic_data['location']['name'],
                                 'country': historic_data['location']['country'],
                                 'latitude': historic_data['location']['lat'],
                                 'longitude': historic_data['location']['lon'],
                                 'temperature': historic_data['forecast']['forecastday'][0]['day']['avgtemp_c'],
                                 'humidity': historic_data['forecast']['forecastday'][0]['day']['avghumidity'],
                                 'wind_speed': historic_data['forecast']['forecastday'][0]['day']['maxwind_mph'],
                                 'precipitation': historic_data['forecast']['forecastday'][0]['day']['totalprecip_mm'],
                                 'update_datetime': historic_data['forecast']['forecastday'][0]['date']}
        print(f"historic weather data {historic_weather_info} for {city} city for date {startdate}")
        print(f"Writing current weather information for {city} city into database")
        weather_info_insert(historic_weather_info, conn, c)
        print(f"Database updated successfully with the historic weather data for {city} city and date {startdate}")
        # Move to the next day
        start_date += datetime.timedelta(days=1)
    print(f"Database updated successfully with the last {days} weather data for {city} city")


@cli.command()
@click.argument('city')
@click.argument('api_key')
@click.argument('frequency', type=int)
def get_latest_weather(city, api_key, frequency):
    """
      Retrieve and store the latest weather data for a given city.

      Args:
          city (str): City name for which weather data is to be retrieved.
          api_key (str): API key for accessing the weather API.
          frequency (int): Frequency in minutes at which to update the weather data.

      Returns:
          None

      Raises:
          None
      """

    def get_current_weather(city, api_key, c):
        """
        Retrieve the current weather data from the weather API and store it in the database.

        Args:
            city (str): City name for which weather data is to be retrieved.
            api_key (str): API key for accessing the weather API.
            c (sqlite3.Connection): SQLite3 database connection.

        Returns:
            None

        Raises:
            None
        """
        params = {'q': city, 'key': api_key}
        current_data = weather_api_call(CURRENT_API, params)
        print(f"Retrieving latest weather from API for city: {city}")
        current_weather_info = {'city': current_data['location']['name'],
                                'country': current_data['location']['country'],
                                'latitude': current_data['location']['lat'],
                                'longitude': current_data['location']['lon'],
                                'temperature': current_data['current']['temp_c'],
                                'humidity': current_data['current']['humidity'],
                                'wind_speed': current_data['current']['wind_mph'],
                                'precipitation': current_data['current']['precip_mm'],
                                'update_datetime': current_data['current']['last_updated']}
        print(f"current weather data {current_weather_info} for {city} city")
        print(f"Writing current weather information for {city} city into database")
        weather_info_insert(current_weather_info, c, conn)
        print(f"Database updated successfully with the latest weather updates for {city} city")

    get_current_weather(city, api_key, conn)
    print(f"Starting the Scheduler to get weather updates for {city} city every {frequency} minutes")
    schedule.every(frequency).minutes.do(get_current_weather, city, api_key, c)
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
            time_of_next_run = schedule.next_run()
            time_now = datetime.datetime.now()
            time_remaining = time_of_next_run - time_now
            print(f"Time left to get the next update {time_remaining}")
        except Exception as e:
            print("An error occurred in process:", e)


if __name__ == '__main__':
    # Run CLI commands
    cli()
