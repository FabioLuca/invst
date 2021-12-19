import numpy as np
import datetime


class PreProcessing:
    """Pre processing is intended to make initial operations to fix or adequate
    the data which is received from the API, fo example, limiting the amount of
    data as eventually the series can have years of data, which is not
    necessary; or to define the the correct column for the closing price of the
    entry.

    """

    def define_past_time(self):
        self.ohlc_dataset["Data Type"] = "Real data"

    def truncate_range(self, length: int = 0, shift_last: int = 0):
        """Limit the data to a proper length, always keeping the latest data
        available.

        .. note::

            The dataframe to be trim might be based on work-days only, so
            weekends are not included. Attention for such cases, so for example
            if a year of data is necessary, the input should be 250 instead of
            360.

        Parameters
        ----------
            length: int
                Number of entries to be included in the analysis. Data outside
                this range is truncated.

        """
        if 0 < length < self.ohlc_dataset.shape[0]:
            self.ohlc_dataset = self.ohlc_dataset.tail(length + shift_last)
            self.ohlc_dataset = self.ohlc_dataset.head(length)
        #self.ohlc_dataset.reset_index(drop=True, inplace=True)

        self.data_length = len(self.ohlc_dataset)

    def extend_time_range(self, length: int):
        """Populates the Pandas dataframe with dates following the next day for
        predictions. The list skips weekends, however holidays are not taken
        into account, so not skipped.

        Parameters
        ----------
            length: int
                Length of the list of dates.

        Returns
        -------
            None:
                Populated new index with dates on the
                ``ohlc_dataset_prediction`` dataframe, with a sequence of dates
                incrementing one by one. Weekends are skipped in the list.

        """
        self.ohlc_dataset_prediction = self.ohlc_dataset.copy()
        self.ohlc_dataset_prediction = self.ohlc_dataset_prediction[0:0]

        initial_day = list(self.ohlc_dataset.index)[-1]
        initial_day = initial_day.to_pydatetime()

        new_index = []
        count_day = 1

        new_day = initial_day

        new_row = [np.nan] * len(self.ohlc_dataset_prediction.columns)

        for i in range(length):
            new_day = new_day + datetime.timedelta(days=1)
            while new_day.weekday() >= 5:
                new_day = new_day + datetime.timedelta(days=1)

            self.ohlc_dataset_prediction.loc[len(
                self.ohlc_dataset_prediction)] = new_row
            new_index.append(new_day)
            count_day = count_day + 1

        self.ohlc_dataset_prediction.index = new_index

        self.ohlc_dataset_prediction["Data Type"] = "Prediction data"

        self.ohlc_dataset = self.ohlc_dataset.append(
            self.ohlc_dataset_prediction)

    def define_closure(self):
        """Define the column for closure. This is necessary since depending on
        the source of data or on the configuration, there might be different
        columns for it. The new column is named "Close Final".

        """
        headers = self.ohlc_dataset.columns

        if "Adj Close" in headers and "Close Final" not in headers:
            self.ohlc_dataset.columns["Close Final"] = self.ohlc_dataset.columns["Adj Close"]
        elif "Close" in headers and "Close Final" not in headers:
            self.ohlc_dataset.columns["Close Final"] = self.ohlc_dataset.columns["Close"]
