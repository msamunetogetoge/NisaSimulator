import datetime
from dateutil import relativedelta

from oauth2client.service_account import ServiceAccountCredentials


class BaseConfig():
    now = datetime.datetime.now()
    starttime = now - relativedelta.relativedelta(years=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Auth Setting
    json_file = "elite-advice-299001-7f9acc2225b6.json"
    file_name = "NisaSimulatorGoogleFinance"

    # Accsess Spread Sheet
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    sheet_name = "ToDB"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file, scope)
