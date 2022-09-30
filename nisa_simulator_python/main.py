# from types import MethodDescriptorType
# from flask import Flask, json, jsonify, request
# from flask import render_template
# from utils.get_finance import get_datas_from_db, make_graph, calculate_portfolio, get_result_from_db
# from flask_sqlalchemy import SQLAlchemy
# import pandas as pd
# import datetime
# import db.Model as Model

# from config import BaseConfig


# app = Flask(__name__)
# app.config.from_object('config.BaseConfig')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/nisa.db"
# db = SQLAlchemy(app)

# def RegisterResult(method=0):
#     """[summary] 本日分の計算結果をdbに登録する。
#     """
#     df = get_datas_from_db()
#     buy = calculate_portfolio(df, method)
#     d = datetime.date.today()
#     try:
#         # 各indexの計算値(既に存在しない時のみ)をdbに登録する
#         for index in buy.keys():
#             if(Model.CalculateResult.query.filter_by(date=d, name=index).first() is None):
#                 r = Model.CalculateResult(
#                     date=d,
#                     name=index,
#                     method_name= method,
#                     resultpercent=int(buy[index][0] * 100),
#                     resultint=buy[index][1])
#                 Model.db.session.add(r)
#         Model.db.session.commit()
#     except Exception as e:
#         print(f"RegisterResult:db commit に失敗しました。{e}")
#         Model.db.session.rollback()
#     return


# @app.route("/")
# async def index():
#     return render_template("index.html")


# @app.route("/data_update", methods=["POST"])
# def initapp():
#     """[summary] dbに値が入っていれば更新、無ければデータ作成
#     """
#     try:
#         Model.db.create_all()
#         #NameBaseを作る
#         if(Model.NameBase.query.count() == 0):
#             print("CreateNameBase")
#             Model.CreateNameBase()
#         #GraphDataを作る
#         if(Model.GraphData.query.count() == 0):
#             Model.CreateGraphData()
#             print("CreateGraphData")
#         else:
#             print("UpdateGraphData")
#             Model.UpdateGraphData()
#         #CalculateResultを作る
#         for k in BaseConfig.method_dict.keys():
#             RegisterResult(method=k)

#     except Exception as e:
#         print(f"initapp false : {e}")
#         return jsonify(False)
#     return jsonify(True)


# @app.route("/need_init", methods=["POST"])
# def need_init():
#     """[summary] GraphDataのデータが最新どうかで、初期化が必要か調べる(更新日が今日か？ and spread sheet でデータを取得してみて最後のデータの日付と、dbのデータの日付が一致するか調べる)
#     Returns:
#         [type]bool: [description] true=>need init, false not need init
#     """
#     try:
#         # 更新日が今日ならnot need init
#         from_time = Model.GraphData.query.with_entities(
#             Model.GraphData.date).order_by(Model.GraphData.updatetime.desc()).first()[0]

#         if(from_time.date() == datetime.date.today()):
#             return jsonify(False)
#         # db の最後のデータの日付を取得
#         from_time = Model.GraphData.query.with_entities(
#             Model.GraphData.date).order_by(Model.GraphData.date.desc()).first()[0]
#         from_time = from_time.date()

#         # 更新しようとする日が土日で、かつ最終データの日付と更新しようとする日の剥離が3日以内なら更新しない
#         # (金曜日にデータを取っていて、その週の日曜日にデータを更新しようとしてもしない)
#         end_time = datetime.date.today()
#         time_delt = end_time - from_time
#         if(end_time.weekday() in [5, 6] and time_delt.days < 3):
#             return jsonify(False)
#     except Exception:
#         # エラーが出るのに何度も更新されたくないので、エラーが出たらデータ更新不要にする
#         print(Exception)
#         return jsonify(False)
#     return jsonify(True)


# @app.route("/plot")
# def plot():
#     g = make_graph()

#     return render_template(
#         'plot.html', graph=g)

# @app.route("/ranking")
# def get_ranking():
#     # dbからデータを読み込むだけにする
#     buy = get_result_from_db()
#     s = sum([p["resultint"] for p in buy])
#     today = buy[0]["date"]
#     return render_template(
#         'ranking.html',today = today, amount=s, method = BaseConfig.method_dict[buy[0]["method_name"]], methods = BaseConfig.method_dict)


# @app.route("/buy_json",methods=["POST"])
# def json_test():
#     try:
#         method = int(request.form["method"])
#     except ValueError:
#         method=0
#     if method in  list(BaseConfig.method_dict.keys()):
#         buy = get_result_from_db(method=method)
#     else:
#         buy = get_result_from_db()
#     return jsonify(buy)

# if __name__ == "__main__":
#     app.run(host='127.0.0.1', port=8080, debug=True)


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
