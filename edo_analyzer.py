import os
from pathlib import Path
from tkinter import filedialog as fd

from analysis import CONFIG
from analysis.data import EdoData
from analysis.plotting import (loop_through_views, plot_sensor_data,
                               plot_time_distribution, plt,
                               show_instruction_window, stack_figures)

CONFIG["filename"] = r"ac4s_datasets/20230815_143348_results_healthy"

def main():
    if CONFIG["filename"] == "":
        foldername = fd.askdirectory(initialdir=Path(os.getcwd()))
        CONFIG["filename"] = foldername

    try:
        edoData = EdoData()
    except FileNotFoundError as e:
        print(f"No valid dataset found. ({CONFIG['filename']})")
        return

    edoData.print_info()

    # plot_time_distribution()
    # plot_sensor_data("Accelerometer")
    loop_through_views(*plot_sensor_data("Accelerometer"))
    loop_through_views(*plot_sensor_data("Gyroscope"))
    loop_through_views(*plot_sensor_data("Magnetometer"))

    stack_figures()

    show_instruction_window()


if __name__ == "__main__":
    main()
    plt.show()
