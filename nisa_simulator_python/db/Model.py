import datetime
import time
from webbrowser import get

import gspread
import pandas as pd
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime


from db.db_config import DBConfig


Base = declarative_base()
engine = create_engine(DBConfig.db_uri, echo=True)
Session = sessionmaker(bind=engine)
DbConfig: DBConfig = DBConfig()


class GraphData(Base):
    """[summary] グラフを描くためのモデル
    date: 年月日
    name:銘柄名
    close:値段
    Args:
        db ([type]): [description]
    """
    __tablename__ = "graph_data"
    date = Column(DateTime, primary_key=True)
    name = Column(String, primary_key=True)
    close = Column(Float)
    updatetime = Column(DateTime)


class _GraphData:
    """DBのGraphDataのcreate, updateを行うクラス
    ただし、create, updateで登録するデータは呼び出された日(now) ~ nowから1年前までのデータ
    """

    def __init__(self, db_config: DBConfig):
        self.db_config = db_config

    def update_config(self, now: datetime.datetime) -> None:
        """self.db_config のstart_time, nowを更新する

        Args:
            now (datetime.datetime): _description_
        """
        self.db_config.cls_update_now_start_time(now=now)

    def update(self):
        """db_config.DBConfig の日付を使ってGraphDataをupdateする
        """
        session = Session()
        try:
            close_of_updating = self.__pack_close_data()
        except Exception as error_of_update_graph_data:
            print(f"get_data 失敗 {error_of_update_graph_data}")
            return
        cols = list(close_of_updating.columns)
        today = self.db_config.now

        # GraphData にデータがあればupdate, なければinsert する
        for col in cols:
            data = close_of_updating[col]
            for i, close in enumerate(data):
                try:
                    ind = data.index[i]
                    new_close = GraphData(date=ind, name=col,
                                          close=close, updatetime=today)
                    close = session.query(GraphData).filter_by(
                        date=ind, name=col).first()
                    if close is None:
                        session.add(new_close)
                    else:
                        session.merge(new_close)
                    session.commit()

                except Exception as error_of_update_graph_data:
                    print(
                        f"UpdateGraphData でエラーが発生。{error_of_update_graph_data}")
                    session.rollback()
        return

    def create(self):
        """GraphDataにinsertする。
        insertするデータは、NameBase.name からGoogleFinanceで集めた
        self.db_config.start_time ~ self.db_config.now までの、Closeのデータ。
        """
        try:
            close_data: pd.DataFrame = self.__pack_close_data()
        except Exception:
            return
        cols = list(close_data.columns)
        today: datetime = self.db_config.now
        try:
            session = Session()
            for col in cols:
                data = close_data[col]
                for i, d in enumerate(data):
                    ind = data.index[i]
                    graph_data: GraphData = GraphData(
                        date=ind, name=col, close=d, updatetime=today)
                    session.add(graph_data)
            session.commit()
        except Exception:
            session.rollback()
        return

    def __pack_close_data(self) -> pd.DataFrame:
        """[summary]
        db_config.DBConfig.starttimeからdb_config.DBConfig.nowまでのデータを収集し、DataFrameにまとめる。
        DataFrameの列名はNameBase.name
        Returns:
            [type pandas.DataFrame]: [description] 取得したデータをまとめたdataframe。 col はNameBase.name
        """
        session = Session()
        names = session.query(
            NameBase.searchname, NameBase.name).all()
        close = pd.Series()
        for i, name_information in enumerate(names):
            try:
                name = name_information[0]
                display_name = name_information[1]
                if i == 0:
                    base = pd.DataFrame(self.__fetch_close_from_spread_sheet(
                        name=name, display_name=display_name))
                else:
                    close_series = self.__fetch_close_from_spread_sheet(
                        name=name, display_name=display_name)
                    close = base.join(close_series)
                    base = close
            except Exception:
                continue
        return close

    def __fetch_close_from_spread_sheet(self, name, display_name) -> pd.Series:
        """[summary] spread sheet で、インデックスのデータを取得し、pd.series を返す。本日(この関数が呼ばれた時)から一年前までのデータを取得する。

        Args:
            name(str) : [description] GoogleFinanceで検索に使う名前
            display_name(str): [description] Series のname

        Returns:
            [type]pandas.Series: [description] index,name付きのpandas.Series. indexは株価の日付、nameはdisplay_name
        """

        # self.db_configの更新
        now_time: datetime.datetime = datetime.datetime.now()
        self.update_config(now=now_time)
        # データ作成
        try:
            gspread_client = gspread.authorize(self.db_config.credentials)
            spread_sheet = gspread_client.open(self.db_config.file_name)
            start = self.db_config.starttime
            start_year = start.year
            start_month = start.month
            start_day = start.day
            if start_day < 1:
                start_day = 1
            start_string = f"DATE({start_year},{start_month},{start_day})"
            end = self.db_config.now
            end_year = end.year
            end_month = end.month
            end_day = end.day
            end_string = f"DATE({end_year},{end_month},{end_day})"
            # spread sheetで株価データを取得するコマンド
            command = f'=GoogleFinance("{name}","close",{start_string},{end_string},"DAILY")'
            work_sheet = spread_sheet.worksheet(DBConfig.sheet_name)
            # セルの初期化
            work_sheet.update_acell("A1", "")
            # コマンドの設定
            work_sheet.update_acell("A1", command)
            # データの更新待ち,5秒経ったら諦める
            timer = time.time()
            while work_sheet.acell('A1').value != "Date":
                timer_end = time.time()
                if timer_end - timer > 5:
                    df = pd.Series(name='Error_Series')
                    work_sheet.update_acell("A1", "")
                    return df
                continue
            df = pd.DataFrame(work_sheet.get_all_values())
            df.columns = list(df.loc[0, :])
            df.drop(0, inplace=True)
            df.reset_index(inplace=True)
            df.drop('index', axis=1, inplace=True)
            # dfの型を変更
            df["Date"] = pd.to_datetime(df["Date"])
            df["Close"] = pd.to_numeric(df["Close"], downcast='float')
            df = df.rename(columns={"Close": display_name})
            s = pd.Series(data=df[display_name])
            s.index = df["Date"].dt.date
            df = s

        except Exception as error_of_make_series:
            print(f"{make_series.__name__}: throws exception {error_of_make_series}")
            df = pd.Series(name='Error_Series')

        return df


class NameBase(Base):
    """[summary]
    name: Graph のname
    namedisplay: SBIキーワードで表示する名前
    searchkeyword : pandas で検索するのにつかう第一引数
    """

    __tablename__ = "name_base"
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
    __tablename__ = "calculate_result"
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
    for key, _ in name2disp.items():
        name_base = NameBase(
            name=key,
            searchkeyword=name2disp[key][0],
            searchname=name2disp[key][1])
        session.add(name_base)
    try:
        session.commit()
    except Exception:

        session.rollback()
    return
