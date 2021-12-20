from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    import src.etl as etl
    df_url = etl.get_daily_dataset_url('12-17-2021')
    result = etl.clean_dataset(df_url)
    #etl.fill_the_table('12-17-2021', result)
    return result.to_string()


if __name__ == '__main__':
    app.run()
