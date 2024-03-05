import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objs as go


def parse_weather_data(url):
    """
        Parses weather data from the specified URL.

        Args:
        url (str): The URL of the webpage containing the weather data.

        Returns:
        pandas.DataFrame: A DataFrame containing the parsed weather data.
        """
    response = requests.get(url)  # Sending an HTTP GET request to the specified URL
    if response.status_code == 200:  # Checking if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')  # Parsing the HTML content of the webpage

        table = soup.find('table')  # Finding the table element containing the weather data

        if table:
            headers = [th.text.strip() for th in table.find('tr').find_all('th')]

            df = pd.DataFrame(columns=headers[:4])

            rows = table.find_all('tr')  # Finding all table rows

            for row in rows[1:]:  # Iterating over each row (skipping the header row)
                data = [td.text.strip() for td in row.find_all('td')]  # Extracting data from each cell in the row
                df = df._append(pd.Series(data[:4], index=df.columns), ignore_index=True)  # Adding a new row to the DataFrame

            return df

        else:
            print('Table not find.')
    else:
        print('The website could not be accessed.')


def visual_temp(df):
    df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y')

    # Create a month column
    df['Месяц'] = df['Дата'].dt.to_period('M')

    # Converting the "Average Temperature" column to a number format
    df['Средняя температура'] = pd.to_numeric(df['Средняя температура'], errors='coerce')

    # We group the data by month and calculate the average, maximum and minimum temperature for each month
    monthly_stats = df.groupby('Месяц').agg({
        'Максимальная температура': 'max',
        'Минимальная температура': 'min',
        'Средняя температура': 'mean'
    }).reset_index()

    print(monthly_stats)
    """
        Visualizes the temperature data from the DataFrame.

        Args:
        df (pandas.DataFrame): DataFrame containing temperature data.
        """
    # Creating a scatter plot
    trace_max = go.Scatter(x=df['Дата'], y=df['Максимальная температура'], name='MaxTemp')
    trace_min = go.Scatter(x=df['Дата'], y=df['Минимальная температура'], name='MinTemp')
    trace_mean = go.Scatter(x=df['Дата'], y=df['Средняя температура'], name='MeanTemp')

    legend = go.Layout(legend=dict(orientation='h'))  # Creating layout with horizontal legend

    # Creating a plotly figure with the traces and layout
    fig = go.Figure(data=[trace_max, trace_min, trace_mean, ], layout=legend)

    fig.show() # Displaying the plotly figure


if __name__ == '__main__':
    website_url = 'http://pogoda-service.ru/archive_gsod_res.php?country=AY&station=890090&datepicker_beg=01.01.2023&datepicker_end=31.12.2023&bsubmit=Посмотреть'

    df = parse_weather_data(website_url)
    visual_temp(df)
