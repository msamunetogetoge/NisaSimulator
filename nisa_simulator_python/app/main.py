from datetime import datetime
import json
from http import HTTPStatus
from typing import List

from fastapi import FastAPI


from db.db_config import DBConfig
from db.Model import _GraphData
from utils.calculate_methods import ICalculateMethod, convert_method_names, get_calculate_methods, get_method, get_method_names
from utils.chart import create_header
from utils.get_finance import calculate_portfolio, make_chart_data, make_graph, get_datas_from_db
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/graph/")
async def get_graph(start_time: str = None, end_time: str = None):
    """ vue-chartjs でグラフを描くためのjsonを返す
        {Labels:["2021-09-15", ...], datasets:[
            {"label": "nikkei", "data":[123.124, Nan, 100.11, ...]},
            ...
        ]}
    """
    if start_time is None or end_time is None:
        db_config = DBConfig()
        db_config.cls_update_now_start_time(now=datetime.now())
        chart = make_chart_data()
        return chart.to_json()
    else:
        # todo: make_graphで、グラフ描画の範囲を指定できるようにする
        chart = make_chart_data()
        return chart.to_json()


@app.post("/update")
async def update_date() -> HTTPStatus:
    """データのアップデートをする。成功ならOk, 失敗ならInternalServerError

    Returns:
        HTTPStatus: hhtpステータスコード
    """
    db_config = DBConfig()
    graph = _GraphData(db_config=db_config)
    try:
        graph.update()
        return HTTPStatus.OK
    except:
        return HTTPStatus.INTERNAL_SERVER_ERROR


@app.get("/methods")
async def calculate_methods() -> List[str]:
    """ 分散最小化(リターン制約あり) など、計算手法の名前のリストを返す

    Returns:
        List[str]: 計算方法名のリスト
    """
    names = get_method_names()
    return names


@app.get("/portfolio/{name}")
async def get_portfolio(name: str) -> json or HTTPStatus:
    """ポートフォリオを計算して、jsonを返す

    Args:
        method_name (str): 計算方法

    Returns:
        str or HTTPStatus: 計算に成功したらjson, 失敗か、変な計算方法名が来たらBadRequest
    """
    try:
        method_name = convert_method_names(name=name)
        method: ICalculateMethod = get_method(method_name=method_name)
        data = get_datas_from_db()
        buy_list = calculate_portfolio(method(data=data))
        buy_list_json = buy_list.to_json(ensure_ascii=False)
        return buy_list_json
    except Exception as e:
        print(e)
        return HTTPStatus.BAD_REQUEST


@app.get("/portfolio_header")
async def get_portfolio_header() -> json:
    """ portfolioを計算した時に表示する図表のヘッダーを返す

    Returns:
        json: {"headers":
                [
                    {"text": "銘柄", "value": "index_name", "align": "start", "sortable": "false"},
                    {"text": "購入割合", "value": "percent", "align": null, "sortable": "true"},
                    {"text": "購入額", "value": "yen", "align": null, "sortable": "true"},
                    {"text": "検索パラメータ", "value": "search_param", "align": null, "sortable": "true"}
                ]
                }
            のようなjson
    """
    headers = create_header()
    headers_json = headers.to_json(ensure_ascii=False)
    return headers_json
