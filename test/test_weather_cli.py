import unittest
import sqlite3
import click
from click.testing import CliRunner
from src import weather_cli
from src.weather_cli import latest, compare, average
from src.weather_fetcher import weather_info_insert


class TestWeatherCli(unittest.TestCase):
    """
    The TestWeatherFetcher class is a unit test class that tests the functionality
    of the weather_cli commands latest(), compare() and average() functions in the
    src.weather_cli module.
    """


    def setUp(self):
        """
        Set up the test environment before each test case is executed.
        """
        self.conn = sqlite3.connect(":memory:")
        self.c = self.conn.cursor()
        self.runner = CliRunner()
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

        test_data = [{'city': 'Frankfurt',
                      'country': 'Germany',
                      'latitude': 26.43,
                      'longitude': 50.11,
                      'temperature': 27.5,
                      'humidity': 35,
                      'wind_speed': 46.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-04-13'},
                     {'city': 'Frankfurt',
                      'country': 'Germany',
                      'latitude': 26.43,
                      'longitude': 50.11,
                      'temperature': 27.5,
                      'humidity': 35,
                      'wind_speed': 46.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-04-13 19:45'},
                     {'city': 'Frankfurt',
                      'country': 'Germany',
                      'latitude': 26.43,
                      'longitude': 50.11,
                      'temperature': 45.5,
                      'humidity': 35,
                      'wind_speed': 46.6,
                      'precipitation': 5.9,
                      'update_datetime': '2022-04-13 19:45'},
                     {'city': 'Frankfurt',
                      'country': 'Germany',
                      'latitude': 27.43,
                      'longitude': 54.11,
                      'temperature': 35.5,
                      'humidity': 35,
                      'wind_speed': 48.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-04-15'},
                     {'city': 'Stuttgart',
                      'country': 'Germany',
                      'latitude': 27.43,
                      'longitude': 54.11,
                      'temperature': 27.5,
                      'humidity': 35,
                      'wind_speed': 48.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-04-13'},
                     {'city': 'Frankfurt',
                      'country': 'Germany',
                      'latitude': 27.43,
                      'longitude': 54.11,
                      'temperature': 25.5,
                      'humidity': 35,
                      'wind_speed': 48.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-03-20'},
                     {'city': 'Munich',
                      'country': 'Germany',
                      'latitude': 26.43,
                      'longitude': 50.11,
                      'temperature': 27.5,
                      'humidity': 35,
                      'wind_speed': 45.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-04-13'},
                     {'city': 'Heidelberg',
                      'country': 'Germany',
                      'latitude': 26.43,
                      'longitude': 50.11,
                      'temperature': 27.5,
                      'humidity': 35,
                      'wind_speed': 45.6,
                      'precipitation': 5.9,
                      'update_datetime': '2023-04-13'}
                     ]
        for i in test_data:
            weather_info_insert(i, self.conn, self.c)
        self.conn.commit()

    def tearDown(self):
        """
        Clean up the test environment after each test case is executed.
        """
        self.c.execute(f"Drop table weather")
        self.conn.close()


    def test_latest_command(self):
        """
        Test case for the latest command with a valid city name
        """
        result = self.runner.invoke(latest, ['Frankfurt'], obj= self.conn)
        expected_output = f"Temperature: 35.5°C, Humidity: 35%, Wind Speed: 48.6m/s, update_datetime: 2023-04-15"
        self.assertEqual(result.exit_code, 0)
        self.assertIn(result.output.strip(),expected_output)


    def test_compare_command(self):
        """
        Test the compare command with a valid city name by passing week,month and year as argument.
        """
        result = self.runner.invoke(compare, ['week','Frankfurt'], obj= self.conn)
        expected_week_output = f"The current temperature is 35.5°C, which is above the average temperature for the past week."
        self.assertEqual(result.exit_code, 0)
        self.assertIn(result.output.strip(), expected_week_output)
        result = self.runner.invoke(compare, ['month', 'Frankfurt'], obj=self.conn)
        expected_month_output = f"The current temperature is 35.5°C, which is above the average temperature for the past month."
        self.assertIn(result.output.strip(), expected_month_output)
        result = self.runner.invoke(compare, ['year', 'Frankfurt'], obj=self.conn)
        self.assertEqual(result.exit_code, 0)
        expected_year_output = f"The current temperature is 35.5°C, which is above the average temperature for the past year."
        self.assertIn(result.output.strip(), expected_year_output)

    def test_average_command(self):
        """
        Test case for the average command with a valid city name and month and year .
        """
        result = self.runner.invoke(average, ['04', '2023', 'Frankfurt'], obj= self.conn)
        expected_output = f"The average temperature for 04/2023 was 31.5°C."
        self.assertEqual(result.exit_code, 0)
        self.assertIn(result.output.strip(),expected_output)



if __name__ == '__main__':
    unittest.main()
