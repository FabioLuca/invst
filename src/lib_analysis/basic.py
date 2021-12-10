import pandas as pd
pd.options.mode.chained_assignment = None


class Basic:

    def calc_difference(self,
                        minuend_column: str,
                        subtrahend_column: str,
                        result_column: str = "",
                        result_dataframe: pd.DataFrame = None):
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

                #. `result_column`: Result of the difference operation.

        """
        if result_column == "":
            result_column = f"{minuend_column} minus {subtrahend_column}"

        if result_dataframe is None:
            self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[minuend_column] - \
                self.ohlc_dataset[subtrahend_column]
        else:
            result_dataframe.loc[:, result_column] = self.ohlc_dataset[minuend_column] - \
                self.ohlc_dataset[subtrahend_column]

    def calc_scalar_multiplication(self,
                                   factor1_column: str,
                                   factor2: float,
                                   result_column: str = "",
                                   result_dataframe: pd.DataFrame = None):
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

                #. `result_column`: Result of the scalar multiplication
                   operation.

        """
        if result_column == "":
            result_column = f"{factor1_column} multiplied by {factor2}"

        if result_dataframe is None:
            self.ohlc_dataset.loc[:,
                                  result_column] = self.ohlc_dataset[factor1_column] * factor2
        else:
            result_dataframe.loc[:,
                                 result_column] = self.ohlc_dataset[factor1_column] * factor2

    def calc_multiplication(self,
                            factor1_column: str,
                            factor2_column: str,
                            result_column: str = "",
                            result_dataframe: pd.DataFrame = None):
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

        if result_dataframe is None:
            self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[factor1_column] * \
                self.ohlc_dataset[factor2_column]
        else:
            result_dataframe.loc[:, result_column] = self.ohlc_dataset[factor1_column] * \
                self.ohlc_dataset[factor2_column]

    def calc_division(self,
                      dividend_column: str,
                      divisor_column: str,
                      result_column: str = "",
                      result_dataframe: pd.DataFrame = None):
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

        if result_dataframe is None:
            self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[dividend_column] / \
                self.ohlc_dataset[divisor_column]
        else:
            result_dataframe.loc[:, result_column] = self.ohlc_dataset[dividend_column] / \
                self.ohlc_dataset[divisor_column]

    def calc_delta(self):
        """Calculate de delta value between the Close (Final) and the Open value
        for the ticker. It will add a column called "Delta" to the Pandas
        dataframe.

        Parameters
        ----------
            None
                The input for the calculation is based on the Pandas dataframe
                data which is already available. The expected column for
                this operation is:

                #. `Open`
                #. `Close Final`

        Returns
        -------
            None
                The outcome from the calculation is not explicitly returned, but
                added to the Pandas dataframe as new columns. The new columns
                are:

                #. `Delta`: Result of the difference between `Close Final` and
                   `Open` values for every sample.

        """
        self.ohlc_dataset.loc[:, "Delta"] = self.calculate_difference(
            minuend_column="Open", subtrahend_column="Close Final", result_column="Delta")

    def calc_absolute(self,
                      source_column: str,
                      result_column: str = "",
                      result_dataframe: pd.DataFrame = None):
        """Calculate de delta value between the Close (Final) and the Open value
        for the ticker. It will add a column called "Delta" to the Pandas
        dataframe.

        Parameters
        ----------
            none

        """
        self.ohlc_dataset.loc[:,
                              result_column] = self.ohlc_dataset[source_column].abs()

    def calc_change(self,
                    source_column: str,
                    shift: int,
                    result_column: str = "",
                    result_dataframe: pd.DataFrame = None):
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

        if result_dataframe is None:
            self.ohlc_dataset.loc[:,
                                  result_column] = self.ohlc_dataset[source_column].diff(shift)
        else:
            result_dataframe.loc[:,
                                 result_column] = self.ohlc_dataset[source_column].diff(shift)

    def calc_threshold(self,
                       source_column: str,
                       threshold: float,
                       comparison: str,
                       replace_value: float,
                       result_column: str = "",
                       result_dataframe: pd.DataFrame = None):
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

        if result_dataframe is None:
            if comparison == "==":
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] == threshold, replace_value)
            elif comparison == ">":
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] > threshold, replace_value)
            elif comparison == "<":
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] < threshold, replace_value)
            elif comparison == ">=":
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] >= threshold, replace_value)
            elif comparison == "<=":
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] <= threshold, replace_value)
        else:
            if comparison == "==":
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] == threshold, replace_value)
            elif comparison == ">":
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] > threshold, replace_value)
            elif comparison == "<":
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] < threshold, replace_value)
            elif comparison == ">=":
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] >= threshold, replace_value)
            elif comparison == "<=":
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].mask(
                    self.ohlc_dataset[source_column] <= threshold, replace_value)

    def calc_SMA(self,
                 source_column: str,
                 length: int,
                 minimum_length: int = None,
                 result_column: str = "",
                 result_dataframe: pd.DataFrame = None):
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

            if result_dataframe is None:
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).mean()
            else:
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).mean()

        else:

            if result_dataframe is None:
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length, min_periods=minimum_length).mean()
            else:
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length, min_periods=minimum_length).mean()

    def calc_MovingStdDev(self,
                          source_column: str,
                          length: int,
                          minimum_length: int = None,
                          result_column: str = "",
                          result_dataframe: pd.DataFrame = None):
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

            if result_dataframe is None:
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).std()
            else:
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).std()

        else:

            if result_dataframe is None:
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length, min_periods=minimum_length).std()
            else:
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length, min_periods=minimum_length).std()

    def calc_EMA(self, source_column: str, length: int, result_column: str = "", result_dataframe: pd.DataFrame = None):
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

        if result_dataframe is None:
            self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].ewm(
                span=length, min_periods=0, adjust=False, ignore_na=False).mean()
        else:
            result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].ewm(
                span=length, min_periods=0, adjust=False, ignore_na=False).mean()

    def calc_integration(self, source_column: str, length: int = 0, result_column: str = "", result_dataframe: pd.DataFrame = None):
        """Calculate the integration for the specified column for a window in a
        Pandas dataframe. For length equals 0, the complete series is used. 
        Depending on the parameters, the result will be a new column on the
        same dataframe.
        """
        if result_column == "":
            result_column = f"Integration {length} {source_column}"

        if result_dataframe is None:
            if length == 0:
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling.sum(
                )
            else:
                self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).sum()
        else:
            if length == 0:
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling.sum(
                )
            else:
                result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).sum()

            result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].ewm(
                span=length, min_periods=0, adjust=False, ignore_na=False).mean()

    def calc_minimum(self, source_column: str, length: int, result_column: str = "", result_dataframe: pd.DataFrame = None):
        """Calculate the rolling minimum.
        """
        if result_column == "":
            result_column = f"Minimum {length} {source_column}"

        if result_dataframe is None:
            self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).min()
        else:
            result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).min()

    def calc_maximum(self, source_column: str, length: int, result_column: str = "", result_dataframe: pd.DataFrame = None):
        """Calculate the rolling maximum.
        """
        if result_column == "":
            result_column = f"Maximum {length} {source_column}"

        if result_dataframe is None:
            self.ohlc_dataset.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).max()
        else:
            result_dataframe.loc[:, result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).max()

    def convert_numpy(self, source_column: str):

        numpy_data = self.ohlc_dataset[source_column].to_numpy()

        return numpy_data

    def split_data(self, numpy_data, percetage_learning: float):

        length = numpy_data.size

        cut_learning = int(round(length * percetage_learning))
        cut_test = length - cut_learning

        train_data = numpy_data[:cut_learning]
        test_data = numpy_data[-cut_test:]

        return train_data, test_data
