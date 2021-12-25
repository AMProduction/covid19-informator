from datetime import date, timedelta

from flask import Flask, render_template, request

import src.etl as etl

app = Flask(__name__)


@app.route('/show', methods=('GET', 'POST'))
def show_historical_data():
    if request.method == 'POST':
        search_date = request.form['datepicker']
        region_code = request.form['region']
        result_json = etl.etl(search_date, region_code)
    return render_template('index.html', data=result_json, date=search_date, region=region_code)


@app.route('/')
def home():
    # Initial loading of the main page
    today = date.today()
    # Get and format yesterday date
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%m-%d-%Y')
    result_json = etl.etl(yesterday, 'all')
    return render_template('index.html', data=result_json, date=yesterday, region='Whole country')


if __name__ == '__main__':
    app.run()
