from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .configuration import CONFIG
from .constants import ACC_TAGS, ACC_TO_SI, ResultType
from .singleton import Singleton


@dataclass
class EdoData(metaclass=Singleton):
    dataset: pd.DataFrame = None
    log: ConfigParser = None
    name: str = ""

    def __post_init__(self):
        self.dataset = pd.read_parquet(Path(f"{CONFIG['filename']}\combined.parquet"))
        self.dataset[ACC_TAGS] *= ACC_TO_SI

        self.log = ConfigParser()
        self.log.read(Path(f"{CONFIG['filename']}\edo.log"))

        self.config = ConfigParser()
        self.config.read(Path(f"{CONFIG['filename']}\config.cfg"))

        self.name = Path(f"{CONFIG['filename']}").name

    def printInfo(self):
        print(
            f"t_measured)\t\t{(self.dataset['Timestamp'].iloc[-1] - self.dataset['Timestamp'].iloc[0]) / 1000:10.2f} sec"
        )
        print(f"Δ_t (mean)\t\t{self.dataset['Timestamp'].diff().mean():10.2f} msec")
        print(f"Δ_t (std)\t\t\t{self.dataset['Timestamp'].diff().std():10.2f} msec")
        print(f"Δ_t (minimal)\t\t{self.dataset['Timestamp'].diff().min():10.2f} msec")
        print(f"Δ_t (maximal)\t\t{self.dataset['Timestamp'].diff().max():10.2f} msec")

    def fetch_markers(self, section: str, key: str, result_type: ResultType = ResultType.INDEX) -> list:
        if result_type == ResultType.MILLIS:
            return eval(self.log[section].get(key))
        elif result_type == ResultType.SECONDS:
            return [x / 1000 for x in eval(self.log[section].get(key))]
        elif result_type == ResultType.INDEX:
            return [
                self.dataset.index[self.dataset["Timestamp"] == x].to_list()[0]
                for x in eval(self.log[section].get(key))
            ]

    def resampled_time(self, result_type: ResultType = ResultType.SECONDS):
        time_arr_ms = self.dataset["Timestamp"].to_list()
        if result_type == ResultType.MILLIS:
            return np.linspace(time_arr_ms[0], time_arr_ms[-1], len(time_arr_ms))
        elif result_type == ResultType.SECONDS:
            return np.linspace(time_arr_ms[0] / 1000, time_arr_ms[-1] / 1000, len(time_arr_ms))
        elif result_type == ResultType.INDEX:
            raise Exception(f"{result_type=} not valid in {self.resampled_time.__qualname__}")

    def object_norm(self, label: str):
        return np.linalg.norm(
            self.dataset[
                [
                    f"Object [{label}X]",
                    f"Object [{label}Y]",
                    f"Object [{label}Z]",
                ]
            ],
            axis=1,
        )

    def get_y_range(self, tag, label):
        data = np.array(
            [
                self.dataset[f"{tag} [{label}X]"],
                self.dataset[f"{tag} [{label}Y]"],
                self.dataset[f"{tag} [{label}Z]"],
            ]
        )
        return (data.min(), data.max())
