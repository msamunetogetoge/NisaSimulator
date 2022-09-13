from abc import ABCMeta, abstractclassmethod
from pandas import DataFrame
from typing import OrderedDict

from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

from calculate_config import CalculateConfig


class ICalculateMethod(metaclass=ABCMeta):
    """ポートフォリオを計算するメソッドのインターフェイス。

    Args:
        metaclass (_type_, optional): _description_. Defaults to ABCMeta.
    """
    @abstractclassmethod
    def calculate(self, data: DataFrame) -> OrderedDict:
        """
            pypfopt.efficient_frontier.EfficientFrontier のmethodを使用して計算する。
        Args:
            data (DataFrame, optional): dbから取得したデータをpandas.DataFrameに格納して渡す。 Defaults to None.

        Returns:
            OrderedDict: {sp500: 20000, topix: 13333}のようなデータ
        """
        pass

    @abstractclassmethod
    def get_name(self) -> str:
        """該当methodの名前を返す

        Returns:
            str: 分散最小化,など
        """
        pass

    @abstractclassmethod
    def get_index(self) -> int:
        """method に割り振ったindexを返す

        Returns:
            int: 0,1,2...など
        """
        pass


efficient_return = next(
    method for method in CalculateConfig.methods if method["method_name"] == "EfficientReturn").informations
min_volatility = next(
    method for method in CalculateConfig.methods if method["method_name"] == "MinVolatility").informations
max_sharpe = next(
    method for method in CalculateConfig.methods if method["method_name"] == "MaxSharpe").informations


class EfficientReturn(ICalculateMethod):
    """分散最小化(リターン制約あり)でポートフォリオを計算するクラス

    Args:
        ICalculateMethod (_type_): _description_
    """

    def __init__(self, data: DataFrame, name: str = efficient_return.name, index: int = efficient_return.index, target_return: float = 0.1) -> None:
        """初期化時、データから平均や分散を計算する。

        Args:
            data (DataFrame): 計算に使用するデータ
            name (str, optional): method名 Defaults to "分散最小化(リターン制約あり)".
            index (int, optional): methodのindex Defaults to 0.
            target_return (float, optional): リターン制約 Defaults to 0.1.
        """
        self._name = name
        self._index = index
        self._target_return = target_return
        self.data = data
        self.mean = expected_returns.mean_historical_return(self.data)
        self.cov = risk_models.sample_cov(self.data)

    def get_name(self) -> str:
        """method名を返す

        Returns:
            str: method名
        """
        return self._name

    def get_index(self) -> int:
        """method に割り振ったindexを返す

        Returns:
            int:index
        """
        return self._index

    def calculate(self, data: DataFrame = None) -> OrderedDict:
        """
            pypfopt.efficient_frontier.EfficientFrontier.efficient_returnで計算する
        Args:
            data (DataFrame, optional): 必要なら再設定する。 Defaults to None.

        Returns:
            OrderedDict: {sp500: 20000, topix: 13333}のようなデータ
        """
        if data != None:
            self.mean = expected_returns.mean_historical_return(data)
            self.cov = risk_models.sample_cov(data)
        ef = EfficientFrontier(self.mean, self.cov)
        return ef.efficient_return(target_return=self._target_return)


class MinVolatility(ICalculateMethod):
    """分散最小化でポートフォリオを計算するクラス

    Args:
        ICalculateMethod (_type_): _description_
    """

    def __init__(self, data: DataFrame, name: str = min_volatility.name, index: int = min_volatility.index) -> None:
        """初期化時、データから平均や分散を計算する。

        Args:
            data (DataFrame): 計算に使用するデータ
            name (str, optional): method名 Defaults to "分散最小化".
            index (int, optional): methodのindex Defaults to 1.
        """
        self._name = name
        self._index = index
        self.data = data
        self.mean = expected_returns.mean_historical_return(self.data)
        self.cov = risk_models.sample_cov(self.data)

    def get_name(self) -> str:
        """method名を返す

        Returns:
            str: method名
        """
        return self._name

    def get_index(self) -> int:
        """method に割り振ったindexを返す

        Returns:
            int:index
        """
        return self._index

    def calculate(self, data: DataFrame = None) -> OrderedDict:
        """
            pypfopt.efficient_frontier.EfficientFrontier.efficient_returnで計算する
        Args:
            data (DataFrame, optional): 必要なら再設定する。 Defaults to None.

        Returns:
            OrderedDict: {sp500: 20000, topix: 13333}のようなデータ
        """
        if data != None:
            self.mean = expected_returns.mean_historical_return(data)
            self.cov = risk_models.sample_cov(data)
        ef = EfficientFrontier(self.mean, self.cov)
        return ef.min_volatility()


class MaxSharpe(ICalculateMethod):
    """シャープ・レシオ最大化でポートフォリオを計算するクラス

    Args:
        ICalculateMethod (_type_): _description_
    """

    def __init__(self, data: DataFrame, name: str = max_sharpe.name, index: int = max_sharpe.index, risk_free_rate: float = 0.02) -> None:
        """初期化時、データから平均や分散を計算する。

        Args:
            data (DataFrame): 計算に使用するデータ
            name (str, optional): method名 Defaults to "分散最小化".
            index (int, optional): methodのindex Defaults to 1.
            risk_free_rate (float, optional):risk-free rate of borrowing/lending  Defaults to 0.02.
        """
        self._name = name
        self._index = index
        self._risk_free_rate = risk_free_rate
        self.data = data
        self.mean = expected_returns.mean_historical_return(self.data)
        self.cov = risk_models.sample_cov(self.data)

    def get_name(self) -> str:
        """method名を返す

        Returns:
            str: method名
        """
        return self._name

    def get_index(self) -> int:
        """method に割り振ったindexを返す

        Returns:
            int:index
        """
        return self._index

    def calculate(self, data: DataFrame = None) -> OrderedDict:
        """
            pypfopt.efficient_frontier.EfficientFrontier.efficient_returnで計算する
        Args:
            data (DataFrame, optional): 必要なら再設定する。 Defaults to None.

        Returns:
            OrderedDict: {sp500: 20000, topix: 13333}のようなデータ
        """
        if data != None:
            self.mean = expected_returns.mean_historical_return(data)
            self.cov = risk_models.sample_cov(data)
        ef = EfficientFrontier(self.mean, self.cov)
        return ef.max_sharpe(risk_free_rate=0.02)
