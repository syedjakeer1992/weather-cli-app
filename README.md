# Weather Data CLI

Weather Data CLI is a command-line interface (CLI) tool for retrieving and analyzing weather data from an SQLite database. It provides commands to retrieve the latest weather data, compare current temperature with average temperature for a specified timeframe, and calculate the average temperature for a specific month and year of your favourite city.
This tool has two modules weather_fetcher.py and weather_cli.py and for retrieving data we are using a free trial of weather API from https://www.weatherapi.com/. Please use the following link for API documentation https://www.weatherapi.com/api-explorer.aspx to understand the request and response data structures as well as input parameters

- weather_feather has the required methods to continuously make API call to get the frequent data and also get the historic weather data of certain date range and insert the data into database
    1. command to get the latest weather data point of a specific city from the API and schedule it.
    2. command to get historic weather data of a specific city from the API.

- weather_cli has the required methods to complete the following task
    1. command to query the latest data point of a specific city. 
    2. command to compare the current weather with an average of the last week (last 7 days), month and year of a specific city. 
    3. command to display the average temperature for a certain month of a certain year of a specific city.

## Prerequisites

- Python 3.9.5 
- SQLite3 database for storing weather data
- Click 8.1.3 (Python package for creating command-line interfaces) installed. You can install it using `pip`:
- Requests 2.28.2 (Python package for running API requests) installed.
- Schedule 1.2.0 (Python package to schedule recurring jobs) installed.

You can install all the above packages using `pip`  and `python setup` as mentioned in the commands.

## Installation

1. Clone the repository  to your local machine.

2. Install the required dependencies using `pip` and `python setup`:

### Commands

`pip install -r requirements.txt`
or
`python setup.py install`

1. `get_historic_weather` : Retrieves historic weather data from API for certain amount of time 
   
`python src/weather_fetcher.py  get-historic-weather [CITY] [API_KEY] [DAYS]`

- Replace `[CITY]` with the name of the city for which you want to retrieve the historic weather data.
- Replace `[API_KEY]` with the API key of the weather API.
- Replace `[DAYS]` with the number of days of historic data required.

2. `get_latest_weather`: Retrieves latest weather data from API and starts the scheduler to continuously get the data from API

`python src/weather_fetcher.py get-latest-weather [CITY] [API_KEY] [DAYS]`

- Replace `[CITY]` with the name of the city for which you want to retrieve the latest weather data.
- Replace `[API_KEY]` with the API key of the weather API.
- Replace `[FREQUENCY]` with the time interval in minutes, to continuously get the latest data from API.

3. `latest`: Retrieves the latest weather data for a specific city.

`python src/weather_cli.py latest [CITY] `

- Replace `[CITY]` with the name of the city for which you want to retrieve the latest weather data.
  
4. `compare`: Compares the current temperature with the average temperature for a specified timeframe of a specific city.

`python src/weather_cli.py compare [TIMEFRAME] [CITY] `
   
- Replace `[TIMEFRAME]` with the desired timeframe (e.g., `week`, `month`, `year`) and `[CITY]` with the name of the city for which you want to compare the temperatures of a specific city.

5. `average`: Calculates the average temperature for a specific month and year.

`python src/weather_cli.py average [MONTH] [YEAR] [CITY] `

- Replace `[MONTH]` with the numeric representation of the month (e.g., `01` for January, `02` for February), `[YEAR]` with the year (e.g., 2023, 2022 etc), and `[CITY]` with the name of the city to calculate the average temperature.