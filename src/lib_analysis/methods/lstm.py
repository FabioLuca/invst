
#from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
#import urllib.request
import json
import os
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

from src.lib_analysis.basic import Basic


class LSTM (Basic):

    def calc_LSTM(self):

        self.logger.info("Performing LSTM analysis for %s", self.symbol)

        high_prices = self.convert_numpy(source_column="High")
        low_prices = self.convert_numpy(source_column="Low")

        mid_prices = (high_prices+low_prices)/2.0

        train_data, test_data = self.split_data(numpy_data=mid_prices,
                                                percetage_learning=0.8)

        #high_prices = self.ohlc_dataset.loc[:, 'High'].values()
        # high_prices = self.ohlc_dataset['High'].to_numpy()
        # low_prices = self.ohlc_dataset['Low'].to_numpy()
        #low_prices = self.ohlc_dataset.loc[:, 'Low'].values()

        print(mid_prices)
        print(train_data)
        print(test_data)

        return 1
