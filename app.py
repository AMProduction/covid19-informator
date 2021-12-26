from flask import Flask, render_template, request

import src.etl as etl

app = Flask(__name__)


@app.route('/show', methods=('GET', 'POST'))
def show_historical_data():
    if request.method == 'POST':
        search_date = request.form['datepicker']
        region_code = request.form['region']
        result_json = etl.etl(search_date, region_code)
        if result_json['Province'] == 'all':
            search_date = etl.get_yesterday_date()
            region_code = 'all'
    return render_template('index.html', data=result_json, date=search_date, region=region_code)


@app.route('/')
def home():
    # Initial loading of the main page
    result_json = etl.etl(etl.get_yesterday_date(), 'all')
    return render_template('index.html', data=result_json, date=etl.get_yesterday_date(), region='Whole country')


if __name__ == '__main__':
    app.run()
