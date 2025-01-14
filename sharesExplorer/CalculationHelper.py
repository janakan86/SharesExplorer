import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import date
from datetime import timezone
import numpy as np


def get_todays_price(code):
    # very slow. Consider downloading and storing prices per day
    ticker = yf.Ticker(str(code) + ".ax").info
    return float(ticker['regularMarketPreviousClose'])


def years_in_between(date_latest, date_earlier):
    dt_object_earliest = to_datetime(date_earlier)
    dt_object_latest = to_datetime(date_latest)

    gap = dt_object_latest.date() - dt_object_earliest.date()
    gap_in_seconds = gap.total_seconds()
    gap_in_years = gap_in_seconds / 31536000
    return gap_in_years


def years_from_today(date_str):
    today = date.today()
    dt_object = to_datetime(date_str)
    gap = today - dt_object.date()

    # if bought today consider it bought a day before to avoid division by zero
    if gap.total_seconds() == 0.0:
        gap_in_seconds = 86400
    else:
        gap_in_seconds = gap.total_seconds()

    gap_in_years = gap_in_seconds / 31536000
    return gap_in_years


# https://gist.github.com/blaylockbk/1677b446bc741ee2db3e943ab7e4cabd?permalink_comment_id=3775327
def to_datetime(date):
    """
    Converts a numpy datetime64 object to a python datetime object
    Input:
      date - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
                 / np.timedelta64(1, 's'))
    return datetime.fromtimestamp(timestamp, timezone.utc)

def write_to_excel(data_frame, sheet_name):
    with pd.ExcelWriter(
            "/Users/kanaganayagamjanakan/Documents/cagr.xlsx"
    ) as writer:
        data_frame.to_excel(writer, sheet_name=sheet_name)