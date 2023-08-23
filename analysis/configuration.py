import matplotlib as mpl
import matplotlib.pyplot as plt
import os

mpl.rcParams['backend'] = 'TkAgg'
mpl.rcParams['font.size'] = '8.0'
mpl.rcParams['lines.linewidth'] = 1.0

mpl.rcParams['savefig.directory'] = os.getcwd()

mpl.rcParams['keymap.back'] = []
mpl.rcParams['keymap.copy'] = []
mpl.rcParams['keymap.forward'] = []
mpl.rcParams['keymap.fullscreen'] = ['escape', 'ctrl+f']
mpl.rcParams['keymap.grid'] = []
mpl.rcParams['keymap.grid_minor'] = []
mpl.rcParams['keymap.help'] = []
mpl.rcParams['keymap.home'] = []
mpl.rcParams['keymap.pan'] = []
mpl.rcParams['keymap.quit'] = []
mpl.rcParams['keymap.quit_all'] = ['q']
mpl.rcParams['keymap.save'] = ['ctrl+s']
mpl.rcParams['keymap.xscale'] = []
mpl.rcParams['keymap.yscale'] = []
mpl.rcParams['keymap.zoom'] = []








plt.rcParams['keymap.quit_all'].append('q')

CONFIG = {
    "filename": r"",
    "evaluate_calibration": True,
    "evaluate_exercise": True,
    "export_csv": False,
}


