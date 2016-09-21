import os
import numpy as np
import random
# import scipy.stats as st
# import math
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk  # Pillow
from collections import deque

import pyfftw
from multiprocessing import Process, Queue
from matplotlib import style, use, animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)
use('TkAgg')  # mpl: set backend

BITS = 16
BIG_FONT = ("Verdana", 12)
style.use("seaborn-whitegrid")
# bmh classic dark_background fivethirtyeight ggplot grayscale seaborn-white
# seaborn-bright seaborn-colorblind seaborn-darkgrid seaborn-dark
# seaborn-dark-palette seaborn-deep seaborn-muted seaborn-notebook seaborn-paper
# seaborn-pastel seaborn-poster seaborn-talk seaborn-ticks seaborn-whitegrid

fig = Figure(figsize=(5, 5), dpi=100)
fig.suptitle("FFT of our data", fontsize=14)
subplt1 = fig.add_subplot(121)  # (rows columns plot_no)
subplt2 = fig.add_subplot(122)


def animate(i):
    ''' open data file for reading (develop: and generate sample data)
    perform fft in separate processess and draw plots '''

    # load random quatisized sample (see sample_base.py)
    # TODO move below to initialization function
    with open('sample_base.txt', 'r') as g:
        gData = g.read()
        base_list = gData.split()
        # class my_pdf(st.rv_continuous):
        #     def _pdf(self, x):
        #         return math.sin(x)
        # my_cv = my_pdf(a=0, b=2**BITS, name='sin_pdf')
        # develop:
        with open('sample_data.txt', 'a') as f:
            # generate 100 random samples between each drawing step

            for k in range(60):
                castInt = int(random.gauss(2**BITS/2, 2**BITS/10))  # dev
                if castInt < 0:
                    castInt = 0
                elif castInt > 2**BITS-1:
                    castInt = 2**BITS-1
                f.write(str(base_list[castInt]))
                f.write('\n')
                # f.write(str(2 + math.sin(2*math.pi**k)))

    with open('sample_data.txt', 'r') as f:
        f.seek(0)
        data = deque(f, 1000)  # read and storage the last 100 lines
    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=doFFT, name='fft_1', args=(data, q1))
    p2 = Process(target=doFFT, name='fft_2', args=(data, q2))  # data2
    p1.start()
    p2.start()
    p1.join()  # wait untill process terminate
    p2.join()
    y1 = q1.get()
    y2 = q2.get()

    subplt1.clear()  # break axex tiles :(
    subplt1.plot(y1)
    subplt2.clear()
    subplt2.plot(y2)

    subplt1.set_title("microfon_1", fontsize=12)
    subplt2.set_title("microfon_2: Reference", fontsize=12)

    # matplotlib: axes properties & function TODO:
    # subplt1.relim()
    # update ax.viewLim using the new dataLim
    # subplt1.autoscale_view()


def doFFT(data, queue):
    ''' read data and perform real one dimensional fft
        return the transform magnitude
    '''
    # -version for data = f.read()
    # ypl = []
    # lines = data.split('\n')
    # for line in lines:
    #    if len(line) > 1:
    #         ypl.appeetup="import pyfftw; \

    # -version for numpy fft and deque:
    # ft = np.fft.fft(data)
    # yar = asarray(ft, dtype=np.float16)
    # queue.put(yar)

    # -vesion for pyfftw and deque:
    # initialize empty output array (real -> complex fft)
    x = np.asarray(data, dtype=np.float32)
    input = pyfftw.empty_aligned(x.shape[0], dtype=np.float32)
    ft = pyfftw.empty_aligned(x.shape[0]//2+1, dtype=np.complex64)
    fft_obj = pyfftw.FFTW(input, ft)
    input[:] = x
    fft_obj()  # __init__ has update_arrays(in, out) and execute()

    magnitude = np.abs(ft)
    queue.put(magnitude)


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

        defaultbg = self.cget('bg')  # self -> from AcousticStand class
        fig.set_facecolor(defaultbg)

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


def main():
    app = AcousticStand()
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    ani.interval = 1001
    app.mainloop()

if __name__ == "__main__":
    main()
