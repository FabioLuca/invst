import pandas as pd


class Summary:

    def get_summary(self, method_name: str):

        self.calc_change(dataframe=self.ohlc_dataset,
                         source_column="Close Final",
                         shift=1,
                         result_column="Summary Change")

        real_dataframe = self.ohlc_dataset[self.ohlc_dataset['Data Type']
                                           == "Real data"]
        prediction_dataframe = self.ohlc_dataset[self.ohlc_dataset['Data Type']
                                                 == "Prediction data"]

        last_event = real_dataframe[f"{method_name} Recommended Events"].iloc[-1]
        previous_event = real_dataframe[f"{method_name} Recommended Events"].iloc[-2]
        day_next_event, next_event = self.day_next_event(
            dataframe=prediction_dataframe, method_name=method_name, last_event=last_event)
        last_value = real_dataframe[f"{method_name} Simulation"].iloc[-1]
        last_value_ref = real_dataframe[f"{method_name} Simulation Reference"].iloc[-1]
        start_value = self.initial_value

        relative_gain = (last_value - start_value) / start_value
        relative_gain_ref = (last_value_ref - start_value) / start_value
        relative_gain_comp = (last_value - last_value_ref) / last_value_ref

        up_movement = self.ohlc_dataset["Summary Change"].clip(
            lower=0).sum() / self.data_length
        down_movement = self.ohlc_dataset["Summary Change"].clip(
            upper=0).abs().sum() / self.data_length

        ratio_up_down = up_movement / down_movement

        self.analysis_results[method_name] = {}
        self.analysis_results[method_name]["Last Day Event"] = last_event
        self.analysis_results[method_name]["Previous Day Event"] = previous_event
        self.analysis_results[method_name]["Next Event"] = next_event
        self.analysis_results[method_name]["Day Next Event"] = day_next_event
        self.analysis_results[method_name]["Analysis length"] = self.data_length
        self.analysis_results[method_name]["Average Volume"] = self.ohlc_dataset["Volume"].mean(
        )
        self.analysis_results[method_name]["Up Movement"] = up_movement
        self.analysis_results[method_name]["Down Movement"] = down_movement
        self.analysis_results[method_name]["Ratio Movement"] = ratio_up_down
        self.analysis_results[method_name]["Relative gain"] = relative_gain
        self.analysis_results[method_name]["Relative gain reference"] = relative_gain_ref
        self.analysis_results[method_name]["Relative gain comparison"] = relative_gain_comp

    def day_next_event(self, dataframe: pd.DataFrame, method_name: str, last_event: str):
        """Calculates the time spam until there is an event change in a
        dataframe. Initially this method is intended to be applied to the
        prediction, but is general to be used also for the non-prediction part.

        Parameters
        ----------
            dataframe: `Pandas Dataframe`
                Dataframe for searching the change of value.
            method_name: `string`
                Method name to be used in the identification of the column to
                be use as reference.
            last_event: `string`
                Last event to be used as reference for the analysis. The value
                should be either `BUY`, `SELL` or `HOLD`.
        Returns
        -------
            day_next_event: `string`
                String with the date of the next change event. In case there are
                no event change inside the time spam, then the returned value
                is `No change`.
            next_event: `string`
                String with the next event description: `BUY`, `SELL` or `HOLD`.
                In case there is no event change in the time spam, then the
                event passed on ``last_event`` will be returned.

        """

        column = f"{method_name} Recommended Events"
        start_event = last_event  # dataframe[column].iloc[0]
        day_next_event = "No change"
        next_event = start_event

        for index, row in dataframe.iterrows():
            if row[column] != start_event:
                day_next_event = str(index)[:10]
                next_event = row[column]
                break

        return day_next_event, next_event
