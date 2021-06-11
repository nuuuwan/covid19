"""Sri Lanka specific COVID19 data."""

from covid19 import covid_data

def get_timeseries():
    return covid_data.load_jhu_data()['LK']['timeseries']
