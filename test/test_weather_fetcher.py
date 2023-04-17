import unittest
from src.weather_fetcher import weather_info_insert, weather_api_call
from unittest.mock import patch
import sqlite3
import requests


class TestWeatherFetcher(unittest.TestCase):
    """
    The TestWeatherFetcher class is a unit test class that tests the functionality
    of the weather_info_insert() and weather_api_call() functions in the
    src.weather_fetcher module.
    """

    def setUp(self):
        """
        Set up the test environment before each test case is executed.
        """
        self.conn = sqlite3.connect(":memory:")
        self.c = self.conn.cursor()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS weather
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
        self.conn.commit()

    def test_insert_weather_data_to_db(self):
        """
        Test inserting weather data into the database.
        """
        weather_data = {'city': 'TestCity',
                        'country': 'TestCountry',
                        'latitude': 26.43,
                        'longitude': 50.11,
                        'temperature': 27.5,
                        'humidity': 35,
                        'wind_speed': 45.6,
                        'precipitation': 5.9,
                        'update_datetime': '2023-04-15 19:45'}

        weather_info_insert(weather_data, self.conn, self.c)

        """ Verify that the data is inserted correctly into the database """

        self.c.execute("SELECT * FROM weather WHERE city=?", ('TestCity',))

        result = self.c.fetchone()
        print(result)
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'TestCity')
        self.assertEqual(result[2], 'TestCountry')
        self.assertEqual(result[3], 26.43)
        self.assertEqual(result[4], 50.11)
        self.assertEqual(result[5], 27.5)
        self.assertEqual(result[6], 35)
        self.assertEqual(result[7], 45.6)
        self.assertEqual(result[8], 5.9)
        self.assertEqual(result[9], '2023-04-15 19:45')

    @patch('requests.get')
    def test_weather_api_call_success(self, mock_get):
        """
        Test making a successful API call to fetch weather data.
        Mock the requests.get() method with a successful response.
        """
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = lambda: {
            'location': {'name': 'City', 'country': 'Country'},
            'current': {'temp_c': 25, 'humidity': 70, 'wind_mph': 5, 'precip_mm': 0, 'last_updated': '2023-04-15 19:45'}
        }
        mock_get.return_value = mock_response

        """ Call the weather_api_call() function """
        endpoint = 'http://api.weatherapi.com/v1/current.json'
        params = {'q': 'City', 'key': 'API_KEY'}
        result = weather_api_call(endpoint, params)

        """ Assert that the returned data matches the expected data """
        expected_data = {
            'location': {'name': 'City', 'country': 'Country'},
            'current': {'temp_c': 25, 'humidity': 70, 'wind_mph': 5, 'precip_mm': 0, 'last_updated': '2023-04-15 19:45'}
        }
        self.assertEqual(result, expected_data)
        mock_get.assert_called_once_with(endpoint, params=params)

    @patch('requests.get')
    def test_weather_api_call_failure(self, mock_get):
        """
        Test making a failed API call to fetch weather data.Mock the requests.get() method with a failed response
        """
        mock_response = requests.Response()
        mock_response.status_code = 500
        mock_response.json = lambda: {'error': 'Internal Server Error'}
        mock_get.return_value = mock_response

        """ Call the weather_api_call() function """
        endpoint = 'http://api.weatherapi.com/v1/current.json'
        params = {'q': 'City', 'key': 'API_KEY'}
        result = weather_api_call(endpoint, params)

        """ Assert that correct failed response is returned """
        self.assertEqual(result, {'error': 'Internal Server Error'})
        mock_get.assert_called_once_with(endpoint, params=params)


if __name__ == '__main__':
    unittest.main()
