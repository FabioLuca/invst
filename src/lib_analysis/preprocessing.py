class PreProcessing:
    """Pre processing is intended to make initial operations to fix or adequate
    the data which is received from the API, fo example, limiting the amount of
    data as eventually the series can have years of data, which is not
    necessary; or to define the the correct column for the closing price of the
    entry.

    """

    def truncate_range(self, length: int):
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

        self.ohlc_dataset = self.ohlc_dataset.tail(length)
        #self.ohlc_dataset.reset_index(drop=True, inplace=True)

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
