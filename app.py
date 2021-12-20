from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    import src.etl as etl
    df_url = etl.get_daily_dataset_url('12-17-2021')
    result = etl.clean_dataset(df_url)
    # etl.fill_the_table('12-17-2021', result)
    print(etl.get_info_from_db('12-17-2021', 'Kharkiv Oblast'))
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
