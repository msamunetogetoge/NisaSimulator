from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pandas as pd
import datetime
from config import BaseConfig
import time
import gspread


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nisa.db"
db = SQLAlchemy(app)


class GraphBase(db.Model):
    """[summary] グラフを描くためのモデル
    date: 年月日
    name:銘柄名
    close:値段
    Args:
        db ([type]): [description]
    """
    date = db.Column(db.DateTime, primary_key=True)
    name = db.Column(db.String, primary_key=True)
    close = db.Column(db.Float)
    updatetime = db.Column(db.DateTime)


class NameBase(db.Model):
    """[summary]
    name: Graph のname
    namedisplay: SBIキーワードで表示する名前
    searchname : pandas で検索するのにつかう第一引数
    """
    name = db.Column(db.String, primary_key=True)
    searchname = db.Column(db.String)
    searchkeyword = db.Column(db.String)


class CalculateResult(db.Model):
    """[summary]
    date: 年月日
    name: Graphのname
    resultpercent:パーセント形式の結果
    resultint:数値形式の結果
    """
    date = db.Column(db.DateTime, primary_key=True)
    name = db.Column(db.String, primary_key=True)
    method_name = db.Column(db.String,default =BaseConfig.method_dict[0])
    resultpercent = db.Column(db.Float)
    resultint = db.Column(db.Integer)


def CreateTables():
    """[summary]
    dbとテーブルを作る
    """
    db.create_all()
    return


def CreateNameBase():
    """[summary]
    NameBaseテーブルにデータを登録する.GoogleFinance を使用
    """
    name2disp = dict()
    name2disp["MSCI_ACWI"] = ["全世界", 'ACWI']
    name2disp['sp500'] = ["S＆P", 'SPY']
    name2disp["nikkei225"] = ["日経", "NI225"]
    name2disp["topix"] = ["topix", 'topix']
    name2disp["FTSE_Emerging"] = ["新興国株式インデックス・ファンド", 'VWO']
    name2disp["MSCI_World"] = ["先進国", 'VEA']
    for key in name2disp.keys():
        n = NameBase(
            name=key,
            searchkeyword=name2disp[key][0],
            searchname=name2disp[key][1])
        db.session.add(n)
    try:
        db.session.commit()
    except Exception:

        db.session.rollback()
    return


def CreateGraphBase():
    """[summary]
    今日から1年前までのデータ取得->GraphBase 登録する
    """
    try:
        df = get_datas()
    except Exception:
        return
    cols = list(df.columns)
    u = datetime.date.today()
    try:
        for col in cols:
            data = df[col]
            for i, d in enumerate(data):
                ind = data.index[i]
                g = GraphBase(date=ind, name=col, close=d, updatetime=u)
                db.session.add(g)
        db.session.commit()
    except Exception:
        db.session.rollback()
    try:
        gs = GraphBase.query.filter(GraphBase.updatetime != u).all()
        db.session.delete(gs)
    except Exception:
        db.session.rollback()
    return


def UpdateGraphBase():
    """[summary]
    add_datas()で最終更新日+1日から今日までのデータを取得し、dbに値を加える
    """
    try:
        from_time = GraphBase.query.with_entities(
            GraphBase.date).order_by(GraphBase.date.desc()).first()[0]
        now_time = datetime.datetime.now()
        df = add_datas(from_time=from_time, now_time=now_time)
    except Exception as e:
        print(f"get_data 失敗 {e}")
        return
    cols = list(df.columns)
    u = datetime.date.today()

    for col in cols:
        data = df[col]
        for i, d in enumerate(data):
            try:
                ind = data.index[i]
                g = GraphBase(date=ind, name=col, close=d, updatetime=u)
                if(GraphBase.query.filter_by(date=ind, name=col).first() is None):
                    db.session.add(g)
                db.session.commit()
            except Exception as e:
                print(f"UpdateGraphBase でエラーが発生。{e}")
                db.session.rollback()
    return


def make_series(name: str, displayname: str, from_time: datetime.datetime = BaseConfig.starttime, now_time: datetime.datetime = datetime.datetime.today()) -> pd.Series:
    """[summary] spread sheet で、from_timeから、now_timeの期間のインデックスのデータを取得し、pd.series を返す。デフォルトは本日から一年前まで

    Args:
        name(str) : [description] 列名

    Returns:
        [type]pandas.Series: [description] index,name付きのpandas.Series
    """
    try:
        gc = gspread.authorize(BaseConfig.credentials)
        sh = gc.open(BaseConfig.file_name)
        start = from_time
        start_year = start.year
        start_month = start.month
        start_day = start.day
        if start_day < 1:
            start_day = 1
        start_string = f"DATE({start_year},{start_month},{start_day})"
        end = now_time
        end_year = end.year
        end_month = end.month
        end_day = end.day
        end_string = f"DATE({end_year},{end_month},{end_day})"
        command = f'=GoogleFinance("{name}","close",{start_string},{end_string},"DAILY")'
        ws = sh.worksheet(BaseConfig.sheet_name)
        # セルの初期化
        ws.update_acell("A1", "")
        ws.update_acell("A1", command)
        time.sleep(0.1)
        # データの更新待ち,5秒経ったら諦める
        timer = time.time()
        while ws.acell('A1').value != "Date":
            timer_end = time.time()
            if timer_end - timer > 5:
                df = pd.Series()
                ws.update_acell("A1", "")
                return df
            continue
        df = pd.DataFrame(ws.get_all_values())
        df.columns = list(df.loc[0, :])
        df.drop(0, inplace=True)
        df.reset_index(inplace=True)
        df.drop('index', axis=1, inplace=True)
        # dfの型を変更
        df["Date"] = pd.to_datetime(df["Date"])
        df["Close"] = pd.to_numeric(df["Close"], downcast='float')
        df = df.rename(columns={"Close": displayname})
        s = pd.Series(data=df[displayname])
        s.index = df["Date"].dt.date
        df = s

    except Exception as e:
        print(f"{make_series.__name__}: throws exception {e}")
        df = pd.Series()
    finally:
        return df


def get_datas() -> pd.DataFrame:
    """[summary]
    1年前までさかのぼってデータを収集し、datafameを返す
    Returns:
        [type pandas.DataFrame]: [description] 取得したデータをまとめたdataframe
    """
    # 取得するデータの開始日と最終日を指定
    names = NameBase.query.with_entities(
        NameBase.searchname, NameBase.name).all()
    df = pd.Series()
    for i, n in enumerate(names):
        try:
            if i == 0:
                base = pd.DataFrame(make_series(name=n[0], displayname=n[1]))
            else:
                s = make_series(name=n[0], displayname=n[1])
                df = base.join(s)
                base = df
        except Exception:
            continue
    return df


def add_datas(from_time: datetime.datetime, now_time: datetime.datetime) -> pd.DataFrame:
    """[summary]
    from_time +1日からnow_timeまでのデータを収集し、datafameを返す
    Args:
        from_time (datetime.date): [description]
        now_time (datetime.date): [description]

    Returns:
        pd.DataFrame: [description]
    """
    from_time = from_time + datetime.timedelta(days=1)
    names = NameBase.query.with_entities(
        NameBase.searchname, NameBase.name).all()
    df = pd.DataFrame()
    for i, n in enumerate(names):
        # join を使いたいので変な書き方する
        try:
            if i == 0:
                base = pd.DataFrame(make_series(
                    name=n[0], displayname=n[1], from_time=from_time, now_time=now_time))
            else:
                s = make_series(name=n[0], displayname=n[1],
                                from_time=from_time, now_time=now_time)
                df = base.join(s)
                base = df
                print(f"base = {base.head()}")
        except Exception as e:
            print(f"{add_datas.__name__}: throw exception {e}")
            continue
    print(f"{add_datas.__name__}: returns df, type = {type(df)}")
    return df
