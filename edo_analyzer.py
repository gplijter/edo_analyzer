import os

from pathlib import Path
from tkinter import filedialog as fd

from analysis import CONFIG
from analysis.data import EdoData
from analysis.plotting import (loop_through_views, plot_sensor_data,
                               plot_time_distribution, plt, stack_figures)


def main():
    foldername = fd.askdirectory(initialdir=Path(os.getcwd()))
    CONFIG['filename'] = foldername

    # CONFIG['filename'] =  r"O:\Software_Projects\__Repositories\git\ac4s_algodev\verification\transfer_2278041_files_5e749021\20230815_143348_results_healthy"
    # CONFIG['filename'] =  r"O:\Software_Projects\__Repositories\git\ac4s_algodev\verification\transfer_2278041_files_5e749021\20230815_144706_results_patient_1"
    # CONFIG['filename'] =  r"O:\Software_Projects\__Repositories\git\ac4s_algodev\verification\transfer_2278041_files_5e749021\20230817_094426_results_patient_2"
    try:
        edoData = EdoData()
    except FileNotFoundError as e:
        print(f"No valid dataset found. ({CONFIG['filename']})")
        return

    edoData.printInfo()

    # plot_time_distribution()
    loop_through_views(*plot_sensor_data("Accelerometer"))
    loop_through_views(*plot_sensor_data("Gyroscope"))
    loop_through_views(*plot_sensor_data("Magnetometer"))

    stack_figures()

    plt.show()

if __name__ == "__main__":
    main()



