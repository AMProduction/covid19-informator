from datetime import date, timedelta

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/show', methods=('GET', 'POST'))
def show_historical_data():
    if request.method == 'POST':
        search_date = request.form['datepicker']
        region_code = request.form['region']
        # Check if table/data exists
        import src.etl as etl
        if etl.if_the_table_exists(search_date):
            result_json = etl.get_info_from_db(search_date, region_code)
        else:
            df_url = etl.get_daily_dataset_url(search_date)
            result_dataset = etl.clean_dataset(df_url)
            etl.fill_the_table(search_date, result_dataset)
            result_json = etl.get_info_from_db(search_date, region_code)
    return render_template('index.html', data=result_json)


@app.route('/')
def home():
    # Initial loading of the main page
    today = date.today()
    # Get and format yesterday date
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%m-%d-%Y')
    # Check if table/data exists
    import src.etl as etl
    if etl.if_the_table_exists(yesterday):
        result_json = etl.get_info_from_db(yesterday, 'all')
    else:
        df_url = etl.get_daily_dataset_url(yesterday)
        result_dataset = etl.clean_dataset(df_url)
        etl.fill_the_table(yesterday, result_dataset)
        result_json = etl.get_info_from_db(yesterday, 'all')
    return render_template('index.html', data=result_json)


if __name__ == '__main__':
    app.run()
