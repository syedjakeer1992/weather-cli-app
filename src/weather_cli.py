# CLI commands
import click
import sqlite3
import datetime


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = sqlite3.connect('../weather_data.db')
    pass


@cli.command()
@click.pass_obj
@click.argument('city')
def latest(conn, city):
    """
    Retrieve the latest weather data for a given city.

    Args:
        conn (sqlite3.Connection): SQLite database connection object.
        city (str): City for which weather data is to be retrieved.

    Returns:
        int: Return code (0 for success).
    """
    try:
        c = conn.cursor()
        # Retrieve latest weather data from database
        c.execute("SELECT * FROM weather WHERE city=? ORDER BY update_datetime DESC LIMIT 1", (city,))
        data = c.fetchone()
        if data is None:
            print(f"No data available for {city}.")
        else:
            print(
                f"Temperature: {data[5]}°C, Humidity: {data[6]}%, Wind Speed: {data[7]}m/s, update_datetime: {data[9]}")
        return 0
    except sqlite3.Error as e:
        print(f"An error occurred while querying the database: {e}")


@cli.command()
@click.pass_obj
@click.argument('timeframe', type=click.Choice(['week', 'month', 'year']))
@click.argument('city')
def compare(conn, timeframe, city):
    """
    Compare the current weather data with average weather data for a given timeframe.

    Args:
        conn (sqlite3.Connection): SQLite database connection object.
        timeframe (str): Timeframe for which average weather data is to be calculated ('week', 'month', or 'year').
        city (str): City for which weather data is to be compared.

    Returns:
        int: Return code (0 for success).
    """
    global data, avg_temp
    try:
        c = conn.cursor()

        # Calculate average temperature for specified timeframe
        def query_builder(days):
            try:
                c.execute("SELECT AVG(group_avg_temp) from "
                          "(SELECT AVG(temperature) AS group_avg_temp,strftime('%d', update_datetime) "
                          " FROM weather WHERE city=?"
                          "AND date(update_datetime) >=? "
                          "group by strftime('%d', update_datetime)) ",
                          (city, (datetime.date.today() - datetime.timedelta(days=days))))
                return c.fetchone()
            except sqlite3.Error as e:
                print(f"An error occurred while querying the database: {e}")

        if timeframe == 'week':
            data = query_builder(7)
        elif timeframe == 'month':
            data = query_builder(30)
        elif timeframe == 'year':
            data = query_builder(365)
        if data is not None:
            avg_temp = data[0]
        else:
            print("No data found in the database.")

        # Retrieve latest weather data from database
        c.execute("SELECT temperature FROM weather WHERE city=? ORDER BY update_datetime DESC LIMIT 1", (city,))
        current_temp = c.fetchone()[0]

        # Compare current temperature to average temperature
        if current_temp > avg_temp:
            print(
                f"The current temperature is {current_temp}°C, which is above the average temperature for the past {timeframe}.")
        elif current_temp < avg_temp:
            print(
                f"The current temperature is {current_temp}°C, which is below the average temperature for the past {timeframe}.")
        else:
            print(
                f"The current temperature is {current_temp}°C, which is same as the average temperature for the past {timeframe}.")
        return 0
    except sqlite3.Error as e:
        print(f"An error occurred while querying the database: {e}")


@cli.command()
@click.pass_obj
@click.argument('month')
@click.argument('year')
@click.argument('city')
def average(conn, month, year, city):
    """
    Calculates and prints the average temperature for a given month and year in a specific city.

    Args:
        conn (object): The database connection object
        month (str): The month for which to calculate the average temperature (format: MM)
        year (str): The year for which to calculate the average temperature (format: YYYY)
        city (str): The city for which to calculate the average temperature

    Returns:
        int: 0 if successful, otherwise an error occurred while querying the database

    Raises:
        sqlite3.Error: If an error occurs while querying the database
    """
    try:
        c = conn.cursor()
        c.execute("SELECT AVG(group_avg_temp) from "
                  "(SELECT AVG(temperature) AS group_avg_temp,strftime('%d', update_datetime) "
                  " FROM weather WHERE city=? AND "
                  "strftime('%m',update_datetime)=? AND "
                  "strftime('%Y',update_datetime)=? group by strftime('%d', update_datetime)) ",
                  (city, month, year))
        avg_temp = c.fetchone()[0]
        if avg_temp is None:
            print(f"No data available for {month}/{year}.")
        else:
            print(f"The average temperature for {month}/{year} was {avg_temp}°C.")
        return 0
    except sqlite3.Error as e:
        print(f"An error occurred while querying the database: {e}")


if __name__ == '__main__':
    # Run CLI commands
    cli()
