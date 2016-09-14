import os
import io
import tkinter as tk
from tkinter import ttk
import numpy as np

from PIL import ImageTk  # for png, jpg ect support
from random import randrange

from multiprocessing import Process, Queue
import matplotlib
matplotlib.use('TkAgg')  # set backend
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)

BITS = 16
BIG_FONT = ("Verdana", 12)
style.use("seaborn-whitegrid")
# bmh classic dark_background fivethirtyeight ggplot grayscale seaborn-white
# seaborn-bright seaborn-colorblind seaborn-darkgrid seaborn-dark
# seaborn-dark-palette seaborn-deep seaborn-muted seaborn-notebook seaborn-paper
# seaborn-pastel seaborn-poster seaborn-talk seaborn-ticks seaborn-whitegrid

fig = Figure(figsize=(5, 5), dpi=100)
fig.suptitle("FFT of out data", fontsize=14)
subplt1 = fig.add_subplot(121)  # (rows, columns, plot_no)
subplt1.set_title("microfon_1", fontsize=12)
subplt2 = fig.add_subplot(122)
subplt2.set_title("microfon_2: Reference", fontsize=12)

# defaultbg = self.cget('bg')
# fig = Figure(figsize=(5, 5), dpi=100, facecolor=defaultbg)
# subplt2 = fig.add_axes([0.58, 0.2, 0.4, 0.65])  # [left, bottom, w, h]
# subplt2.plot(np.imag(ft), color='green')


def animate(i):
    ''' open data file for reading (develop: and generate sample data)
    perform fft in separate processess and draw plots '''

    # load random quatisized sample (see sample_base.py)
    # TODO move below to initialization function
    with open('sample_base.txt', 'r') as g:
        gData = g.read()
        base_list = gData.split()

    with open('sample_data.txt', 'a+') as f:  # final ver: 'r'
        # generate 100 random samples between each drawing step
        for k in range(10):
            castInt = randrange(0, 2**BITS)
            f.write(str(base_list[castInt]))
            f.write('\n')
        try:
            f.seek(-500, 2)  # last x bites
        except io.UnsupportedOperation:
            f.seek(0, 0)  # set pointer to the begging of the file
        data = f.read()

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=doFFT, name='fft_1', args=(data, q1))
    p2 = Process(target=doFFT, name='fft_2', args=(data, q2))  # data2
    p1.start()
    p2.start()
    p1.join()  # wait untill process terminate
    p2.join()

    x1, y1, x2, y2 = ([], [], [], [])
    # maybe make numpy.array if they will be big - for efficiency TODO
    x1, y1 = q1.get()
    x2, y2 = q2.get()
    subplt1.clear()
    subplt1.plot(x1, y1)
    subplt2.clear()
    subplt2.plot(x2, y2)


def doFFT(data, queue):
    ''' read data and perform fft '''
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
    queue.put((xpl, ft))


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


def main():
    app = AcousticStand()
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    ani.interval = 1001
    app.mainloop()

if __name__ == "__main__":
    main()
