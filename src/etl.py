import re
import sqlite3

import pandas as pd
import requests


def get_daily_dataset_url(date):
    # Check date format (only MM-DD-YYYY is acceptable)
    if re.search("^(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])-20(20|21|22)$", date) is None:
        raise ValueError('Date format error')
    base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
    file_extension = '.csv'
    # final dataset URL
    dataset_url = base_url + date + file_extension
    return dataset_url


def clean_dataset(dataset_url):
    # Get the dataset
    daily_dataset = requests.get(dataset_url).url
    # Load CSV
    df_all_countries = pd.read_csv(daily_dataset)
    # Select Ukraine only
    ukraine_dataset = df_all_countries[df_all_countries["Country_Region"] == "Ukraine"]
    # Clean the dataset
    ukraine_dataset = ukraine_dataset.drop(["FIPS", "Admin2", "Last_Update", "Lat", "Long_", "Combined_Key"], axis=1)
    ukraine_dataset.fillna(0, inplace=True)
    ukraine_dataset[["Confirmed", "Deaths", "Recovered", "Active", "Incident_Rate", "Case_Fatality_Ratio"]] = \
        ukraine_dataset[["Confirmed", "Deaths", "Recovered", "Active", "Incident_Rate", "Case_Fatality_Ratio"]].apply(
            pd.to_numeric, errors='coerce')
    # Add total row
    ukraine_dataset.loc['all'] = ukraine_dataset.sum(numeric_only=True)
    ukraine_dataset.fillna(0, inplace=True)
    return ukraine_dataset


def fill_the_table(date, dataset):
    # Check date format (only MM-DD-YYYY is acceptable)
    if re.search("^(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])-20(20|21|22)$", date) is None:
        raise ValueError('Date format error')
    # Connect to the database
    con = sqlite3.connect('covid19-informator.sqlite')
    # Save the dataset to table with Date name
    dataset.to_sql(date, con=con)
    # Close connection
    con.close()


def if_the_table_exists(table_name):
    con = sqlite3.connect('covid19-informator.sqlite')
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name",
                         {"table_name": table_name})
    result = cur.fetchone()
    con.close()
    if result is not None:
        return True
    else:
        return False
