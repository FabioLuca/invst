

class Summary:

    def get_summary(self, method_name: str):

        self.calc_change(source_column="Close Final",
                         shift=1,
                         result_column="Summary Change")

        last_event = self.ohlc_dataset[f"{method_name} Recommended Events"].iloc[-1]
        previous_event = self.ohlc_dataset[f"{method_name} Recommended Events"].iloc[-2]
        last_value = self.ohlc_dataset[f"{method_name} Simulation"].iloc[-1]
        last_value_ref = self.ohlc_dataset[f"{method_name} Simulation Reference"].iloc[-1]
        start_value = self.initial_value

        relative_gain = (last_value - start_value) / start_value
        relative_gain_ref = (last_value_ref - start_value) / start_value
        relative_gain_comp = (last_value - last_value_ref) / last_value_ref

        up_movement = self.ohlc_dataset["Summary Change"].clip(
            lower=0).sum() / self.analysis_length
        down_movement = self.ohlc_dataset["Summary Change"].clip(
            upper=0).abs().sum() / self.analysis_length

        ratio_up_down = up_movement / down_movement

        self.analysis_results[method_name] = {}
        self.analysis_results[method_name]["Last Day Event"] = last_event
        self.analysis_results[method_name]["Previous Day Event"] = previous_event
        self.analysis_results[method_name]["Analysis length"] = self.analysis_length
        self.analysis_results[method_name]["Average Volume"] = self.ohlc_dataset["Volume"].mean(
        )
        self.analysis_results[method_name]["Up Movement"] = up_movement
        self.analysis_results[method_name]["Down Movement"] = down_movement
        self.analysis_results[method_name]["Ratio Movement"] = ratio_up_down
        self.analysis_results[method_name]["Relative gain"] = relative_gain
        self.analysis_results[method_name]["Relative gain reference"] = relative_gain_ref
        self.analysis_results[method_name]["Relative gain comparison"] = relative_gain_comp
