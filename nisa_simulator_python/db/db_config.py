import datetime
from dateutil import relativedelta

from oauth2client.service_account import ServiceAccountCredentials


class DBConfig():
    """DB読み込み、書き込みに関する設定の為のクラス
    """
    now = datetime.datetime.now()
    starttime = now - relativedelta.relativedelta(years=1)
    db_uri = "sqlite:///db/nisa.db"

    # Auth Setting
    json_file = "elite-advice-299001-7f9acc2225b6.json"
    file_name = "NisaSimulatorGoogleFinance"

    # Accsess Spread Sheet
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    sheet_name = "ToDB"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_file, scope)
