import os
import numpy as np
import random
import tkinter as tk
from tkinter import ttk
from time import gmtime, strftime
from pathlib import PurePath

#  from PIL import ImageTk
#  from collections import deque

import pyfftw
from multiprocessing import Process, Queue
from matplotlib import style, use, animation, ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)

#  -----------------------------------GLOBALS----------------------------------
BITS = 16
FREQUENCY = 10000  # of new samples per sec
REFRESH_TIME = 1  # 1s
XLIM_FFT = (1, FREQUENCY)
YLIM_FFT = (0, FREQUENCY/2 + FREQUENCY/30)
XLIM_SAMPLE = (0, FREQUENCY*REFRESH_TIME)
YLIM_SAMPLE = (0, 3.3)  # 3.3V signal max voltage
RECORD_FLAG = False
FONT = ('Verdana', 12)
# TODO:
# root of style (.)
    #  s = ttk.Style()
    #  s.configure('.', font=('Helvetica', 12))
#  -----------------------------------VISUAL SETTINGS--------------------------

use('TkAgg')  # mpl: set backend
style.use('seaborn-whitegrid')
# bmh classic dark_background fivethirtyeight ggplot grayscale seaborn-white
# seaborn-bright seaborn-colorblind seaborn-darkgrid seaborn-dark
# seaborn-dark-palette seaborn-deep seaborn-muted seaborn-notebook seaborn-paper
# seaborn-pastel seaborn-poster seaborn-talk seaborn-ticks seaborn-whitegrid

fig = Figure(figsize=(5, 5), dpi=100)
fig.subplots_adjust(bottom=0.15, top=0.92, hspace=.7)

sample_graph = fig.add_subplot(2, 1, 1,
                               xlabel='time [ms]', ylabel='voltage',
                               xlim=XLIM_SAMPLE, ylim=YLIM_SAMPLE)
sample_graph.set_title('time domain', fontsize=13)

fft_graph = fig.add_subplot(2, 1, 2,
                            xlabel='frequency [Hz]', ylabel='FT magnitude',
                            xlim=XLIM_FFT, ylim=YLIM_FFT, xscale='log')
fft_graph.set_title('frequency domain', fontsize=13)
fft_graph.xaxis.grid(True, which='major', linewidth=0.7, color='0.5')
fft_graph.xaxis.grid(which='minor', linestyle='-', color='0.5')
fft_graph.yaxis.grid(which='major', color='0.7')
subs = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]  # ticks to show per decade
fft_graph.xaxis.set_minor_locator(ticker.LogLocator(subs=subs))
fft_graph.xaxis.set_major_formatter(ticker.LogFormatterMathtext(base=10.0,
                                    labelOnlyBase=False))
sample_lines = sample_graph.plot([], [], 'g,', [], [], 'r-')
fft_lines = fft_graph.plot([], [], 'g,', [], [], 'r-')

base_list = []  # develop: to storage data from init (file)
plot_data = np.empty([3, FREQUENCY*REFRESH_TIME], np.float32)


class AcousticStand(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        if os.name == "nt":  # windows
            self.iconbitmap("AcousticStand.ico")  # check. If not try default=.
        else:
            pass
            # line below calls similar func like last line here
            #  self.iconbitmap("@AcS.xbm")  # b&white; overwrite below
            #  icon = tk.PhotoImage(file='AcousticStand.gif')  # .gif colo64
            #  self.tk.call('wm', 'iconphoto', self._w, icon)  # TODO: activate

        self.title("AcousticStand alpha")  # like: tk.Tk.wm_title(self, "title")
        self.geometry("1400x900")
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
        label = ttk.Label(self, text="Start Joda Page", font=FONT)
        label.pack(padx=10, pady=10)
        # now, lets display a image&text inside label TODO doesn't work
        #  joda = ImageTk.PhotoImage(file="jodapng.png")
        #  label["image"] = joda
        #  label["compound"] = "top"  # posision of image against text

        button1 = ttk.Button(
            self, text="show GraphPage",
            command=lambda: controller.show_frame(GraphPage))
        button1.pack()


class GraphPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page", font=FONT)
        label.pack(pady=10, padx=10)

        defaultbg = self.cget('bg')  # self -> from AcousticStand class
        fig.set_facecolor(defaultbg)

        #  button_home = ttk.Button(
            #  self, text="Back to Home",
            #  command=lambda: controller.show_frame(StartPage))
        #  button_home.pack(side=tk.BOTTOM)

        ttk_style = ttk.Style()
        ttk_style.map('Mine.TButton'
                      , relief=[('pressed', 'flat')]
                      , background=[('pressed', '#ffebcd')]
                      , foreground=[('active', 'red')]
                      )

        self.button_record = ttk.Button(self, width=14, text='Record data',
                                        style='Mine.TButton',
                                        command=lambda: self.record_data())
        self.button_record.pack(side=tk.BOTTOM)

        # TODO try place here most of the code from the beggining (except fig)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM)  # unwanted effect

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def record_data(self):
        ''' toogle recording data to file
        '''
        global RECORD_FLAG
        if not RECORD_FLAG:
            RECORD_FLAG = True
            self.button_record.state(('pressed',))
            self.button_record['text'] = 'Recording...'

        else:
            RECORD_FLAG = False
            self.button_record['text'] = 'Record data'


class MyFuncAnimation(animation.FuncAnimation):
    '''
    Unfortunately, it seems that the _blit_clear method of the Animation
    class contains an error in several matplotlib verions
    That's why, I fork it here and insert the latest git version of
    the function. '''

    def _blit_clear(self, artists, bg_cache):
        # Get a list of the axes that need clearing from the artists that
        # have been drawn. Grab the appropriate saved background from the
        # cache and restore.
        axes = set(a.axes for a in artists)
        for a in axes:
            if a in bg_cache:  # this is the previously missing line
                a.figure.canvas.restore_region(bg_cache[a])


def init():
    ''' Initializtion function to animate refreshing only fft_lines
    develop: load random quatisized sample (see sample_base.py)
    '''
    global base_list
    with open('sample_base.txt', 'r') as g:
        gData = g.read()
        base_list = gData.split()
    for i in range(2):
        sample_lines[i].set_data([], [])
        fft_lines[i].set_data([], [])
    figure_data = sample_lines + fft_lines
    return figure_data


def animate(i):
    ''' develop: generate sample data and pug it in Line2D ([x1,y1],[x2,y2]) tup
    Perform fft in separate processess and draw plots.
    '''

    # random data
    global plot_data
    for k in range(FREQUENCY*REFRESH_TIME):
        randInt = random.randint(0, 2**BITS)
        plot_data[0, k] = (base_list[randInt-1])
        plot_data[2, k] = k  # x axes values

    # some sin data
    t = np.arange(0, REFRESH_TIME, 1/FREQUENCY, dtype=np.float32)
    x = np.sin(2*np.pi*150*t) + np.sin(2*np.pi*100*t)

    sample_lines[0].set_data(plot_data[2], plot_data[0])
    sample_lines[1].set_data([i for i in range(len(x))], x)

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=do_fft, name='fft_1', args=(plot_data[0], q1))
    p2 = Process(target=do_fft, name='fft_2', args=(x, q2))
    p1.start()
    p2.start()
    p1.join()  # wait untill process terminate
    p2.join()
    fft_lines[0].set_data(q1.get())
    fft_lines[1].set_data(q2.get())
    figure_data = sample_lines + fft_lines

    # TODO in nicer format
    data_file_name = strftime("%d.%m.%Y %H-%M-%S", gmtime())
    if RECORD_FLAG:
        p3 = Process(target=write_data, name='writer',
                     args=(data_file_name, figure_data))
        p3.start()

    # actualize the iterable artist every step of animation
    return figure_data


def do_fft(data, queue):
    '''
    Read data and perform real one dimensional fft.
    Returns the tuple of transform magnitude and frequency vector.
    '''
    x = np.asarray(data, dtype=np.float32)  # float16 is enough but not availab.

    # initialize empty in/out-put arrays (real -> complex fft)
    input = pyfftw.empty_aligned(x.shape[0], dtype=np.float32)
    output = pyfftw.empty_aligned(x.shape[0]//2+1, dtype=np.complex64)
    fft_obj = pyfftw.FFTW(input, output)  # creating object clean its arrays

    input[:] = x  # assign
    fft_obj()  # __init__ has update_arrays(in, out) and execute()

    magnitude = np.abs(output)

    # Frequency vector associated with the output signal sampled in freq. space.
    freq = pyfftw.empty_aligned(output.shape[0], dtype=np.float32)
    olen = len(output)
    for i in range(olen):
        freq[i] = i*FREQUENCY/olen

    queue.put((freq, magnitude))


def write_data(filename, data, state=True):
    '''write drawing data (samples and fft)
    stop record data if state=False
    '''
    path = str(PurePath('data', filename))
    with open(path, 'x') as f:
        number = 0
        for line2D in data:
            number += 1
            f.write('\n\nPlot_line no: {} \n'.format(number))
            data2D = line2D.get_data()
            f.write('x axis now \n')
            for i in data2D[0]:
                f.write("".join((str(i), '\n')))
            f.write('y axis now \n')
            for i in data2D[1]:
                f.write("".join((str(i), '\n')))


def main():
    app = AcousticStand()
    ani = MyFuncAnimation(fig, animate, init_func=init,
                          interval=REFRESH_TIME*1000, blit=True)
    ani.interval = 1001
    app.mainloop()

if __name__ == "__main__":
    main()
