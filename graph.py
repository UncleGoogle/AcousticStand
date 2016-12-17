import os
import sys
import random
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk
from time import localtime, strftime
from pathlib import PurePath
from multiprocessing import Process, Queue

sys.path.append('/usr/local/lib/')  # to find proper original fftw on RaspPi
# TODO append syspath outside the program:
# add to ~/.profile file: export PYTHONPATH=$PYTHONPATH:/path/you/want/to/add
import pyfftw
import numpy as np
# from PIL import ImageTk

import settings
from my_animation import FuncAnimation
from gui import AcousticStand
import gui


# develop:
# global base_list, plot_data
base_list = []
plot_data = np.empty([3, int(settings.FREQUENCY*settings.REFRESH_TIME)],
                     dtype=np.float32)

def init():
    ''' Initializtion function to animate refreshing only fft_lines
    develop: load random quatisized sample (see sample_base.py)

    --> data structure:
    figure_data is list of four Artists -> Line2D that will be plotting:
    (samples and fft) for each microphone (measurement and reference).
    So figure_data = [Line2DArtist]*4;
    each Line2DArtist contains: (x[],y[]);
    we need get_data() method to unpack that.
    '''
    global base_list
    with open('sample_base.txt', 'r') as g:
        gData = g.read()
        base_list = gData.split()
    for i in range(2):
        settings.sample_lines[i].set_data([], [])
        settings.fft_lines[i].set_data([], [])
    figure_data = settings.sample_lines + settings.fft_lines
    # TODO: if you want write data in separate process:
    # settings.record_flag = False
    return figure_data


def animate(i):
    ''' develop: generate sample data and pug it in Line2D ([x1,y1],[x2,y2]) tup
    Perform fft in separate processess and draw plots.
    Perform data recording on demand (record_flag).
    '''
    # random data
    global plot_data
    for k in range(int(settings.FREQUENCY*settings.REFRESH_TIME)):
        randInt = random.randint(0, 2**settings.BITS)
        plot_data[0, k] = (base_list[randInt-1])
        plot_data[2, k] = k  # x axes values

    # some sin data
    t = np.arange(0, settings.REFRESH_TIME, 1/settings.FREQUENCY,
                  dtype=np.float32)
    x = 1.6 + np.sin(np.pi*520*t) + 0.9*np.sin(200*np.pi*t) + \
        0.5*np.cos(np.pi*500*t)

    # TODO ** develop: initialize below to show nothing as default
    settings.sample_lines[0].set_data(plot_data[2], plot_data[0])
    settings.sample_lines[1].set_data([np.float32(i) for i in range(len(x))], x)

    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=do_fft, name='fft_1', args=(plot_data[0], q1))
    p2 = Process(target=do_fft, name='fft_2', args=(x, q2))
    p1.start()
    p2.start()
    p1.join()  # wait untill process terminate
    p2.join()
    # TODO like todo **
    settings.fft_lines[0].set_data(q1.get())
    settings.fft_lines[1].set_data(q2.get())
    figure_data = settings.sample_lines + settings.fft_lines

    data_file_name = strftime("AC_%d.%m.%Y_%H-%M-%S", localtime())
    if settings.record_flag:
        p3 = Process(target=record_data, name='writer',
                     args=(data_file_name, figure_data))
        p3.start()

    # returning figure_data actualize the iterable artist every step of anima.
    return figure_data


def do_fft(data, queue):
    ''' Read data and perform real one-dimensional fft.
    Returns the tuple consist of transform magnitude and frequency vector.
    '''
    x = np.asarray(data, dtype=np.float32)
    # float16 would be enough but isn't available under Raspbarian OS.

    # initialize empty in/out-put arrays (real -> complex fft)
    input = pyfftw.empty_aligned(x.shape[0], dtype=np.float32)
    output = pyfftw.empty_aligned(x.shape[0]//2+1, dtype=np.complex64)
    fft_obj = pyfftw.FFTW(input, output)  # creating object clean its arrays

    input[:] = x  # assign
    fft_obj()  # __call__ has methods: update_arrays(in, out) and execute()

    magnitude = np.abs(output)

    # Frequency vector associated with the output signal sampled in freq. space.
    freq = pyfftw.empty_aligned(output.shape[0], dtype=np.float32)
    olen = len(output)
    for i in range(olen):
        freq[i] = i*settings.FREQUENCY/olen

    queue.put((freq, magnitude))


def record_data(filename, data):
    '''Write drawing data (samples and fft)
    activate using record_flag boolean
    '''
    row_data = []
    #  --> 'unzip' data
    for line2D in data:  # len(data)=4
        tups = line2D.get_data()
        for i in range(len(tups)):  # len(tups)=2
            row_data.append(tups[i])
    #  --> pad row_data with nothing, to obtain equall lists
    longest_l = len(max(row_data, key=lambda l: len(l)))
    for i in range(len(row_data)):
        current_l = len(row_data[i])
        if current_l < longest_l:
            row_data[i] = np.lib.pad(row_data[i], (0, longest_l - current_l),
                                     'constant', constant_values=np.nan)
    array_data = np.array(row_data, dtype=np.float32)

    filename = filename + '.CSV'
    path = str(PurePath('data', filename))
    try:
        f = open(path, 'x')
    except FileExistsError:
        filename += '_n'
        path = str(PurePath('data', filename))
    else:
        with f:
            #  --> write to file using slicing (writing row by row all columns)
            f.write("X\tY\tref_X\tref_Y\tfft_X\tfft_Y\tref_fft_X\tref_fft_Y\n")
            for item in range(len(array_data[0])):
                f.write('\t'.join(map(str, array_data[:, item])))
                f.write('\n')


def main():
    initial_popup = gui.Popup_settings()
    initial_popup.mainloop()

    settings.init()

    app = AcousticStand()
    ani = FuncAnimation(settings.fig, animate, init_func=init,
                        interval=settings.REFRESH_TIME*1000, blit=True)
    ani.blit = True

    # TODO make gui independent on refresh time (another process/thread
    # handles gui response)
    app.mainloop()

if __name__ == "__main__":
    main()
