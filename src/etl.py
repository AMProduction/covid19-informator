import collections
import logging
import re
import sqlite3
from datetime import date, timedelta

import pandas as pd
import requests


def get_yesterday_date():
    today = date.today()
    # Get and format yesterday date
    yesterday = today - timedelta(days=1)
    return yesterday.strftime('%m-%d-%Y')


def get_daily_dataset_url(date):
    # Check date format (only MM-DD-YYYY is acceptable)
    if re.search("^(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])-20(19|20|21|22)$", date) is None:
        raise ValueError('Date format error')
    base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
    file_extension = '.csv'
    # final dataset URL
    dataset_url = base_url + date + file_extension
    return dataset_url


def is_source_exists(url):
    response = requests.get(url)
    if response.ok:
        return True
    else:
        return False


def clean_dataset(dataset_url):
    # Get the dataset
    daily_dataset = requests.get(dataset_url).url
    # Load CSV
    df_all_countries = pd.read_csv(daily_dataset)
    # Check .csv formatting (There is an old file format)
    if "Country_Region" in df_all_countries:
        # Select Ukraine only
        ukraine_dataset = df_all_countries[df_all_countries["Country_Region"] == "Ukraine"]
        # Clean the dataset
        ukraine_dataset = ukraine_dataset.drop(["FIPS", "Admin2", "Last_Update", "Lat", "Long_", "Combined_Key"], axis=1)
        ukraine_dataset.fillna(0, inplace=True)
        ukraine_dataset[["Confirmed", "Deaths", "Recovered", "Active", "Incident_Rate", "Case_Fatality_Ratio"]] = \
            ukraine_dataset[["Confirmed", "Deaths", "Recovered", "Active", "Incident_Rate", "Case_Fatality_Ratio"]].apply(
                pd.to_numeric, errors='coerce')
        # Some calculations
        confirmed_total = ukraine_dataset['Confirmed'].sum()
        deaths_total = ukraine_dataset['Deaths'].sum()
        incident_rate_median = ukraine_dataset['Incident_Rate'].median()
        case_fatality_ratio_median = ukraine_dataset['Case_Fatality_Ratio'].median()
        # Total row
        total_data = {'Province_State': ['all'],
                      'Country_Region': ['Ukraine'],
                      'Confirmed': [confirmed_total],
                      'Deaths': [deaths_total],
                      'Recovered': [0],
                      'Active': [0],
                      'Incident_Rate': [incident_rate_median],
                      'Case_Fatality_Ratio': [case_fatality_ratio_median]
                      }
        total_row = pd.DataFrame(total_data, index=['0'])
        # Add the new total row
        ukraine_dataset = ukraine_dataset.append(total_row)
        return ukraine_dataset
    else:
        return None


def fill_the_table(date, dataset):
    # Connect to the database
    con = sqlite3.connect('covid19-informator.sqlite')
    # Save the dataset to table with Date name
    try:
        with con:
            dataset.to_sql(date, con=con)
    except sqlite3.IntegrityError:
        print('Error during insert data')
        logging.error('Error during insert data')
    finally:
        # Close connection
        con.close()


def is_the_table_exists(table_name):
    con = sqlite3.connect('covid19-informator.sqlite')
    cur = con.cursor()
    # Check if the table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name",
                {"table_name": table_name})
    result = cur.fetchone()
    con.close()
    if result is not None:
        return True
    else:
        return False


def get_info_from_db(table_name, region):
    con = sqlite3.connect('covid19-informator.sqlite')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM '{table_name}' WHERE Province_State='{region}'")
    result = cur.fetchall()
    # Save the result to the JSON
    for row in result:
        dict = collections.OrderedDict()
        dict['index'] = row[0]
        dict['Province'] = row[1]
        dict['Country'] = row[2]
        dict['Confirmed'] = row[3]
        dict['Deaths'] = row[4]
        dict['Recovered'] = row[5]
        dict['Active'] = row[6]
        dict['Incident_Rate'] = row[7]
        dict['Case_Fatality_Ratio'] = row[8]
    con.close()
    return dict


def etl(search_date, region_code):
    # Check if table exists/data already in DB
    if is_the_table_exists(search_date):
        # If YES - just get the data
        result_json = get_info_from_db(search_date, region_code)
    else:
        # If NO:
        df_url = get_daily_dataset_url(search_date)
        # Check if .csv is exists
        # If YES - download and process
        if is_source_exists(df_url):
            result_dataset = clean_dataset(df_url)
            # Check format file check result
            if result_dataset is not None:
                fill_the_table(search_date, result_dataset)
                result_json = get_info_from_db(search_date, region_code)
            else:
                result_json = get_info_from_db(get_yesterday_date(), 'all')
        # If NO - get yesterday data
        else:
            result_json = get_info_from_db(get_yesterday_date(), 'all')
    return result_json
