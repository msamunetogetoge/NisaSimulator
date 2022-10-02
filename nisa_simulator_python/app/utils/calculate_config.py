class CalculateConfig():
    """計算に使う設定クラス
    """
    # method <-> 名前対応辞書 key = index, value= name
    methods = [
        {
            "method_name": "EfficientReturn", "informations": {"index": 0, "name": "分散最小化(リターン制約あり)"}
        },
        {
            "method_name": "MinVolatility", "informations": {"index": 1, "name": "分散最小化"}
        },
        {
            "method_name": "MaxSharpe", "informations": {"index": 2, "name": "シャープ・レシオ最大化"}
        },
    ]
