class CalculateConfig():
    """計算に使う設定クラス
    """
    # method <-> 名前対応辞書 key = index, value= name
    methods = [
        {
            "method_name": "EfficientReturn", "infomations": {"index": 0, "name": "分散最小化(リターン制約あり)"}
        },
        {
            "method_name": "MinVolatility", "infomations": {"index": 1, "name": "分散最小化"}
        },
        {
            "method_name": "MaxSharpe", "infomations": {"index": 2, "name": "シャープ・レシオ最大化"}
        },
    ]
