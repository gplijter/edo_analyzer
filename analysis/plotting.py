from pathlib import Path
from tkinter import Tk

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends._backend_tk import FigureManagerTk

from .configuration import CONFIG
from .constants import (DATA_TAGS, LABELS, UI_BACKWARD_TOUCH_VIEW,
                        UI_CALIBRATION_VIEW, UI_FORWARD_TOUCH_VIEW, UNITS,
                        ResultType)
from .data import EdoData
from .extractionfuncs import find_calibration_indices, find_touch_indices

mpl.rcParams['backend'] = 'TkAgg'

def showMaximized(manager: FigureManagerTk) -> None:
    root: Tk = manager.window
    root.state("zoomed")
    return None


def annotate_label_with_name(label="FULL RANGE"):
    return f"{Path(CONFIG['filename']).name} - {label}"


def plot_time_distribution():
    edo_data = EdoData()
    time_arr = edo_data.resampled_time(result_type=ResultType.SECONDS)

    plt.figure()
    plt.title(annotate_label_with_name("Time difference over time"))
    plt.plot(time_arr, edo_data.dataset["Timestamp"].diff() / 1000, ".")
    plt.xlabel("Time (sec)")
    plt.ylabel("Time diff (sec)")
    plt.grid()

    # showMaximized(plt.get_current_fig_manager())


def plot_sensor_data(src="Accelerometer"):
    edo_data = EdoData()
    time_arr = edo_data.resampled_time(result_type=ResultType.SECONDS)
    touch_indices = edo_data.fetch_markers("R2P", "touches", result_type=ResultType.INDEX)

    fig, axs = plt.subplots(4, 1)
    fig.suptitle(annotate_label_with_name())

    label = LABELS[src.lower()]
    unit = UNITS[src.lower()]

    axs_flattened = axs.flatten()
    for count, (ax, tag) in enumerate(zip(axs_flattened, DATA_TAGS)):
        ax.set_title(f"{tag} - {src}")
        ax.sharex(axs_flattened[0])

        ax.plot(time_arr, edo_data.dataset[f"{tag} [{label}X]"], "r", label=f"{label}X")
        ax.plot(time_arr, edo_data.dataset[f"{tag} [{label}Y]"], "g", label=f"{label}Y")
        ax.plot(time_arr, edo_data.dataset[f"{tag} [{label}Z]"], "b", label=f"{label}Z")

        ax.vlines(
            time_arr[touch_indices],
            *edo_data.get_y_range(tag, label),
            colors="k",
            label="touch",
            linestyles={"dashdot"},
        )

        if label == "acc" and tag.lower() == "object":
            ax.plot(
                time_arr,
                edo_data.object_norm(label),
                "y",
                label="norm_acc",
            )
            ax.hlines(
                y=eval(edo_data.config["R2P"].get("threshold")),
                xmin=time_arr[0],
                xmax=time_arr[-1],
                colors="k",
                label="threshold",
                linestyles={"dashed"},
            )

        # if label == "mag" and tag.lower() == "object":
        #     ax.plot(
        #         time_arr,
        #         edo_data.object_norm(label),
        #         "k",
        #         label="norm_mag",
        #     )

        ax.set(ylabel=f"--> {unit}")
        ax.grid()
        ax.legend(loc="upper left")
        if count > 2:
            ax.set(xlabel="Time (sec)")

    # showMaximized(plt.get_current_fig_manager())
    fig.subplots_adjust(left=0.16, right=0.97, top=0.93, bottom=0.06, hspace=0.25)
    return fig, axs_flattened


def update_counter(key: str, info: dict) -> None:
    min_id = 0
    max_id = len(info["touches"]) - 1

    if key == UI_BACKWARD_TOUCH_VIEW:
        info["counter"] -= 1
        if info["counter"] < min_id:
            info["counter"] = min_id

    elif key == UI_FORWARD_TOUCH_VIEW:
        info["counter"] += 1
        if info["counter"] > max_id:
            info["counter"] = max_id


def get_start_stop_view(key: str, info: dict) -> tuple:
    start = 0
    stop = -1
    if key == UI_BACKWARD_TOUCH_VIEW or key == UI_FORWARD_TOUCH_VIEW:
        start, _, stop = info["touches"][info["counter"]]
    elif key == UI_CALIBRATION_VIEW:
        start, stop = info["calibration"][0]
    return start, stop


def update_suptitle(key: str, info: dict) -> None:
    info["fig"].suptitle(annotate_label_with_name())
    if key == UI_BACKWARD_TOUCH_VIEW or key == UI_FORWARD_TOUCH_VIEW:
        info["fig"].suptitle(annotate_label_with_name(f"TOUCH #{info['counter'] + 1}"))
    elif key == UI_CALIBRATION_VIEW:
        info["fig"].suptitle(annotate_label_with_name("CALIBRATION"))
    return None


def scale_axis(key: str, info: dict) -> None:
    edo_data = EdoData()
    start, stop = get_start_stop_view(key, info)
    for ax in info["axes"]:
        # x-axis
        ax.set_xlim(
            edo_data.dataset["Timestamp"].iloc[start] / 1000, edo_data.dataset["Timestamp"].iloc[stop] / 1000
        )

        # y-axis
        y_data = np.array([line.get_ydata() for line in ax.lines])
        if key == UI_BACKWARD_TOUCH_VIEW or key == UI_FORWARD_TOUCH_VIEW or key == UI_CALIBRATION_VIEW:
            y_data = np.array([line.get_ydata()[range(start, stop)] for line in ax.lines])
        ax.set_ylim(y_data.min() * 1.1, y_data.max() * 1.1)


def on_key_event(event, info: dict):
    if "shift" in event.key or "win" in event.key:
        return

    _ = [func(event.key, info) for func in [update_counter, update_suptitle, scale_axis]]
    plt.draw()


def loop_through_views(fig: plt.Figure, axes: list[plt.Axes]):
    info = {
        "counter": 0,
        "axes": axes,
        "fig": fig,
        "touches": find_touch_indices(),
        "calibration": find_calibration_indices(),
    }
    fig.canvas.mpl_connect("key_press_event", lambda event: on_key_event(event, info))


def stack_figures():
    def get_manager() -> FigureManagerTk:
        return plt.get_current_fig_manager()

    N_fig = len(plt.get_fignums())
    mngr = get_manager()
    screenwidth = mngr.window.winfo_screenwidth()
    screenheight = mngr.window.winfo_screenheight()
    screenwidth_fig = int(screenwidth / N_fig)
    x_pos = -10
    for fignum in plt.get_fignums():
        _figure: plt.Figure = plt.figure(fignum)
        mngr = get_manager()
        mngr.window.geometry(f"{screenwidth_fig}x{screenheight - 80}+{x_pos}+0")
        x_pos += screenwidth_fig
