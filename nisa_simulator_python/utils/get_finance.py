import pandas as pd


import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.calculate_methods import ICalculateMethod
from db.Model import GraphData, NameBase, CalculateResult, Session

# todo query_with_entity 等がsqlalchemy でも使えるかチェックする

session = Session()


def scalling(X: pd.Series) -> pd.Series:
    """与えられたpd.Series のデータを正規化(平均を0)にして、値を大体-1 ~ 1の間に収める

    Args:
        X (pd.Series): 数値データ

    Returns:
        pd.Series:平均を調整したデータ
    """
    return (X - X.mean()) / X.mean()


def get_series_from_db(col_name: str) -> pd.Series:
    """[summary]与えられた名前のデータから、pd.Seriesを作る

    Args:
        col_name (str): [description] 欲しいデータの名前( NameBase.name )

    Returns:
        pd.Series: [description] index: GraphData.date, name: GraphData.name, value GraphData.close
    """
    col_date = session.query(
        GraphData.date).filter_by(name=col_name).all()
    col_date = [d[0] for d in col_date]
    col_close = session.query(
        GraphData.close).filter_by(name=col_name).all()
    col_close = [c[0] for c in col_close]
    data = pd.Series(index=col_date, data=col_close, name=col_name)
    return data


def get_datas_from_db() -> pd.DataFrame:
    """[summary] dbからGraphDataを読み込む

    Returns:
        [type]pd.DataFrame: [description]
    """
    df = pd.Series()
    col_names = session.query(NameBase.name).all()
    for i, col in enumerate(col_names):
        col_name = col[0]
        if i == 0:
            base = pd.DataFrame(get_series_from_db(col_name=col_name))
        else:
            s = get_series_from_db(col_name=col_name)
            df = base.join(s)
            base = df
    return df


def get_result_from_db(method=0) -> list(dict()):
    """[summary] dbのCalculateResultからデータを取得し、整形する

    Returns:
        [type]list(dict) d: [description]d[0]:string"yyyy/mm/dd/",d[1]:string"name" d[2]:float calculateresultpercent, d[3]: int calculateresultint
    """
    result_list = list(dict())
    names = session.query(
        NameBase.name, NameBase.searchkeyword).all()
    for n in names:
        try:
            result = session.query(CalculateResult).filter(
                CalculateResult.name == n[0]).filter(CalculateResult.method_name == method).order_by(CalculateResult.date.desc()).first()
            day = result.date
            day_str = day.strftime('%Y/%m/%d')
            result_dict = {
                "date": day_str,
                "name": n[0],
                "method_name": result.method_name,
                "searchkeyword": n[1],
                "resultpercent": result.resultpercent,
                "resultint": result.resultint}
            result_list.append(result_dict)
        except Exception:
            # logger.error(f"{n[1]} がありません。")
            pass
    result_list.sort(key=lambda x: x["resultint"], reverse=True)
    return result_list

# todo: いつからいつまでのグラフを作成するのか選べるようにする。
# min = datetime.now()から1年前, max = now


def make_graph(scale=True) -> str:
    """[summary]dbからデータを読み込んでhtmlで表示する為のグラフを描く

    Args:
        minimax (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    df = get_datas_from_db()
    cols = list(df.columns)
    if (scale is True):
        for col in cols:
            df[col] = scalling(df[col])

    fig = make_subplots()
    for col in cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col))
    plot_fig = fig.to_html(include_plotlyjs='cdn')
    return plot_fig


def calculate_portfolio(method: ICalculateMethod) -> dict or Exception:
    """指定された計算方法でポートフォリオを計算する。また、所定のdict に整形する。

    Args:
        method (ICalculateMethod): _description_

    Returns:
        dict: {"sp500":(0.1,3333,"sp500")}のような形のdict
        Exception: 計算失敗時のエラー
    """
    try:
        buy = method.calculate()
    except Exception as error_of_calculate:
        print(
            f"In {calculate_portfolio.__name__} error occured :{error_of_calculate}")
        raise error_of_calculate

    buy_dict = dict()
    for k in buy.keys():
        sbi = session.query(
            NameBase.searchkeyword).filter(
            NameBase.name == k).first()
        buy_dict[k] = (buy[k], int(33333 * buy[k]), sbi[0])
    return buy_dict
