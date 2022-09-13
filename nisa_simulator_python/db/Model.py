import datetime
import time

import gspread
import pandas as pd
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime


from db_config import DBConfig

# todo dbのアップデートなどが動くか確認する

Base = declarative_base()
engine = create_engine(DBConfig.db_uri, echo=True)
Session = sessionmaker(bind=engine)

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nisa.db"
# db = SQLAlchemy(app)


class GraphData(Base):
    """[summary] グラフを描くためのモデル
    date: 年月日
    name:銘柄名
    close:値段
    Args:
        db ([type]): [description]
    """
    __table_name__ = "graph_data"
    date = Column(DateTime, primary_key=True)
    name = Column(String, primary_key=True)
    close = Column(Float)
    updatetime = Column(DateTime)


class NameBase(Base):
    """[summary]
    name: Graph のname
    namedisplay: SBIキーワードで表示する名前
    searchkeyword : pandas で検索するのにつかう第一引数
    """

    __table_name__ = "name_base"
    name = Column(String, primary_key=True)
    searchname = Column(String)
    searchkeyword = Column(String)


class CalculateResult(Base):
    """[summary]
    date: 年月日
    name: Graphのname
    resultpercent:パーセント形式の結果
    resultint:数値形式の結果
    method_name: 計算方式
    """
    __table_name__ = "calculate_result"
    date = Column(DateTime, primary_key=True)
    name = Column(String, primary_key=True)
    resultpercent = Column(Float)
    resultint = Column(Integer)
    method_name = Column(Integer, default=0, primary_key=True)


def CreateTables():
    """[summary]
    dbとテーブルを作る
    """
    Base.metadata.create_all(engine)
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

    session = Session()
    for key in name2disp.keys():
        n = NameBase(
            name=key,
            searchkeyword=name2disp[key][0],
            searchname=name2disp[key][1])
        session.add(n)
    try:
        session.commit()
    except Exception:

        session.rollback()
    return


def CreateGraphData():
    """[summary]
    今日から1年前までのデータ取得->GraphData 登録する
    """
    try:
        df = get_datas()
    except Exception:
        return
    cols = list(df.columns)
    u = datetime.date.today()
    try:
        session = Session()
        for col in cols:
            data = df[col]
            for i, d in enumerate(data):
                ind = data.index[i]
                g = GraphData(date=ind, name=col, close=d, updatetime=u)
                session.add(g)
        session.commit()
    except Exception:
        session.rollback()
    try:
        gs = GraphData.query.filter(GraphData.updatetime != u).all()
        session.delete(gs)
    except Exception:
        session.rollback()
    return


def UpdateGraphData():
    """[summary]
    add_datas()で最終更新日+1日から今日までのデータを取得し、dbに値を加える
    insert で既にデータがある時は、insertしようとした日付に、updatetimeを更新する
    """
    try:
        from_time = GraphData.query.with_entities(
            GraphData.date).order_by(GraphData.date.desc()).first()[0]
        now_time = datetime.datetime.now()
        df = add_datas(from_time=from_time, now_time=now_time)
    except Exception as e:
        print(f"get_data 失敗 {e}")
        return
    cols = list(df.columns)
    u = datetime.date.today()

    # GraphData にデータがあればupdate, なければinsert する
    session = Session()
    for col in cols:
        data = df[col]
        for i, d in enumerate(data):
            try:
                ind = data.index[i]
                new_close = GraphData(date=ind, name=col,
                                      close=d, updatetime=u)
                close = GraphData.query.filter_by(date=ind, name=col).first()
                if (close):
                    session.merge(new_close)
                else:
                    session.add(new_close)
                session.commit()

            except Exception as e:
                print(f"UpdateGraphData でエラーが発生。{e}")
                session.rollback()
    return


def make_series(name: str, displayname: str, from_time: datetime.datetime = DBConfig.starttime, now_time: datetime.datetime = datetime.datetime.today()) -> pd.Series:
    """[summary] spread sheet で、from_timeから、now_timeの期間のインデックスのデータを取得し、pd.series を返す。デフォルトは本日から一年前まで

    Args:
        name(str) : [description] 列名

    Returns:
        [type]pandas.Series: [description] index,name付きのpandas.Series
    """
    try:
        gc = gspread.authorize(DBConfig.credentials)
        sh = gc.open(DBConfig.file_name)
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
        ws = sh.worksheet(DBConfig.sheet_name)
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
        except Exception as e:
            print(f"{add_datas.__name__}: throw exception {e}")
            continue
    return df
