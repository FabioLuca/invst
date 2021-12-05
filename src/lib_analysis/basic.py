import pandas as pd


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

        """
        if result_column == "":
            result_column = f"{minuend_column} minus {subtrahend_column}"

        if result_dataframe is None:
            self.ohlc_dataset[result_column] = self.ohlc_dataset[minuend_column] - \
                self.ohlc_dataset[subtrahend_column]
        else:
            result_dataframe[result_column] = self.ohlc_dataset[minuend_column] - \
                self.ohlc_dataset[subtrahend_column]

    def calc_delta(self):
        """Calculate de delta value between the Close (Final) and the Open value
        for the ticker. It will add a column called "Delta" to the Pandas
        dataframe.

        Parameters
        ----------
            none

        """
        self.ohlc_dataset["Delta"] = self.calculate_difference(
            minuend_column="Open", subtrahend_column="Close Final", result_column="Delta")

    def calc_SMA(self,
                 source_column: str,
                 length: int,
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

        if result_dataframe is None:
            self.ohlc_dataset[result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).mean()
        else:
            result_dataframe[result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).mean()

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
            self.ohlc_dataset[result_column] = self.ohlc_dataset[source_column].ewm(
                span=length, min_periods=0, adjust=False, ignore_na=False).mean()
        else:
            result_dataframe[result_column] = self.ohlc_dataset[source_column].ewm(
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
                self.ohlc_dataset[result_column] = self.ohlc_dataset[source_column].rolling.sum(
                )
            else:
                self.ohlc_dataset[result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).sum()
        else:
            if length == 0:
                result_dataframe[result_column] = self.ohlc_dataset[source_column].rolling.sum(
                )
            else:
                result_dataframe[result_column] = self.ohlc_dataset[source_column].rolling(
                    window=length).sum()

            result_dataframe[result_column] = self.ohlc_dataset[source_column].ewm(
                span=length, min_periods=0, adjust=False, ignore_na=False).mean()

    def calc_minimum(self, source_column: str, length: int, result_column: str = "", result_dataframe: pd.DataFrame = None):
        """Calculate the rolling minimum.
        """
        if result_column == "":
            result_column = f"Minimum {length} {source_column}"

        if result_dataframe is None:
            self.ohlc_dataset[result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).min()
        else:
            result_dataframe[result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).min()

    def calc_maximum(self, source_column: str, length: int, result_column: str = "", result_dataframe: pd.DataFrame = None):
        """Calculate the rolling maximum.
        """
        if result_column == "":
            result_column = f"Maximum {length} {source_column}"

        if result_dataframe is None:
            self.ohlc_dataset[result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).max()
        else:
            result_dataframe[result_column] = self.ohlc_dataset[source_column].rolling(
                window=length).max()
