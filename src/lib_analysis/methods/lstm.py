"""The basic architecture of the

.. image:: https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/LSTM_Cell.svg/1200px-LSTM_Cell.svg.png
    :width: 400
    :align: center
    :alt: Alternative text

"""
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM as KerasLSTM
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from keras.layers import Activation
from src.lib_analysis.basic import Basic


class LSTM (Basic):

    def calc_LSTM(self,
                  dataframe: pd.DataFrame,
                  source_column: str,
                  sequence_length: int,
                  prediction_length: int = 1,
                  extend_original_data: bool = True,
                  result_column: str = "",
                  ratio_train: float = -1.0,
                  verbose: bool = False):
        """Calculate a prediction based on the LSTM (Long Short-Term Memory)
        method, which is a RNN (recurrent neural network) architecture.

        The implementation is based on the following steps:

        1. Vectorize the data, since it starts as a ``(N,)`` shape, where `N`
           is the number of data points. After vectorization, it becomes of
           shape ``(N, 1)``.
        2. Normalize the data points to the range [0, 1].
        3. Splits the data into 2 blocks: learning and testing. This is done
           for all the data available to this points, even if not necessary for
           the algorithm per se. The additional data split is done for reason of
           plotting results.
        4. Strucutre the data for the RNN. See documentation in the
           ``create_dataset`` method for more details.
        5. Rephase the data to a 3D for LSTM demand: samples, time steps,
           and features. As an example, for the `N` size dataset, if we use
           sequences (called sub-sequences in the code) of size `L`, and given
           only 1 feature (e.g. only the Closing value is used), then this
           tensor will be (N-L-1, L, 1). Note that the `N-L-1` is due to the
           previous operation of structuring the data.

        Parameters
        ----------
            sequence_length: int
                Number of samples to be used as sub-sequences for the feature
                learning.
            prediction_length: int, optional
                Number of samples to be used as sub-sequences for the feature
                learning.
            ratio_train: float, optional
                Value between 0 and 1 that represents the division in the
                series to split between training and test data. If a value of
                -1 is supplied (default value), then the split is done so that
                the last `N` samples (with `N` = sequence_length) will be
                allocate to test, and thus provide a prediction of length
                ``prediction_length``, while all the remaining data will be used
                for training.

        """
        number_blocks = 200
        number_features = 1
        hidden_neurons = 300
        epochs = 200
        normalization_range = (-1, 1)

        self.logger.info(
            "Performing LSTM analysis for %s for source %s", self.symbol, source_column)

        if result_column == "":
            result_column = f"LSTM {sequence_length} {prediction_length} {source_column}"

        # ----------------------------------------------------------------------
        #   Get the data for analysis and adapt to the proper format.
        # ----------------------------------------------------------------------
        index = dataframe[dataframe['Data Type']
                          == "Real data"].index.to_numpy()
        new_index = self.create_future_index(steps=prediction_length,
                                             previous_day=index[-1])
        data = self.convert_numpy(dataframe=dataframe,
                                  source_column=source_column)
        data_vector = data.reshape(-1, 1)

        # ----------------------------------------------------------------------
        #   Normalize the data between 0 and 1.
        # ----------------------------------------------------------------------
        scaler = MinMaxScaler(feature_range=normalization_range)
        data_normalized = scaler.fit_transform(data_vector)

        # ----------------------------------------------------------------------
        #   Split the data into training and test.
        # ----------------------------------------------------------------------
        train_data_normalized, test_data_normalized = (
            self.split_data(data=data_normalized,
                            percetage_learning=ratio_train,
                            sequence_length=sequence_length))

        train_data_absolute, test_data_absolute = (
            self.split_data(data=data_vector,
                            percetage_learning=ratio_train,
                            sequence_length=sequence_length))

        train_data_index, test_data_index = (
            self.split_data(data=index,
                            percetage_learning=ratio_train,
                            sequence_length=sequence_length))

        # ----------------------------------------------------------------------
        #   Structure the dataset and reshape for the LSTM.
        # ----------------------------------------------------------------------
        x_train, y_train = self.create_dataset(
            dataset=train_data_normalized,
            input_sequence_length=sequence_length,
            output_sequence_length=prediction_length)

        x_test, y_test = self.create_dataset(
            dataset=test_data_normalized,
            input_sequence_length=sequence_length,
            output_sequence_length=prediction_length)

        if x_train is not None:
            x_train_reshaped = x_train.reshape(
                x_train.shape[0], x_train.shape[1], number_features)
        else:
            x_train_reshaped = None

        if x_test is not None:
            x_test_reshaped = x_test.reshape(
                x_test.shape[0], x_test.shape[1], number_features)
        else:
            x_test_reshaped = None

        # ----------------------------------------------------------------------
        #   Makes the model
        # ----------------------------------------------------------------------
        model = self.create_lstm_model(
            X=x_train_reshaped,
            Y=y_train,
            number_blocks=number_blocks,
            epochs=epochs,
            sequence_length=sequence_length,
            prediction_length=prediction_length,
            number_features=number_features,
            hidden_neurons=hidden_neurons,
            save_model=False,
            source_column=source_column
        )

        train_predict = model.predict(x_train_reshaped)
        test_predict = model.predict(x_test_reshaped)

        train_predict = self.squash_output(data=train_predict, mode="last")
        test_predict = self.squash_output(data=test_predict, mode="last")

        train_predict = scaler.inverse_transform(train_predict)
        test_predict = scaler.inverse_transform(test_predict)

        # ----------------------------------------------------------------------
        #   Results from the fitting are output'ed in 2 ways: First they are
        #   appended to the original data, as a sequence of the previous ones.
        #   Second, the data is also stored in a new columns in the dataframe.
        # ----------------------------------------------------------------------
        if extend_original_data:
            dataframe.loc[dataframe["Data Type"]
                          == "Prediction data", source_column] = test_predict.tolist()

        self.ohlc_dataset_prediction[source_column] = test_predict.tolist()

        temp_train_predict = (
            ([[np.nan]] * sequence_length) +
            (train_predict.tolist()) +
            ([[np.nan]] * sequence_length)
        )

        dataframe.loc[dataframe["Data Type"]
                      == "Real data", result_column] = temp_train_predict
        dataframe.loc[dataframe["Data Type"]
                      == "Prediction data", result_column] = test_predict.tolist()

        # ----------------------------------------------------------------------
        #   Plot and print some data for debugging reasons.
        # ----------------------------------------------------------------------
        if verbose:
            train_data_index_redux = train_data_index[(
                sequence_length):]
            test_data_index_redux = test_data_index[(
                sequence_length):]

            train_predict = train_predict.reshape(1, -1)
            test_predict = test_predict.reshape(1, -1)
            train_data_index_redux = train_data_index_redux.reshape(1, -1)
            test_data_index_redux = test_data_index_redux.reshape(1, -1)

            plt.title("Debug Predicted")
            plt.plot(index, data_vector, "-g", label='Original', linewidth=1)
            plt.plot(train_data_index, train_data_absolute, "-.c",
                     linewidth=1, label='Original Train')
            plt.plot(test_data_index, test_data_absolute, "-.m",
                     linewidth=1, label='Original Test')
            plt.plot(train_data_index_redux[0],
                     train_predict[0], "-b",
                     # marker=".",
                     # markersize=8,
                     linewidth=2, label='Predicted Train')
            if 0 <= ratio_train <= 1:
                plt.plot(test_data_index_redux[0], test_predict[0],
                         "-r", linewidth=2,
                         label='Predicted Test')
            else:
                plt.plot(new_index, test_predict[0], "-r",
                         marker=".",
                         markersize=8,
                         linewidth=2, label='Predicted Test')

            plt.legend()
            plt.show()

            print("===============================================================")
            print(f"Size original data:      {len(data)}")
            print(f"Size original index:     {len(index)}")
            print(f"Size added index:        {len(new_index)}")
            print(f"Sequence length:         {sequence_length}")
            print(f"Prediction length:       {prediction_length}")
            print(f"Shape normalized train:  {train_data_normalized.shape}")
            print(f"Shape normalized test:   {test_data_normalized.shape}")
            print(f"Shape absolute train:    {train_data_absolute.shape}")
            print(f"Shape absolute test:     {test_data_absolute.shape}")
            print(f"Shape index train:       {train_data_index.shape}")
            print(f"Shape index train:       {test_data_index.shape}")
            print(f"Shape X train:           {x_train.shape}")
            print(f"Shape Y train:           {y_train.shape}")
            print(f"Shape X test:            {x_test.shape}")
            print(f"Shape Y test:            {y_test.shape}")
            print(f"Shape index test:        {test_data_index.shape}")
            print(f"Shape predicted train:   {train_predict.shape}")
            print(f"Shape predicted test:    {test_predict.shape}")
            print(f"Plot X:                  {len(train_data_index_redux[0])}")
            print(f"Plot Y:                  {len(train_predict[0])}")
            print("===============================================================")

    def create_dataset(self, dataset, input_sequence_length: int = 1, output_sequence_length: int = 1, shift_future: int = 0):
        """Structures the data into sequences and labels for the learning. It's
        done by breaking the data into sub-sequences and pairing to the
        respective label (sequence or single value).

        For example, in the case the predicted sequence has length one, a
        dataset of `N` entries:

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
        ``time_step`` is equal to 3:

        .. math::

            \\text{SubSeq}_{1, 3} = \\left[ x_{1}, x_{2}, x_{3} \\right] \\rightarrow \\text{Predict: } x_{4}

            \\text{SubSeq}_{2, 3} = \\left[ x_{2}, x_{3}, x_{4} \\right] \\rightarrow \\text{Predict: } x_{5}

            \\text{SubSeq}_{3, 3} = \\left[ x_{3}, x_{4}, x_{5} \\right] \\rightarrow \\text{Predict: } x_{6}

        Example (predicted length greater than one):

        .. image:: _static/images/drawing_lstm_structure.png
            :width: 600
            :align: center
            :alt: Example of data structure

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

        # input_sequence_length = 5
        # output_sequence_length = 5
        # dataset = dataset[:11]

        # print("---------------------------------------------------------------")
        # print(f"Input length:        {dataset.shape}")
        # print(f"Input seq length:    {input_sequence_length}")
        # print(f"Output seq length:   {output_sequence_length}")
        # print(f"Shift future:        {shift_future}")

        if input_sequence_length == len(dataset):
            # print("Same size")
            dataX = dataset
            dataY = []
            dataX = [dataX]
        else:
            # print("Different size")
            # print(dataset.flatten())
            for i in range(len(dataset)-input_sequence_length-output_sequence_length + 1):

                subsequence = dataset[
                    (i): (i + input_sequence_length)]

                start_label = i + input_sequence_length + shift_future
                label = dataset[
                    (start_label): (start_label + output_sequence_length)]

                if output_sequence_length == 1:
                    label = label[0]

                # print(
                #     f"SEQ: {i} {'        ' * i} {subsequence.flatten()}  --> {label.flatten()}")
                # # print(f"LAB  {'      ' * i} {label.flatten()}")

                dataX.append(subsequence)
                dataY.append(label)

        # print(f"Data X length:        {len(dataX)}")
        # print(f"Data Y length:        {len(dataY)}")
        # print("---------------------------------------------------------------")

        return np.array(dataX), np.array(dataY)

    def create_lstm_model(self, X, Y,
                          number_blocks: int,
                          epochs: int,
                          sequence_length: int,
                          prediction_length: int,
                          number_features: int,
                          hidden_neurons: int = 100,
                          save_model: bool = False,
                          source_column: str = ""):
        """Creates the LSTM model. The architecture can be different, depending
        on the inputs from the method. Basically 3 designs are possible:

        #. Many to one
        #. Many to many where the size of the input and output are the same
        #. Many to many where the size of the input and output are different

        Pictured below:

        .. image:: _static/images/lstm_design.png
            :width: 600
            :align: center
            :alt: Example of data squashing

        For the application, the most relevant is the last case, since more data
        can be used to try to predict a range not so far into the future, and
        thus try to increase the chances of success.

        To optimize operation, the method will store the model after calculation
        in case the parameter ``save_model`` is enabled (``true``). Also in
        case this parameter is enabled, before starting a new run, it tries to
        load the stored model.

        """
        model_name = f"{source_column}_{number_blocks}_{epochs}_{sequence_length}_{prediction_length}_{number_features}"
        model_path = f"models/lstm_{model_name}"

        if Path(model_path).is_dir() and save_model:
            model = keras.models.load_model(model_path)

        else:

            # ------------------------------------------------------------------
            #   LSTM many to many with different sizes.
            # ------------------------------------------------------------------
            if prediction_length > 1 and sequence_length > 1 and sequence_length != prediction_length:

                self.logger.info(
                    "LSTM analysis based on model many to many with different sides.")

                model = Sequential()
                model.add(KerasLSTM(number_blocks,
                                    input_shape=(sequence_length,
                                                 number_features)
                                    ))
                model.add(RepeatVector(prediction_length))
                model.add(KerasLSTM(number_blocks,
                                    return_sequences=True
                                    ))
                model.add(TimeDistributed(Dense(number_features)))
                model.add(Activation('linear'))

            # ------------------------------------------------------------------
            #   LSTM many to many with same sizes.
            # ------------------------------------------------------------------
            elif prediction_length > 1 and sequence_length == prediction_length:

                self.logger.info(
                    "LSTM analysis based on model many to many with same sizes.")

                model = Sequential()
                model.add(KerasLSTM(number_blocks,
                                    activation='relu',
                                    input_shape=(sequence_length,
                                                 number_features)
                                    ))
                model.add(RepeatVector(prediction_length))
                model.add(KerasLSTM(number_blocks,
                                    activation='relu',
                                    return_sequences=True
                                    ))
                model.add(TimeDistributed(Dense(number_features)))

            # ------------------------------------------------------------------
            #   LSTM many to one.
            # ------------------------------------------------------------------
            elif prediction_length == 1 and sequence_length > 1:

                self.logger.info(
                    "LSTM analysis based on model many to one.")
                model = Sequential()
                model.add(KerasLSTM(number_blocks,
                                    return_sequences=True,
                                    input_shape=(sequence_length,
                                                 number_features)
                                    ))
                model.add(KerasLSTM(units=number_blocks,
                                    return_sequences=True
                                    ))
                model.add(Dropout(0.2))

                model.add(KerasLSTM(units=number_blocks,
                                    return_sequences=True
                                    ))
                model.add(Dropout(0.2))

                model.add(KerasLSTM(units=number_blocks))
                model.add(Dropout(0.2))

                model.add(Dense(units=1))

            model.compile(loss='mean_squared_error', optimizer='adam')
            model.fit(X, Y, epochs=epochs, verbose=0)

            if save_model:
                model.save(model_path)

        return model

    def squash_output(self, data, mode: str = "average"):
        """Combines the overlapping results from the steps into a single
        sequence of values. The combination can be done by different methods:

        1. Average.
        2. Last.
        3. First.
        4. Weighted average (linear weigths, with highest weight to the last
           value).

        The squashing is the reverse operation from the ``create_dataset``
        method. To illustrate it, an example of a 7 elements is presented below:

        .. image:: _static/images/drawing_lstm_squash.png
            :width: 600
            :align: center
            :alt: Example of data squashing

        Incide each cell (value), the index is written, so first the data
        element index and then the index inside this vector. The last value is
        always 0, since we have here only 2 dimensions.

        The operation is done by a more simple iteration. To represent it, the
        same data is represented below, just rearranging it. The colors are used
        to indicate the tracking of the "movement":

        .. image:: _static/images/drawing_lstm_rearrange.png
            :width: 600
            :align: center
            :alt: Example of rearrangement

        The important point is to note that **each level has an unique sum of
        the indexes**, so the first anti-diagonal cut is denoted by sum 0,
        the second anti-diagonal cut by sum equal to 1, and so one.

        A second note is that the initial part and final part of the squashing
        have less elements to be used.

        Parameters
        ----------
            data: np.array
                Data to be squashed.
            mode: string, optional
                The method to be used for the combination of the values. The
                possible methods are:

                * ``average``
                * ``last``
                * ``first``
                * ``weighted-average``

        Returns
        -------
            results: np.array
                List of values from ``data`` squashed into a single dimension
                vector. The size of the output is given by the first dimension
                of data added to its second dimension.

        """

        results = []

        if data.shape[0] == 1 or (len(data.shape) == 2 and data.shape[1] == 1):
            results = data.flatten()

        else:
            results = [[] for Null in range(data.shape[0] + data.shape[1] - 1)]
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    results[i+j].append(data[i][j][0])

            for k in range(data.shape[0] + data.shape[1] - 1):
                if mode == "average":
                    results[k] = sum(results[k]) / len(results[k])
                elif mode == "last":
                    # The new list is inverted
                    results[k] = results[k][0]
                elif mode == "first":
                    # The new list is inverted
                    results[k] = results[k][-1]
                elif mode == "weighted-average":
                    weights = np.linspace(1, len(results[k]))
                    values = np.array(results[k])
                    results[k] = sum(np.multiply(
                        weights, values)) / sum(weights)

        results = np.array(results)
        results = results.reshape(-1, 1)

        return results

    def create_future_index(self, steps: int, previous_day: np.timedelta64):
        """Creates an array of dates following the Numpy timedelta type to be
        used for the predictions. The list skips weekends, however holidays are
        not taken into account, so not skipped.

        Parameters
        ----------
            steps: int
                Length of the list of dates.
            previous_day: np.timedelta64
                The last day to be used for the list. The first date of the
                list will be next one from the passed ``previous_day``.

        Returns
        -------
            sequences: list of np.timedelta64
                List with a sequence of dates, incrementing one by one. Weekends
                are skipped in the list.

        """

        new_index = []
        count_day = 1

        for i in range(steps):
            new_day = previous_day + np.timedelta64(count_day, 'D')
            while not np.is_busday(str(new_day).split('T')[0]):
                count_day = count_day + 1
                new_day = previous_day + np.timedelta64(count_day, 'D')

            new_index.append(new_day)
            count_day = count_day + 1

        return new_index
