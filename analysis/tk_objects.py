import tkinter as tk

from .singleton import Singleton


class InstructionWindowTk(tk.Toplevel):
    def __init__(self, parent=None, *arg, **kwargs):
        super(InstructionWindowTk, self).__init__(*arg, **kwargs)
        self.parent: InstructionWindowSingleton = parent

    def destroy(self) -> None:
        self.parent.is_closed = True
        super(InstructionWindowTk, self).destroy()


class InstructionWindowSingleton(metaclass=Singleton):
    _isclosed: bool = False
    _instruction_text = (
        "press 'c' to show calibration data\n"
        "press '→' to show next reach attempt\n"
        "press '←' to show previous reach attempt\n"
        "press 'ctrl+s' to save view\n"
        "press 'ctrl+f' or 'esc' to toggle fullscreen\n"
        "press 'q' to close all views\n"
        "press any other key to reset view to FULL RANGE\n"
        "press 'F1' to show this instruction\n"
    )

    def __init__(self):
        self.setupUI()

    def raise_(self):
        self.root.attributes("-topmost", True)

    def setupUI(self):
        self.root = InstructionWindowTk(parent=self)
        self.root.minsize(400, 300)
        self.root.maxsize(400, 300)
        self.root.title("Instruction for using EDO Analyzer")

        frame = tk.Frame(self.root, width=400, height=300)
        frame.pack()

        text = tk.Text(frame, wrap="word", borderwidth=0)
        text.place(x=0, y=0, width=400, height=200)
        text.insert("1.0", self._instruction_text)
        text.config(state=tk.DISABLED)
        button = tk.Button(frame, text="OK", command=self.root.destroy)
        button.place(x=0, y=200, width=400, height=100)

        self.root.state("zoomed")

        self.is_closed = False
        # self.raise_()

    @property
    def is_closed(self):
        return self._isclosed

    @is_closed.setter
    def is_closed(self, val: bool):
        self._isclosed = val