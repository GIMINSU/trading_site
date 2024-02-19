import sys
from os import path

from flask import Flask, render_template, request
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
logging.basicConfig(filename="./development.log", level=logging.DEBUG)

def add_to_sys_path(directory):
    directory_path = path.abspath(path.join(directory))
    if directory_path not in sys.path:
        sys.path.append(directory_path)

# Add the application path to sys.path
add_to_sys_path("")

# Add the config path to sys.path
add_to_sys_path("..")

app = Flask(__name__)

@app.route("/investment_sense_meter", methods=["GET", "POST"])
def flask_first_page():
    target_code_str = "005930"
    investment_days_int = 30
    target_return_rate_float = 5.0
    max_predicted_date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    predicted_date_str = (datetime.now() - timedelta(days=investment_days_int+1)).strftime("%Y-%m-%d")
    real_return_rate_float = None
    rate_diff = None
    predicted_close = None
    end_close = None

    if request.method == "POST":
        predicted_date_str = request.form.get('input_predicted_date_str')
        target_code_str = request.form.get('input_target_code_str')
        investment_days_int = request.form.get('input_investment_days_int')
        target_return_rate_float = request.form.get('input_target_return_rate_float')

    investment_days_int = int(investment_days_int)
    
    target_return_rate_float = float(target_return_rate_float)

    import FinanceDataReader as fdr

    df = fdr.DataReader(target_code_str, start=predicted_date_str)
    df = df.reset_index()
    search_max_date = df["Date"].iloc[-1]
    end_date = (datetime.strptime(predicted_date_str, "%Y-%m-%d") + timedelta(days=investment_days_int))
    df = df[df["Date"] <= end_date].reset_index(drop=True)
    
    if end_date <= search_max_date:
        end_date_str = end_date.strftime("%Y-%m-%d")
        predicted_close = round(df["Close"].iloc[0], 2)
        end_close = round(df["Close"].iloc[-1], 2)
        real_return_rate_float = round((end_close - predicted_close) / predicted_close, 3)
        rate_diff =  real_return_rate_float - target_return_rate_float
    else:
        possible_days = (search_max_date - datetime.strptime(predicted_date_str, "%Y-%m-%d")).days
        real_return_rate_float = "측정 불가"
        rate_diff = "측정불가"
        end_date_str = f"현재 예측일 기준 최대 선택 가능 일수 : {possible_days}"

    return render_template("first_page.html",
    max_predicted_date_str = max_predicted_date_str,
    predicted_date_str = predicted_date_str,
    target_code_str = target_code_str,
    investment_days_int = investment_days_int,
    target_return_rate_float = target_return_rate_float,
    real_return_rate_float=real_return_rate_float,
    rate_diff = rate_diff,
    predicted_close = predicted_close,
    end_close = end_close,
    end_date_str=end_date_str
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)