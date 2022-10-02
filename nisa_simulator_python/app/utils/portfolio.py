from pypfopt import expected_returns
from pypfopt import risk_models
from collections import OrderedDict
from db.Model import NameBase


def calculate_portfolio(df):
    """[summary]
    Args:
        df ([pandas.DataFrame]): [description]
    Returns:
        [OrderedDict]: [description]
    """
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    from pypfopt.efficient_frontier import EfficientFrontier
    ef = EfficientFrontier(mu, S)
    buy = ef.efficient_return(target_return=0.1)
    b = OrderedDict()
    # SBIの検索パラメータも入れる->NameBase.query.entity_with(NameBase.nameDisplay).filter(name=key).first()
    # みたいな感じで
    for k in buy.keys():
        sbi = NameBase.query.entity_with(
            NameBase.nameDisplay).filter(
            name=k).first()
        b[k] = (buy[k], int(33333 * buy[k]), sbi)
    return b
