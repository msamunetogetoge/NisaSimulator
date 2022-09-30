from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Header:
    """portfolio 表示の際のヘッダーオブジェクト
    """
    text: str
    value: str
    align: str = None
    sortable: str = "true"


@dataclass_json
@dataclass
class Headers:
    """Header をまとめる用のデータクラス
    """
    headers: List[Header]


def create_header() -> List[Headers]:
    """Headers を作成する。

    Returns:
        Headers: 作成されたheader
    """
    index = Header(
        text="銘柄",
        value="index_name",
        align="start",
        sortable="false"
    )
    purchane_percent = Header(
        text="購入割合",
        value="percent",
    )
    purchane = Header(
        text="購入額",
        value="yen"
    )
    search = Header(
        text="検索パラメータ",
        value="search_param"
    )

    return Headers([index, purchane_percent, purchane, search
                    ])
