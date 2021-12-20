import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None


class Basic:

    def calc_difference(self,
                        dataframe: pd.DataFrame,
                        minuend_column: str,
                        subtrahend_column: str,
                        result_column: str = "",
                        value_prediction=np.nan):
        """Calculate the difference between 2 columns from a Pandas Dataframe.

        Parameters
        ----------
            minuend_column: string
                Name of the column in the Pandas Dataframe to be used as the
                minuend of the differentiation operation.
            subtrahend_column: string
                Name of the column in the Pandas Dataframe to be used as the
                subtrahend of the differentiation operation.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `minuend_column
                minus subtrahend_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        Returns
        -------
            None
                The outcome from the calculation is not explicitly returned, but
                added to the Pandas dataframe as new columns. The new columns
                are:

                1. `result_column`: Result of the difference operation.

        """
        if result_column == "":
            result_column = f"{minuend_column} minus {subtrahend_column}"

        dataframe.loc[:, result_column] = dataframe[minuend_column] - \
            dataframe[subtrahend_column]

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_scalar_multiplication(self,
                                   dataframe: pd.DataFrame,
                                   factor1_column: str,
                                   factor2: float,
                                   result_column: str = "",
                                   value_prediction=np.nan):
        """Calculate the multiplication between a column from a Pandas Dataframe
        and a number.

        Parameters
        ----------
            factor1_column: string
                Name of the column in the Pandas Dataframe to be used as the
                dividend of the division operation.
            factor2_column: float
                Value of the factor.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `minuend_column
                minus subtrahend_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        Returns
        -------
            None
                The outcome from the calculation is not explicitly returned, but
                added to the Pandas dataframe as new columns. The new columns
                are:

                1. `result_column`: Result of the scalar multiplication
                   operation.

        """
        if result_column == "":
            result_column = f"{factor1_column} multiplied by {factor2}"

        dataframe.loc[:, result_column] = dataframe[factor1_column] * factor2

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_multiplication(self,
                            dataframe: pd.DataFrame,
                            factor1_column: str,
                            factor2_column: str,
                            result_column: str = "",
                            value_prediction=np.nan):
        """Calculate the division between 2 columns from a Pandas Dataframe.

        Parameters
        ----------
            factor1_column: string
                Name of the column in the Pandas Dataframe to be used as the
                dividend of the division operation.
            factor2_column: string
                Name of the column in the Pandas Dataframe to be used as the
                divisor of the division operation.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `minuend_column
                minus subtrahend_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"{factor1_column} multiplied by {factor2_column}"

        dataframe.loc[:, result_column] = dataframe[factor1_column] * \
            dataframe[factor2_column]

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_division(self,
                      dataframe: pd.DataFrame,
                      dividend_column: str,
                      divisor_column: str,
                      result_column: str = "",
                      value_prediction=np.nan):
        """Calculate the division between 2 columns from a Pandas Dataframe.

        Parameters
        ----------
            dividend_column: string
                Name of the column in the Pandas Dataframe to be used as the
                dividend of the division operation.
            divisor_column: string
                Name of the column in the Pandas Dataframe to be used as the
                divisor of the division operation.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `minuend_column
                minus subtrahend_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"{dividend_column} divided by {divisor_column}"

        dataframe.loc[:, result_column] = dataframe[dividend_column] / \
            dataframe[divisor_column]
        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_delta(self,
                   dataframe: pd.DataFrame,
                   value_prediction=np.nan):
        """Calculate de delta value between the Close (Final) and the Open value
        for the ticker. It will add a column called "Delta" to the Pandas
        dataframe.

        Parameters
        ----------
            None
                The input for the calculation is based on the Pandas dataframe
                data which is already available. The expected column for
                this operation is:

                1. `Open`
                2. `Close Final`

        Returns
        -------
            None
                The outcome from the calculation is not explicitly returned, but
                added to the Pandas dataframe as new columns. The new columns
                are:

                1. `Delta`: Result of the difference between `Close Final` and
                   `Open` values for every sample.

        """
        dataframe.loc[:, "Delta"] = self.calculate_difference(
            minuend_column="Open", subtrahend_column="Close Final", result_column="Delta")

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", "Delta"] = value_prediction

    def calc_absolute(self,
                      dataframe: pd.DataFrame,
                      source_column: str,
                      result_column: str = "",
                      value_prediction=np.nan):
        """Calculate de delta value between the Close (Final) and the Open value
        for the ticker. It will add a column called "Delta" to the Pandas
        dataframe.

        Parameters
        ----------
            none

        """
        dataframe.loc[:, result_column] = dataframe[source_column].abs()
        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_change(self,
                    dataframe: pd.DataFrame,
                    source_column: str,
                    shift: int,
                    result_column: str = "",
                    value_prediction=np.nan):
        """Calculate the difference between entries from a column. For example
        the closing price difference for every day.

        Parameters
        ----------
            source_column: string
                Name of the column in the Pandas Dataframe to be used for the
                calculation of the change.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `SMA length
                source_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"Change {source_column}"

        dataframe.loc[:, result_column] = dataframe[source_column].diff(shift)

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_threshold(self,
                       dataframe: pd.DataFrame,
                       source_column: str,
                       threshold: float,
                       comparison: str,
                       replace_value: float,
                       result_column: str = "",
                       value_prediction=np.nan):
        """Replaces values below or above a threshold, replacing them by a new
        one.

        Parameters
        ----------
            source_column: string
                Name of the column in the Pandas Dataframe to be used for the
                calculation of the change.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `SMA length
                source_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"Replacement {source_column} {comparison} {threshold}"

        if comparison == "==":
            dataframe.loc[:, result_column] = dataframe[source_column].mask(
                dataframe[source_column] == threshold, replace_value)
        elif comparison == ">":
            dataframe.loc[:, result_column] = dataframe[source_column].mask(
                dataframe[source_column] > threshold, replace_value)
        elif comparison == "<":
            dataframe.loc[:, result_column] = dataframe[source_column].mask(
                dataframe[source_column] < threshold, replace_value)
        elif comparison == ">=":
            dataframe.loc[:, result_column] = dataframe[source_column].mask(
                dataframe[source_column] >= threshold, replace_value)
        elif comparison == "<=":
            dataframe.loc[:, result_column] = dataframe[source_column].mask(
                dataframe[source_column] <= threshold, replace_value)

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_SMA(self,
                 dataframe: pd.DataFrame,
                 source_column: str,
                 length: int,
                 minimum_length: int = None,
                 result_column: str = "",
                 value_prediction=np.nan):
        """Calculate the simple moving average (SMA) for the specified column
        and length in a Pandas dataframe. Depending on the parameters, the
        result will be a new column on the same dataframe.

        Parameters
        ----------
            source_column: string
                Name of the column in the Pandas Dataframe to be used for the
                calculation of the moving average.
            length: int
                Number of samples to be used as rolling window for the average
                calculation.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `SMA length
                source_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"SMA {length} {source_column}"

        if minimum_length is None:
            dataframe.loc[:, result_column] = dataframe[source_column].rolling(
                window=length).mean()
        else:
            dataframe.loc[:, result_column] = dataframe[source_column].rolling(
                window=length, min_periods=minimum_length).mean()

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_MovingStdDev(self,
                          dataframe: pd.DataFrame,
                          source_column: str,
                          length: int,
                          minimum_length: int = None,
                          result_column: str = "",
                          value_prediction=np.nan):
        """Calculate the simple moving standard deviation for the specified
        column and length in a Pandas dataframe. Depending on the parameters,
        the result will be a new column on the same dataframe.

        Parameters
        ----------
            source_column: string
                Name of the column in the Pandas Dataframe to be used for the
                calculation of the moving average.
            length: int
                Number of samples to be used as rolling window for the average
                calculation.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `SMA length
                source_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"Moving StdDev {length} {source_column}"

        if minimum_length is None:
            dataframe.loc[:, result_column] = dataframe[source_column].rolling(
                window=length).std()
        else:
            dataframe.loc[:, result_column] = dataframe[source_column].rolling(
                window=length, min_periods=minimum_length).std()

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_EMA(self,
                 dataframe: pd.DataFrame,
                 source_column: str,
                 length: int,
                 result_column: str = "",
                 value_prediction=np.nan):
        """Calculate the exponential moving average (EMA) for the specified
        column and length in a Pandas dataframe. Depending on the parameters,
        the result will be a new column on the same dataframe.

        Parameters
        ----------
            source_column: string
                Name of the column in the Pandas Dataframe to be used for the
                calculation of the moving average.
            length: int
                Number of samples to be used as rolling window for the average
                calculation.
            result_column: string, optional
                Name of the column in the Pandas Dataframe to be used as the
                result of the operation. If no information is
                passed, then the name will be in the format: `EMA length
                source_column`.
            result_dataframe: Pandas Dataframe, optional
                If passed, the result of the operation will be stored in the new
                dataframe, otherwise, the original dataframe is used.

        """
        if result_column == "":
            result_column = f"EMA {length} {source_column}"

        dataframe.loc[:, result_column] = dataframe[source_column].ewm(
            span=length, min_periods=0, adjust=False, ignore_na=False).mean()

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_integration(self,
                         dataframe: pd.DataFrame,
                         source_column: str,
                         length: int = 0,
                         result_column: str = "",
                         value_prediction=np.nan):
        """Calculate the integration for the specified column for a window in a
        Pandas dataframe. For length equals 0, the complete series is used.
        Depending on the parameters, the result will be a new column on the
        same dataframe.
        """
        if result_column == "":
            result_column = f"Integration {length} {source_column}"

        if length == 0:
            dataframe.loc[:, result_column] = dataframe[source_column].rolling.sum(
            )
        else:
            dataframe.loc[:, result_column] = dataframe[source_column].rolling(
                window=length).sum()
        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

            # result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].ewm(
            #     span=length, min_periods=0, adjust=False, ignore_na=False).mean()

    def calc_minimum(self,
                     dataframe: pd.DataFrame,
                     source_column: str,
                     length: int,
                     result_column: str = "",
                     value_prediction=np.nan):
        """Calculate the rolling minimum.
        """
        if result_column == "":
            result_column = f"Minimum {length} {source_column}"

        dataframe.loc[:, result_column] = dataframe[source_column].rolling(
            window=length).min()
        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def calc_maximum(self,
                     dataframe: pd.DataFrame,
                     source_column: str,
                     length: int,
                     result_column: str = "",
                     value_prediction=np.nan):
        """Calculate the rolling maximum.
        """
        if result_column == "":
            result_column = f"Maximum {length} {source_column}"

        dataframe.loc[:, result_column] = self.ohlc_datadataframe[source_column].rolling(
            window=length).max()

        if value_prediction is not None:
            dataframe.loc[dataframe['Data Type']
                          == "Prediction data", result_column] = value_prediction

    def convert_numpy(self,
                      dataframe: pd.DataFrame,
                      source_column: str):

        numpy_data = dataframe[dataframe['Data Type']
                                       == "Real data"][source_column].to_numpy()

        return numpy_data

    def split_data(self, data, percetage_learning: float = -1, sequence_length: int = 0):

        length = data.size

        if 0 <= percetage_learning <= 1:
            cut_learning = int(round(length * percetage_learning))
            cut_test = length - cut_learning
        elif int(percetage_learning) == -1 and sequence_length > 0:
            cut_learning = int(length - sequence_length)
            cut_test = length - cut_learning
        else:
            cut_learning = length
            cut_test = 0

        if isinstance(data, np.ndarray):
            train_data = data[: cut_learning]
            test_data = data[-cut_test:]
        elif isinstance(data, pd.DataFrame):
            train_data = data.iloc[: cut_learning].values
            test_data = data.iloc[-cut_test:].values

        # if percetage_learning == 0:
        #     train_data = None
        #     test_data = data
        # else:
        #     train_data = data
        #     test_data = None

        return train_data, test_data
