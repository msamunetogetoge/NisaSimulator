import pandas as pd
from db.Model import GraphBase, NameBase, CalculateResult

from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns
from pypfopt import risk_models

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def scalling(X: pd.Series) -> pd.Series:
    return (X - X.mean()) / X.mean()


def get_series_from_db(col_name: str) -> pd.Series:
    """[summary]与えられた名前のデータから、pd.Seriesを作る

    Args:
        col_name (str): [description] 欲しいデータの名前( NameBase.name )

    Returns:
        pd.Series: [description] index: GraphBase.date, name: GraphBase.name, value GraphBase.close
    """
    col_date = GraphBase.query.with_entities(
        GraphBase.date).filter_by(name=col_name).all()
    col_date = [d[0] for d in col_date]
    col_close = GraphBase.query.with_entities(
        GraphBase.close).filter_by(name=col_name).all()
    col_close = [c[0] for c in col_close]
    data = pd.Series(index=col_date, data=col_close, name=col_name)
    return data


def get_datas_from_db() -> pd.DataFrame:
    """[summary] dbからデータを読み込む

    Returns:
        [type]pd.DataFrame: [description]
    """
    df = pd.Series()
    col_names = NameBase.query.with_entities(NameBase.name).all()
    for i, col in enumerate(col_names):
        col_name = col[0]
        if i == 0:
            base = pd.DataFrame(get_series_from_db(col_name=col_name))
        else:
            s = get_series_from_db(col_name=col_name)
            df = base.join(s)
            base = df
    return df


def get_result_from_db() -> list(dict()):
    """[summary] dbのCalculateResultからデータを取得し、整形する

    Returns:
        [type]list(dict) d: [description]d[0]:string"yyyy/mm/dd/",d[1]:string"name" d[2]:float calculateresultpercent, d[3]: int calculateresultint
    """
    result_list = list(dict())
    names = NameBase.query.with_entities(
        NameBase.name, NameBase.searchkeyword).all()
    for n in names:
        try:
            result = CalculateResult.query.filter(
                CalculateResult.name == n[0]).order_by(CalculateResult.date.desc()).first()
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
        except BaseException:
            # logger.error(f"{n[1]} がありません。")
            pass
    result_list.sort(key=lambda x: x["resultint"], reverse=True)
    return result_list


def make_graph(scale=True):
    """[summary]dbからデータを読み込んでhtmlで表示する為のグラフを描く

    Args:
        minimax (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    df = get_datas_from_db()
    cols = list(df.columns)
    if(scale is True):
        for col in cols:
            df[col] = scalling(df[col])

    fig = make_subplots()
    for col in cols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col))
    plot_fig = fig.to_html(include_plotlyjs=False)
    return plot_fig


def calculate_portfolio(df, method=0) -> dict:
    """[summary]
    Args:
        df ([pandas.DataFrame]): [description]
    Returns:
        [OrderedDict]: [description]
    """
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    ef = EfficientFrontier(mu, S)
    # method の値によって使うやつを変える
    try:
        if method == 0:
            buy = ef.efficient_return(target_return=0.1)
        elif method == 1:
            buy = ef.min_volatility()
        elif method == 2:
            buy = ef.max_sharpe(risk_free_rate=0.02)
        else:
            buy = ef.efficient_return(target_return=0.1)
    except Exception:
        b = {"error": (0, 0, "Error")}
        return b

    b = dict()
    for k in buy.keys():
        sbi = NameBase.query.with_entities(
            NameBase.searchkeyword).filter(
            NameBase.name == k).first()
        b[k] = (buy[k], int(33333 * buy[k]), sbi[0])
    return b
