import os
import numpy as np
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk  # for png, jpg ect support
from random import uniform

import matplotlib
matplotlib.use('TkAgg')  # set backend - next time use your own window
# from pyFFTW import fft # TODO the best fft is fftw based on C
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.animation as animation


BIG_FONT = ("Verdana", 12)
style.use("seaborn-whitegrid")
# bmh classic dark_background fivethirtyeight ggplot grayscale seaborn-white
# seaborn-bright seaborn-colorblind seaborn-darkgrid seaborn-dark
# seaborn-dark-palette seaborn-deep seaborn-muted seaborn-notebook seaborn-paper
# seaborn-pastel seaborn-poster seaborn-talk seaborn-ticks seaborn-whitegrid

fig = Figure(figsize=(5, 5), dpi=100)
fig.suptitle("FFT of out data", fontsize=14)
subplt1 = fig.add_subplot(121)  # (rows, columns, plot_no)
subplt1.set_title("Real part", fontsize=12)

# defaultbg = self.cget('bg')
# fig = Figure(figsize=(5, 5), dpi=100, facecolor=defaultbg)
# fig.facecolor = defaultbg
# subplt2 = fig.add_subplot(122)
# subplt2 = fig.add_axes([0.58, 0.2, 0.4, 0.65])  # [left, bottom, w, h]
# subplt2.plot(np.imag(ft), color='green')
# subplt2.set_title("Imaginary part", fontsize=12)


def animate(i):

    # data = self.generate_data()
    # ft = np.fft.fft(data)
    # subplt1.plot(np.real(ft))

    # open a file for reading and then appendding (for develop purpose)
    f = open('sample_data.txt', 'r+')
    data = f.read()
    lines = data.split('\n')
    xpl = []
    ypl = []
    i = 0
    for line in lines:
        if len(line) > 1:
            ypl.append(line)
            xpl.append(i)
            i += 1
    ft = np.fft.fft(ypl)
    subplt1.clear()
    subplt1.plot(xpl, ft)

    f.write(str(uniform(0, 3.3)))
    f.write('\n')
    f.seek(0)  # set pointer to te start of file
    f.close()


class AcousticStand(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        if os.name == "nt":  # windows
            self.iconbitmap("AcousticStand.ico")  # check. If not try default=.
        else:
            # line below calls similar func like last line here
            self.iconbitmap("@AcS.xbm")  # b&white; overwrite below
            icon = tk.PhotoImage(file='AcousticStand.gif')  # .gif colo64
            self.tk.call('wm', 'iconphoto', self._w, icon)

        self.title("AcousticStand alpha")  # like: tk.Tk.wm_title(self, "title")
        self.geometry("700x500")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container["borderwidth"] = 2
        container["relief"] = "sunken"  # "raised" "solid" "ridge""groove"

        self.frames = {}  # make list of my frames

        for fr in (StartPage, GraphPage):
            frame = fr(container, self)
            self.frames[fr] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame(GraphPage)  # initial show

    def show_frame(self, control):
        frame = self.frames[control]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Start Joda Page", font=BIG_FONT)
        label.pack(padx=10, pady=10)
        # now, lets display a image&text inside label TODO doesn't work
        joda = ImageTk.PhotoImage(file="jodapng.png")
        label["image"] = joda
        label["compound"] = "top"  # posision of image against text

        # # make a variable label
        # resultsContents = tk.StringVar()
        # label["textvariable"] = resultsContents
        # resultsContents.set("Joda updated become")

        button1 = ttk.Button(
            self, text="show GraphPage",
            command=lambda: controller.show_frame(GraphPage))
        button1.pack()


class GraphPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page", font=BIG_FONT)
        label.pack(pady=10, padx=10)

        button_home = ttk.Button(
            self, text="Back to Home",
            command=lambda: controller.show_frame(StartPage))
        button_home.pack(side=tk.BOTTOM)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM)  # unwanted effect

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # def generate_data(self):
        # # generate random data
        # data = []
        # for i in range(10):
            # data.append(random())
        # return data


def main():
    app = AcousticStand()
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    ani.interval = 1200
    app.mainloop()

if __name__ == "__main__":
    main()
