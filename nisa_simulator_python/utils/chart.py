from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json

# todo: create_header()を作る
# todo: portofolio のデータを格納するdataclassを作成して、ICalculateMethod.calculateの戻り値をそのdataclassにする


@dataclass
@dataclass_json
class Header:
    """portfolio 表示の際のヘッダーオブジェクト
    """
    text: str
    value: str
    align: str = None
    sortable: str = "true"


@dataclass
@dataclass_json
class Headers:
    """Header をまとめる用のデータクラス
    """
    headers: List[Header]


def create_header() -> Headers:
    """Headers を作成する。

    Returns:
        Headers: 作成されたheader
    """

    return Headers(headers=[])
