import sys
import base64
from io import BytesIO
from pathlib import Path
from tkinter import Tk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends._backend_tk import FigureManagerTk

from .configuration import CONFIG
from .constants import (ACC_TO_SI, DATA_TAGS, LABELS, UI_BACKWARD_TOUCH_VIEW,
                        UI_CALIBRATION_VIEW, UI_FORWARD_TOUCH_VIEW,
                        UI_IGNORE_PRESSES, UNITS, ResultType)
from .data import EdoData
from .extractionfuncs import find_calibration_indices, find_touch_indices
from .tk_objects import InstructionWindowSingleton

#
# class InstructionWindow(metaclass=Singleton):
#     _isclosed: bool = False
#     _instruction_text = (
#         "pressing 'c' = show calibration\n"
#         "pressing '→' = show next touch\n"
#         "pressing '←' = show previous touch)\n"
#         "pressing 'f' = show fullscreen\n"
#         "pressing 'ctrl+s' = save view\n"
#         "pressing 'q' = close all view\n"
#         "pressing any other = reset view\n"
#     )
#     def __init__(self, *arg, **kwargs):
#         super(InstructionWindow, self).__init__(*arg, **kwargs)
#         self.setupUI()
#
#     def setupUI(self):
#         root = tk.Toplevel()
#         root.title("Instruction for using EDO Analyzer")
#         text = tk.Text(root, wrap="word", width=50, height=8, borderwidth=1)
#         # t.tag_configure("blue", foreground="blue")
#         text.pack(sid="top", fill="both", expand=True)
#         text.insert("1.0", self._instruction_text)
#         text.config(state=tk.DISABLED)
#         tk.Button(root, text="OK", height=5, command=lambda: self.close(root)).pack()
#
#     @property
#     def is_closed(self):
#         return self._isclosed
#
#     @is_closed.setter
#     def is_closed(self, val: bool):
#         self._isclosed = val
#
#     def close(self, root: tk.Toplevel):
#         self.is_closed = True
#         root.destroy()


def get_manager() -> FigureManagerTk:
    return plt.get_current_fig_manager()


def show_maximized(manager: FigureManagerTk) -> None:
    root: Tk = manager.window
    root.state("zoomed")
    return None


def annotate_label_with_name(label="FULL RANGE"):
    return f"{Path(CONFIG['filename']).name} - {label}"


def show_instruction_window():
    win = InstructionWindowSingleton()
    if win.is_closed:
        win.setupUI()
    else:
        win.raise_()


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
    fig.suptitle(annotate_label_with_name(), style="italic")

    label = LABELS[src.lower()]
    unit = UNITS[src.lower()]

    axs_flattened = axs.flatten()
    for count, (ax, tag) in enumerate(zip(axs_flattened, DATA_TAGS)):
        ax.set_title(f"{tag} - {src}", fontweight="bold")

        ax.plot(time_arr, edo_data.dataset[f"{tag} [{label}X]"], "r", label=f"{label}X")
        ax.plot(time_arr, edo_data.dataset[f"{tag} [{label}Y]"], "g", label=f"{label}Y")
        ax.plot(time_arr, edo_data.dataset[f"{tag} [{label}Z]"], "b", label=f"{label}Z")

        ax.vlines(
            time_arr[touch_indices],
            *edo_data.get_y_range(tag, label),
            colors="k",
            label="touch",
            linestyles={"dashdot"},
            linewidth=1.5,
        )

        if label == "acc" and tag.lower() == "object":
            ax.plot(
                time_arr,
                edo_data.object_norm(label),
                "y",
                label="norm_acc",
            )
            ax.hlines(
                y=eval(edo_data.config["R2P"].get("threshold")) * ACC_TO_SI,
                xmin=time_arr[0],
                xmax=time_arr[-1],
                colors="k",
                label="threshold",
                linestyles={"dashed"},
            )

        ax.sharex(axs_flattened[0])
        ax.set(ylabel=f"--> {unit}")
        ax.yaxis.set_label_coords(-0.06, 0.5)
        ax.grid()
        ax.legend(loc="upper left")
        if count > 2:
            ax.set(xlabel="Time (sec)")

    # showMaximized(plt.get_current_fig_manager())
    fig.subplots_adjust(left=0.09, bottom=0.04, right=0.99, top=0.94, hspace=0.21)
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
    info["fig"].suptitle(annotate_label_with_name(), style="italic")
    if key == UI_BACKWARD_TOUCH_VIEW or key == UI_FORWARD_TOUCH_VIEW:
        info["fig"].suptitle(annotate_label_with_name(f"TOUCH #{info['counter'] + 1}"), style="italic")
    elif key == UI_CALIBRATION_VIEW:
        info["fig"].suptitle(annotate_label_with_name("CALIBRATION"), style="italic")
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


def orient_legend(key: str, info: dict):
    for ax in info["axes"]:
        ax.legend(loc="best")
        if key == UI_BACKWARD_TOUCH_VIEW or key == UI_FORWARD_TOUCH_VIEW:
            ax.legend(loc="upper right")
        elif key == UI_CALIBRATION_VIEW:
            ax.legend(loc="upper left")

def print_fig_as_base64():
    buf = BytesIO()
    plt.gcf().savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")


def on_key_event(event, info: dict):
    if event.key == "f1":
        show_instruction_window()
        return

    if any([x in event.key for x in UI_IGNORE_PRESSES]):
        return

    _ = [func(event.key, info) for func in [update_counter, update_suptitle, scale_axis, orient_legend]]
    plt.draw()


def on_close_event(event):
    for i in plt.get_fignums():
        plt.close(plt.figure(i))


def loop_through_views(fig: plt.Figure, axes: list[plt.Axes]):
    info = {
        "counter": 0,
        "axes": axes,
        "fig": fig,
        "touches": find_touch_indices(),
        "calibration": find_calibration_indices(),
    }
    fig.canvas.mpl_connect("key_press_event", lambda event: on_key_event(event, info))
    fig.canvas.mpl_connect("close_event", on_close_event)


def stack_figures():
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


