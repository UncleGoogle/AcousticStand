import os
import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2TkAgg)

import settings

class Popup(tk.Tk):
    """Create popup window for different purposes.
    Additional kwargs: width=300, haigh=120.

    To show warning or info window use rather tk.messagebox.
    """
    def __init__(self, *args, **kwargs):
        w = kwargs.pop('width', None)
        h = kwargs.pop('height', None)
        tk.Tk.__init__(self, *args, **kwargs)
        if not w:
            w = self.winfo_reqwidth() + 20
        if not h:
            h = self.winfo_reqheight() - 60
        self.set_centrally(w, h)


    def set_centrally(self, w, h):
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry('{}x{}+{}+{}'.format(w, h, x, y))


class Popup_settings(Popup):
    """Show small window that allow to change some settings"""
    def __init__(self, *args, **kwargs):
        Popup.__init__(self, *args, **kwargs)

        self.set_widgets()

        if settings.REFRESH_TIME == 0:
            tk.messagebox.showerror("Error 101",
                                "Set REFRESH_TIME>0")
            sys.exit(1)
        if settings.REFRESH_TIME*settings.FREQUENCY > 16300:  # TODO check for Raspb.Pi3
            tk.messagebox.showerror("Error 102",
                                "Too big amount of data in sample. Set \
                                FREQUENCY*REFRESH_TIME less than 16300")
            sys.exit("Stack overflow")


    def submit(self):
        settings.FREQUENCY = self.freq.get()
        settings.REFRESH_TIME = self.refr_time.get()
        self.destroy()



    def set_widgets(self):
        self.wm_title("Initial settings")  # the same like .title

        self.freq = tk.IntVar()
        self.freq.set(10000)
        self.refr_time = tk.DoubleVar()
        self.refr_time.set(0.5)
        PADY = 5
        PADX = 5

        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="both", expand=False)

        middle_frame = tk.Frame(self)
        middle_frame.pack(side="top", fill="both", expand=True)

        bottom_frame = tk.Frame(self)#, background="green")
        bottom_frame.pack(side="bottom", fill="both", expand=False)

        tip = ttk.Label(top_frame, width=40, anchor='c',
                        text="Next: <Tab>, Press: <Space>")
        tip.pack(side="top", pady=PADY)

        labels_frame = tk.Frame(middle_frame)#, background='red')
        labels_frame.pack(side="left", fill="both", expand=True, padx=PADX)
        freq_label = ttk.Label(labels_frame, text="frequency [Hz]:")
        freq_label.pack(side="top", anchor="e", pady=PADY)
        time_label = ttk.Label(labels_frame, text="refresh time [s]:")
        time_label.pack(side="top", anchor="e", pady=PADY)

        entries_frame = tk.Frame(middle_frame)#, background='blue')
        entries_frame.pack(side="right", fill="both", expand=True, padx=PADX)
        freq_entry = ttk.Entry(entries_frame, textvariable=self.freq, width=6)
        freq_entry.pack(side="top", anchor="w", pady=PADY)
        time_entry = ttk.Entry(entries_frame, textvariable=self.refr_time, width=6)
        time_entry.pack(side="top", anchor="w", pady=PADY)

        submit_btn = ttk.Button(bottom_frame, text="OK", width=10,
                                command = self.submit)
        submit_btn.pack(side="bottom", pady=PADY)


class AcousticStand(tk.Tk):
    ''' Mother class that keeps app overall settings and all frames to show
    '''
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        if os.name == "nt":  # windows
            self.iconbitmap("AcousticStand.ico")
        else:
            # TODO: create transparent icon
            icon = tk.PhotoImage(file='AcousticStand.gif')  # .gif colo64
            self.tk.call('wm', 'iconphoto', self._w, icon)

        self.title("AcousticStand alpha")  # like: tk.Tk.wm_title(self, "title")
        self.geometry("1400x900")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container["borderwidth"] = 2
        container["relief"] = "sunken"  # "raised" "solid" "ridge""groove"

        self.frames = {}  # make list of all frames
        for fr in (GraphPage, InfoPage):
            frame = fr(container, self)
            self.frames[fr] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame(GraphPage)  # initial show
        # popup_settings(self)  # settings at the very beggining

    def show_frame(self, control):
        frame = self.frames[control]
        frame.tkraise()
        frame.focus_set()


class GraphPage(tk.Frame):
    ''' Page in which canvas is drawn: sample graph and fft graph are shown.
    '''
    def __init__(self, parent, controller, figure=settings.fig):

        tk.Frame.__init__(self, parent)
        defaultbg = self.cget('bg')  # self -> from AcousticStand class
        figure.set_facecolor(defaultbg)

        # highlightborder doesn't work because of bugs/incopletions in ttk.
        # there are wrappers for this (from tk) but... bez przesady
        ttk_style = ttk.Style()
        ttk_style.configure('Mine.TButton',
                            highlightthickness=1,  # doesn't work
                            )
        ttk_style.map('Mine.TButton',
                      relief=[('pressed', 'sunken'),
                              ('!pressed', 'raised')],
                      background=[('pressed', '#ffebcd')],
                      foreground=[('active', 'green'),  # by mouse
                                  ('focus','green')],  # by keyboard
                      )

        canvas = FigureCanvasTkAgg(figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side="bottom")

        button_home = ttk.Button(
            self, text="About the project", width=14, takefocus=1,
            style='Mine.TButton',
            command=lambda: controller.show_frame(InfoPage))
        button_home.pack(side="left")

        self.button_record = ttk.Button(self, width=14, text='Record data',
                                        style='Mine.TButton',
                                        command=lambda: self.call_record())
        self.button_record.pack(side="left")

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side="bottom", fill="both", expand=True)

    def call_record(self):
        ''' toogle recording data to file
        '''
        if not settings.record_flag:
            settings.record_flag = True
            self.button_record.state(('pressed',))
            self.button_record['text'] = 'Recording...'

        else:
            settings.record_flag = False
            self.button_record.state(('!pressed',))
            self.button_record['text'] = 'Record data'

class InfoPage(tk.Frame):
    ''' Page with official information about the project
    '''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="""
Aplikacja jest częścią projektu współfinansowanego ze środków Grantu Rektora \
Politechniki Warszawskiej.

temat projektu: Budowa stanowiska do analizy widma sygnałów \
akustycznych o możliwej aplikacji w analizie mowy.
kierownik grantu: dr hab. inż. Michał Urbański, prof. PW

Koło Naukowe Muzyka i Akustyka 2016
""",
                          # członkowie zespołu:
                          # Mieszko Bańczerowski
                          # Łukasz Majewski
                          # Łukasz Krauze
                          # Łukasz Kołodziejczak
                          # Aleksander Szpakiewicz-Szatan
                          # czy oni muszą wyrazić zgodę na wypisanie nazwisk?

# Grant of the Warsaw University of Technology Rector. Edition 2016.
# The grant laureate is Music and Acoustic Student Assossiation.

# subject: Set up/build of the stand for freq?... signals analysis
# leader: dr hab. inż. Michał Urbański, prof. WUT
#                           TODO english

#                           <logo pw TODO>
# http://www.promocja.pw.edu.pl/Dokumenty/Logo-Politechniki-Warszawskiej
# © ?

                          font=settings.FONT,
                          justify=tk.CENTER)
        label.pack(padx=10, pady=10)

        back_btn = ttk.Button(
            self, text="Back",
            command=lambda: controller.show_frame(GraphPage))
        back_btn.focus_set()
        back_btn.pack()
