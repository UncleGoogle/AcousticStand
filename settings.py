import numpy as np
from matplotlib import style, use, ticker
from matplotlib.figure import Figure

# ------------------------------------GLOBALS to set by user-------------------
FREQUENCY = 10000  # new samples per sec
REFRESH_TIME = 0.5  # sec. ATTENTION! it is time between all func done ther job
# -----------------------------------------------------------------------------
FONT = ('Verdana', 12)
BITS = 16

record_flag = False

fig = Figure(figsize=(5, 5), dpi=100)
# serve as globals with values assign in init():
sample_lines, fft_lines = None, None

def init():
    """initialize the TkAgg backend for gui
    and matplotlib figure with their axes (subplots) and visual settings.
    """
    use('TkAgg')  # matplotlib: set backend
    style.use('seaborn-whitegrid')

    XLIM_FFT = (1, FREQUENCY)
    YLIM_FFT = (0, REFRESH_TIME*FREQUENCY/2 + REFRESH_TIME*FREQUENCY/30)
    XLIM_SAMPLE = (0, FREQUENCY*REFRESH_TIME)
    YLIM_SAMPLE = (0, 3.3)  # 3.3V is signal max voltage

    global fig, sample_lines, fft_lines


    fig.subplots_adjust(bottom=0.15, top=0.92, hspace=.7)
    sample_graph = fig.add_subplot(2, 1, 1,
                                # TODO(low)show always REFRESH_TIME as max value
                                xlabel='samples in {} ms'.format(REFRESH_TIME),
                                ylabel='voltage',
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

    sample_lines = sample_graph.plot([], [], 'g,', [], [], 'r.')
    fft_lines = fft_graph.plot([], [], 'g,', [], [], 'b-')
    # for settings check:
    # http://matplotlib.org/api/lines_api.html#matplotlib.lines.Line2D
    # TIME: microphone1:
    # TODO check which one(if above is right)
    # sample_lines[0].set_linestyle('--')
    # TIME: microphone2:
    sample_lines[1].set_linestyle('-')
    sample_lines[1].set_linewidth(1)
    sample_lines[1].set_marker('')
    # sample_lines[1].set_markersize(0.1)
    # FREQ: microphone1:
    # FREQ: microphone2:
    fft_lines[1].set_linestyle('-')
    fft_lines[1].set_linewidth(1)
    fft_lines[1].set_marker('.')
    fft_lines[1].set_markersize(4)
    fft_lines[1].set_dash_capstyle('projecting')
    fft_lines[1].set_solid_capstyle('projecting')
    # fft_lines[1].set_dash_joinstyle
