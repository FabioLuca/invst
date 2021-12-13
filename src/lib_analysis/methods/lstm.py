"""
The basic architecture of the

.. image:: https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/LSTM_Cell.svg/1200px-LSTM_Cell.svg.png
    :width: 400
    :align: center
    :alt: Alternative text


"""
import matplotlib.pyplot as plt
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import LSTM as KerasLSTM
from keras.layers import Dropout
from keras.layers import Dense
from src.lib_analysis.basic import Basic


class LSTM (Basic):

    def calc_LSTM(self):
        """Calculate a prediction based on the LSTM (Long Short-Term Memory)
        method, which is a RNN (recurrent neural network) architecture.

        The implementation is based on the following steps:

        # . Vectorize the data, since it starts as a `(N,)` shape, where `N` is
           the number of data points. After vectorization, it becomes of shape
           `(N, 1)`.
        # . Normalize the data points to the range [0, 1].
        # . Splits the data into 2 blocks: learning and testing. This is done
           for all the data available to this points, even if not necessary for
           the algorithm per se. The additional data split is done for reason of
           plotting results.
        #. Strucutre the data for the RNN. See documentation in the
           `create_dataset` method for more details.
        #. Rephase the data to a 3D for LSTM demand: samples, time steps,
           and features. As an example, for the `N` size dataset, if we use
           sequences (called sub-sequences in the code) of size `L`, and given
           only 1 feature (e.g. only the Closing value is used), then this
           tensor will be (N-L-1, L, 1). Note that the N-L-1 is due to the
           previous operation of structuring the data.

        """

        self.logger.info("Performing LSTM analysis for %s", self.symbol)

        index = self.ohlc_dataset.index.to_numpy()
        prices = self.convert_numpy(source_column="Close Final")
        # high_prices = self.convert_numpy(source_column="High")
        # low_prices = self.convert_numpy(source_column="Low")
        # mid_prices = (high_prices+low_prices)/2.0

        # ----------------------------------------------------------------------
        #   Get the data for analysis and adapt to the proper format.
        # ----------------------------------------------------------------------
        data = prices
        data_vector = data.reshape(-1, 1)

        # ----------------------------------------------------------------------
        #   Normalize the data between 0 and 1.
        # ----------------------------------------------------------------------
        scaler = MinMaxScaler(feature_range=(0, 1))
        data_scaled = scaler.fit_transform(data_vector)

        # ----------------------------------------------------------------------
        #   Split the data into training and test.
        # ----------------------------------------------------------------------
        ratio_train = 0.8
        train_data_normalized, test_data_normalized = (
            self.split_data(data=data_scaled,
                            percetage_learning=ratio_train))
        train_data_absolute, test_data_absolute = (
            self.split_data(data=data_vector,
                            percetage_learning=ratio_train))
        train_data_index, test_data_index = (
            self.split_data(data=index,
                            percetage_learning=ratio_train))

        # ----------------------------------------------------------------------
        #   Structure the dataset and reshape for the LSTM
        # ----------------------------------------------------------------------
        sequence_length = 21
        prediction_length = 10
        number_features = 1
        x_train, y_train = self.create_dataset(
            dataset=train_data_normalized,
            input_sequence_length=sequence_length,
            output_sequence_length=prediction_length)
        x_test, y_test = self.create_dataset(
            dataset=test_data_normalized,
            input_sequence_length=sequence_length,
            output_sequence_length=prediction_length)
        x_train_reshaped = x_train.reshape(
            x_train.shape[0], x_train.shape[1], number_features)
        x_test_reshaped = x_test.reshape(
            x_test.shape[0], x_test.shape[1], number_features)

        # ----------------------------------------------------------------------
        #   Makes the model
        # ----------------------------------------------------------------------
        model = Sequential()
        # return_sequences=True,
        model.add(KerasLSTM(50,
                            return_sequences=True,
                            input_shape=(sequence_length, number_features)))
        model.add(KerasLSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))

        model.add(KerasLSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))

        model.add(KerasLSTM(units=50))
        model.add(Dropout(0.2))

        # model.add(KerasLSTM(50))
        # model.add(KerasLSTM(50))
        model.add(Dense(units=1))
        model.compile(loss='mean_squared_error', optimizer='adam')

        epochs = 200
        model.fit(x_train_reshaped, y_train, epochs=epochs, verbose=0)

        train_predict = model.predict(x_train_reshaped)
        test_predict = model.predict(x_test_reshaped)

        train_predict = scaler.inverse_transform(train_predict)
        test_predict = scaler.inverse_transform(test_predict)

        #result = math.sqrt(mean_squared_error(y_train, train_predict))

        train_data_index_redux = train_data_index[(
            sequence_length+prediction_length):]
        test_data_index_redux = test_data_index[(
            sequence_length+prediction_length):]

        train_predict = train_predict.reshape(1, -1)
        test_predict = test_predict.reshape(1, -1)
        train_data_index_redux = train_data_index_redux.reshape(1, -1)
        test_data_index_redux = test_data_index_redux.reshape(1, -1)

        plt.title("Predicted")
        plt.plot(index, data_vector, "-g", label='Original', linewidth=1)
        plt.plot(train_data_index, train_data_absolute, "-.c",
                 linewidth=1, label='Original Train')
        plt.plot(test_data_index, test_data_absolute, "-.m",
                 linewidth=1, label='Original Test')
        plt.plot(train_data_index_redux[0],
                 train_predict[0], "-b", linewidth=2, label='Predicted Train')
        plt.plot(test_data_index_redux[0], test_predict[0],
                 "-r", linewidth=2, label='Predicted Test')
        plt.legend()
        plt.show()

        return 1

    def create_dataset(self, dataset, input_sequence_length: int = 1, output_sequence_length: int = 1, shift_future: int = 0):
        """Structures the data into sequences and labels for the learning. It's
        done by breaking the data into sub-sequences and pairing to the
        respective label.

        For example, a dataset of `N` entries:

        .. math::

            \\text{Seq}_{N} = [x_{1}, x_{2}, x_{3}, x_{4}, \\ldots, x_{N}]

        a sub-sequence of size `L` (where :math:`L < N`) to predict the next
        point after the sequence, it would be defined as:

        .. math::

            \\text{SubSeq}_{i, L} = [x_{i}, x_{i+1}, x_{i+2}, \\ldots, x_{i+L}] \\rightarrow \\text{Predict: } x_{i+L+1}

        As a numeric example, given :math:`\\text{Seq}` with 6 samples:

        .. math::

            \\text{Seq}_{6} = [x_{1}, x_{2}, x_{3}, x_{4}, x_{5}, x_{6}]

        and using 3 samples to predict the next one, so the parameter
        `time_step` is equal to 3:

        .. math::

            \\text{SubSeq}_{1, 3} = \\left[ x_{1}, x_{2}, x_{3} \\right] \\rightarrow \\text{Predict: } x_{4}

            \\text{SubSeq}_{2, 3} = \\left[ x_{2}, x_{3}, x_{4} \\right] \\rightarrow \\text{Predict: } x_{5}

            \\text{SubSeq}_{3, 3} = \\left[ x_{3}, x_{4}, x_{5} \\right] \\rightarrow \\text{Predict: } x_{6}

        Parameters
        ----------
            dataset: data
                Name of the column in the Pandas Dataframe to be used for the
                calculation of the moving average.
            input_sequence_length: integer, optional
                Length of the sequences.
            output_sequence_length: integer, optional
                Length of the sequences.
            shift_future: integer, optional
                Length of the sequences.

        Returns
        -------
            sequences: Numpy array
                Array of sequence arrays paired to the labels.
            labels: Numpy array
                Array of labels paired to the sequence arrays.

        """
        dataX = []
        dataY = []

        for i in range(len(dataset)-input_sequence_length-output_sequence_length):

            subsequence = dataset[(i): (i + input_sequence_length)]
            label = dataset[(i + input_sequence_length + shift_future): (i +
                                                                         input_sequence_length + shift_future + output_sequence_length)]
            if output_sequence_length == 1:
                label = label[0]
            dataX.append(subsequence)
            dataY.append(label)

        return np.array(dataX), np.array(dataY)
