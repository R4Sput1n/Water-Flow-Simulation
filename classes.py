# All classes will be here
import math as m
import tkinter as tk
from tkinter import ttk
import statistics
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import data
import pygame
matplotlib.use("TkAgg")


class SingleInputTank:
    def __init__(self, tank_num, h_0, area, h_max, h_min=0, dt=0.1):
        self.save_file = None
        self.tank_num = tank_num
        self.h = h_0
        self.A = area
        self.h_max = h_max
        self.h_min = h_min
        self.time = 0
        self.dt = dt
        self.q_out = 0
        self.time_list = []
        self.h_list = []

    def __str__(self):
        return f'After t = {round(self.time, 2)} fluid height in tank {self.tank_num} is h = {round(self.h, 3)}'

    def calc_increase(self, q,  kv):
        self.q_out = kv * m.sqrt(self.h)
        return (q - self.q_out) / self.A

    def limits(self):
        if self.h < self.h_min:
            self.h = self.h_min
        if self.h > self.h_max:
            self.h = self.h_max

    def iteration(self, q, kv, file):
        self.changes_over_time(file)
        increase = self.calc_increase(q, kv)
        self.h = increase * self.dt + self.h
        self.time += self.dt
        self.limits()

    def changes_over_time(self, file):
        self.h_list.append(self.h)
        self.time_list.append(self.time)
        self.save_file = open(file, 'a')
        self.save_file.write(f'{self.time},{self.h}\n')


left_upper_tank = SingleInputTank(tank_num=1, h_0=0, area=(data.LU_LENGTH * data.LU_WIDTH), h_max=data.LU_HEIGHT * 10)
right_upper_tank = SingleInputTank(tank_num=2, h_0=0, area=(data.RU_LENGTH * data.RU_WIDTH), h_max=data.RU_HEIGHT * 10)
lower_tank = SingleInputTank(tank_num=3, h_0=0, area=(data.B_LENGTH * data.B_WIDTH), h_max=data.B_HEIGHT * 10)


class Util:
    def __init__(self):
        self.l_valve_btn = None
        self.r_valve_btn = None
        self.sim_btn = None

    def switch_left_valve(self, Q, root):
        if Q:
            self.l_valve_btn['text'] = 'OFF'
            root.Ql = False
        else:
            self.l_valve_btn['text'] = 'ON'
            root.Ql = True

    def switch_right_valve(self, Q, root):
        if Q:
            self.r_valve_btn['text'] = 'OFF'
            root.Qr = False
        else:
            self.r_valve_btn['text'] = 'ON'
            root.Qr = True

    def start_stop_btn(self, sim_status, root):
        if sim_status:
            self.sim_btn['text'] = 'START'
            root.start_stop_sim()
        else:
            self.sim_btn['text'] = 'STOP'
            root.start_stop_sim()


class SubInfoWidget(tk.Frame):
    def __init__(self, parent, h_variable, starting_row, starting_col, title):
        super().__init__(parent)

        if title == 'Left Upper Tank':
            leng = data.LU_LENGTH
            wid = data.LU_WIDTH
        elif title == 'Right Upper Tank':
            leng = data.RU_LENGTH
            wid = data.RU_WIDTH
        else:
            leng = data.B_LENGTH
            wid = data.B_WIDTH
        # Left upper tank info
        left_label = ttk.Label(parent, text=title, font='Roboto 10 bold')
        left_label.grid(column=starting_col, row=starting_row + 1, columnspan=2, sticky='WE', padx=5, pady=10)

        length_label = ttk.Label(parent, text='Length:')
        length_label.grid(column=starting_col, row=starting_row + 2, sticky='W', padx=3)
        length_text = ttk.Label(parent, text=leng)
        length_text.grid(column=starting_col + 1, row=starting_row + 2, sticky='W', padx=3)

        width_label = ttk.Label(parent, text='Width:')
        width_label.grid(column=starting_col, row=starting_row + 3, sticky='W', padx=3)
        width_text = ttk.Label(parent, text=wid)
        width_text.grid(column=starting_col + 1, row=starting_row + 3, sticky='W', padx=3)

        area_label = ttk.Label(parent, text='Area:')
        area_label.grid(column=starting_col, row=starting_row + 4, sticky='W', padx=3)
        area_text = ttk.Label(parent, text=leng * wid)
        area_text.grid(column=starting_col + 1, row=starting_row + 4, sticky='W', padx=3)

        height_label = ttk.Label(parent, text='Current height:')
        height_label.grid(column=starting_col, row=starting_row + 5, sticky='W', padx=3)

        var_frame = tk.Frame(parent, width=30, height=18)
        var_frame.grid(column=starting_col + 1, row=starting_row + 5, sticky='W', padx=3)
        height_label_var = ttk.Label(var_frame, textvariable=h_variable)
        height_label_var.grid(column=0, row=0)
        var_frame.grid_propagate(False)


class InformationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        for col in range(4):
            self.grid_columnconfigure(col, weight=1)
        self.grid_rowconfigure(6, weight=1)
        win_name_frame = tk.Frame(self, width=500, height=28, background='white')
        win_name_frame.grid(column=0, row=0, columnspan=6, sticky='WE')
        win_name_frame.grid_propagate(False)
        page_label = tk.Label(self, text='Information', font=data.LARGE_FONT)
        page_label.grid(column=0, row=0, sticky='EW', columnspan=6)

        SubInfoWidget(self, controller.hl, 0, 0, 'Left Upper Tank')
        SubInfoWidget(self, controller.hr, 0, 2, 'Right Upper Tank')
        SubInfoWidget(self, controller.hb, 0, 4, 'Bottom Tank')

        button1 = ttk.Button(self, text='Next Page', command=lambda: controller.show_frame(Model))
        button1.grid(column=4, row=7, sticky='SE')


class Graph(tk.Frame, Util):
    def __init__(self, parent, controller):
        super().__init__(parent)

        for col in range(4):
            if col == 1:
                self.grid_columnconfigure(col, weight=1)
            else:
                self.grid_columnconfigure(col, weight=2)

        label = tk.Label(self, text='Graph', font=data.LARGE_FONT)
        label.grid(column=0, row=0, columnspan=4, sticky='WE')

        canvas = FigureCanvasTkAgg(data.fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=1, columnspan=4)

        left_tank_lbl = ttk.Label(self, text='Left upper tank')
        left_tank_lbl.grid(column=0, row=2)
        left_tank_kv_lbl = ttk.Label(self, text='kv:')
        left_tank_kv_lbl.grid(column=1, row=2, sticky='E', padx=3)
        self.l_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', variable=controller.l_kv)
        self.l_slider.grid(column=2, row=2, sticky='W')
        self.l_valve_btn = ttk.Button(self, text='ON',
                                      command=lambda: self.switch_left_valve(controller.Ql, controller))
        self.l_valve_btn.grid(column=3, row=2, sticky='W')

        right_tank_lbl = ttk.Label(self, text='Right upper tank')
        right_tank_lbl.grid(column=0, row=3)
        right_tank_kv_lbl = ttk.Label(self, text='kv:')
        right_tank_kv_lbl.grid(column=1, row=3, sticky='E', padx=3)
        self.r_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', variable=controller.r_kv)
        self.r_slider.grid(column=2, row=3, sticky='W')
        self.r_valve_btn = ttk.Button(self, text='ON',
                                      command=lambda: self.switch_right_valve(controller.Qr, controller))
        self.r_valve_btn.grid(column=3, row=3, sticky='W')

        bottom_tank_lbl = ttk.Label(self, text='Bottom tank')
        bottom_tank_lbl.grid(column=0, row=4)
        bottom_tank_kv_lbl = ttk.Label(self, text='kv:')
        bottom_tank_kv_lbl.grid(column=1, row=4, sticky='E', padx=3)
        self.b_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', variable=controller.b_kv)
        self.b_slider.grid(column=2, row=4, sticky='W')

        self.sim_btn = ttk.Button(self, text='START',
                                  command=lambda: self.start_stop_btn(controller.sim_running, controller))
        self.sim_btn.grid(column=3, row=5)

        self.prev_pg_btn = ttk.Button(self, text='Previous Page', command=lambda: controller.show_frame(Model))
        self.prev_pg_btn.grid(column=0, row=6, sticky='W')

        self.anim = animation.FuncAnimation(data.fig, controller.animate, interval=100)
        self.anim.pause()


class Model(tk.Frame, Util):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.l_water = None
        self.controller = controller

        label = tk.Label(self, text='Model', font=data.LARGE_FONT)
        label.grid(column=0, row=0, columnspan=4, sticky='WE')

        left_tank_lbl = ttk.Label(self, text='Left upper tank')
        left_tank_lbl.grid(column=0, row=2)
        left_tank_kv_lbl = ttk.Label(self, text='kv:')
        left_tank_kv_lbl.grid(column=1, row=2, sticky='E', padx=3)
        self.l_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', variable=controller.l_kv)
        self.l_slider.grid(column=2, row=2, sticky='W')
        self.l_valve_btn = ttk.Button(self, text='ON',
                                      command=lambda: self.switch_left_valve(controller.Ql, controller))
        self.l_valve_btn.grid(column=3, row=2, sticky='W')

        right_tank_lbl = ttk.Label(self, text='Right upper tank')
        right_tank_lbl.grid(column=0, row=3)
        right_tank_kv_lbl = ttk.Label(self, text='kv:')
        right_tank_kv_lbl.grid(column=1, row=3, sticky='E', padx=3)
        self.r_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', variable=controller.r_kv)
        self.r_slider.grid(column=2, row=3, sticky='W')
        self.r_valve_btn = ttk.Button(self, text='ON',
                                      command=lambda: self.switch_right_valve(controller.Qr, controller))
        self.r_valve_btn.grid(column=3, row=3, sticky='W')

        bottom_tank_lbl = ttk.Label(self, text='Bottom tank')
        bottom_tank_lbl.grid(column=0, row=4)
        bottom_tank_kv_lbl = ttk.Label(self, text='kv:')
        bottom_tank_kv_lbl.grid(column=1, row=4, sticky='E', padx=3)
        self.b_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', variable=controller.b_kv)
        self.b_slider.grid(column=2, row=4, sticky='W')

        self.sim_btn = ttk.Button(self, text='START',
                                  command=lambda: self.start_stop_btn(controller.sim_running, controller))
        self.sim_btn.grid(column=3, row=5)

        self.prev_pg_btn = ttk.Button(self, text='Previous Page',
                                      command=lambda: controller.show_frame(InformationPage))
        self.prev_pg_btn.grid(column=0, row=6, sticky='W')

        self.next_pg_btn = ttk.Button(self, text='Next Page', command=lambda: controller.show_frame(Graph))
        self.next_pg_btn.grid(column=3, row=6, sticky='E')

        ModelCanvas(self, controller)


class ModelCanvas(tk.Canvas):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.parent = parent
        self.root = controller
        self['width'] = 500
        self['height'] = 500
        self['bg'] = 'white'
        self.label_img = None
        self.img = 'assets/overflow_1.png'
        self.grid(column=0, row=1, columnspan=4, sticky='EW')

        self.xl0 = 100
        self.yl0 = 200
        self.xl1 = 100 + data.LU_LENGTH * 10
        self.yl1 = 200 + 0.001

        self.xr0 = self.xl1 + 20
        self.yr0 = 200
        self.xr1 = self.xr0 + data.RU_LENGTH * 10
        self.yr1 = self.yr0 + 0.001

        self.xb0 = statistics.mean([self.xl0, self.xr1]) - data.B_LENGTH * 10 / 2
        self.yb0 = 200 + 25 + (data.B_HEIGHT * 10)
        self.xb1 = self.xb0 + data.B_LENGTH * 10
        self.yb1 = self.yb0 + 0.001

        self.l_water = self.create_rectangle(self.xl0, self.yl0, self.xl1, self.yl1, fill='blue', outline='')
        self.r_water = self.create_rectangle(self.xr0, self.yr0, self.xr1, self.yr1, fill='blue', outline='')
        self.b_water = self.create_rectangle(self.xb0, self.yb0, self.xb1, self.yb1, fill='blue', outline='')

        # left tank
        self.create_line(self.xl0, self.yl0, self.xl0, self.yl0 - data.LU_HEIGHT*10, fill='black', width=3)
        self.create_line(self.xl0, self.yl0, self.xl1, self.yl0, fill='black', width=3)
        self.create_line(self.xl1, self.yl0, self.xl1, self.yl0 - data.LU_HEIGHT*10, fill='black', width=3)

        # right tank
        self.create_line(self.xr0, self.yr0, self.xr0, self.yr0 - data.RU_HEIGHT*10, fill='black', width=3)
        self.create_line(self.xr0, self.yr0, self.xr1, self.yr0, fill='black', width=3)
        self.create_line(self.xr1, self.yr0, self.xr1, self.yr0 - data.RU_HEIGHT*10, fill='black', width=3)

        # bottom tank
        self.create_line(self.xb0, self.yb0, self.xb0, self.yb0 - data.B_HEIGHT*10, fill='black', width=3)
        self.create_line(self.xb0, self.yb0, self.xb1, self.yb0, fill='black', width=3)
        self.create_line(self.xb1, self.yb0, self.xb1, self.yb0 - data.B_HEIGHT*10, fill='black', width=3)

        # left water stream and kv valve:
        self.create_line(self.xl1 - 28.5, self.yl0, self.xl1 - 21.5, self.yl0 + 15, width=2)
        self.create_line(self.xl1 - 21.5, self.yl0, self.xl1 - 28.5, self.yl0 + 15, width=2)
        self.create_line(self.xl1 - 28.5, self.yl0 + 15, self.xl1 - 21.5, self.yl0 + 15, width=2)
        self.l_ws = self.create_line(self.xl1 - 25, self.yl0 + 15, self.xl1 - 25, self.yl0 + 40 + (data.B_HEIGHT * 10),
                                     fill='', dash=(5, 3))

        # right water stream and kv valve
        self.create_line(self.xr0 + 28.5, self.yr0, self.xr0 + 21.5, self.yr0 + 15, width=2)
        self.create_line(self.xr0 + 21.5, self.yr0, self.xr0 + 28.5, self.yr0 + 15, width=2)
        self.create_line(self.xr0 + 28.5, self.yr0 + 15, self.xr0 + 21.5, self.yr0 + 15, width=2)
        self.r_ws = self.create_line(self.xr0 + 25, self.yr0 + 15, self.xr0 + 25, self.yr0 + 40 + (data.B_HEIGHT * 10),
                                     fill='', dash=(5, 3))

        # bottom water stream and kv valve
        self.create_line(self.xb0 + data.B_LENGTH*10/2 - 3.5, self.yb0,
                         self.xb0 + data.B_LENGTH*10/2 + 3.5, self.yb0 + 15, width=2)
        self.create_line(self.xb0 + data.B_LENGTH*10/2 + 3.5, self.yb0,
                         self.xb0 + data.B_LENGTH*10/2 - 3.5, self.yb0 + 15, width=2)
        self.create_line(self.xb0 + data.B_LENGTH*10/2 - 3.5, self.yb0 + 15,
                         self.xb0 + data.B_LENGTH*10/2 + 3.5, self.yb0 + 15, width=2)
        self.create_line(self.xr0 + 28.5, self.yr0 + 15, self.xr0 + 21.5, self.yr0 + 15, width=2)
        self.b_ws = self.create_line(self.xb0 + data.B_LENGTH*10/2, self.yb0 + 15,
                                     self.xb0 + data.B_LENGTH*10/2, self.yb0 + 1500,
                                     fill='', dash=(5, 3))

        # left inlet valve and water
        self.lv = self.create_oval(self.xl0 - 50, self.yl0 - data.LU_HEIGHT*10 - 50, self.xl0 - 25,
                                   self.yl0 - data.LU_HEIGHT*10 - 75, fill='green')

        # valve
        self.create_line(self.xl0 + data.LU_LENGTH*10/2 - 3.5, self.yl0 - 100,
                         self.xl0 + data.LU_LENGTH*10/2 + 3.5, self.yl0 - 115, width=2)
        self.create_line(self.xl0 + data.LU_LENGTH*10/2 + 3.5, self.yl0 - 100,
                         self.xl0 + data.LU_LENGTH*10/2 - 3.5, self.yl0 - 115, width=2)
        self.create_line(self.xl0 + data.LU_LENGTH*10/2 - 3.5, self.yl0 - 100,
                         self.xl0 + data.LU_LENGTH*10/2 + 3.5, self.yl0 - 100, width=2)
        self.create_line(self.xl0 + data.LU_LENGTH*10/2 - 3.5, self.yl0 - 115,
                         self.xl0 + data.LU_LENGTH*10/2 + 3.5, self.yl0 - 115, width=2)

        # water stream
        self.lu_ws = self.create_line(self.xl0 + data.LU_LENGTH*10/2, self.yl0 - 100,
                                      self.xl0 + data.LU_LENGTH*10/2, self.yl0, fill='', dash=(5, 3), width=5)

        # pipe
        self.create_line(self.xl0 + data.LU_LENGTH*10/2 - 3.5, self.yl0 - 115,
                         self.xl0 + data.LU_LENGTH*10/2 - 3.5, self.yl0 - 200, width=2)
        self.create_line(self.xl0 + data.LU_LENGTH*10/2 + 3.5, self.yl0 - 115,
                         self.xl0 + data.LU_LENGTH*10/2 + 3.5, self.yl0 - 200, width=2)

        # right inlet valve and water
        self.rv = self.create_oval(self.xr1 + 50, self.yr0 - data.RU_HEIGHT*10 - 50, self.xr1 + 25,
                                   self.yr0 - data.RU_HEIGHT*10 - 75, fill='green')
        # valve
        self.create_line(self.xr0 + data.RU_LENGTH*10/2 - 3.5, self.yr0 - 100,
                         self.xr0 + data.RU_LENGTH*10/2 + 3.5, self.yr0 - 115, width=2)
        self.create_line(self.xr0 + data.RU_LENGTH*10/2 + 3.5, self.yr0 - 100,
                         self.xr0 + data.RU_LENGTH*10/2 - 3.5, self.yr0 - 115, width=2)
        self.create_line(self.xr0 + data.RU_LENGTH*10/2 - 3.5, self.yr0 - 100,
                         self.xr0 + data.RU_LENGTH*10/2 + 3.5, self.yr0 - 100, width=2)
        self.create_line(self.xr0 + data.RU_LENGTH*10/2 - 3.5, self.yr0 - 115,
                         self.xr0 + data.RU_LENGTH*10/2 + 3.5, self.yr0 - 115, width=2)

        # pipe
        self.create_line(self.xr0 + data.RU_LENGTH*10/2 - 3.5, self.yr0 - 115,
                         self.xr0 + data.RU_LENGTH*10/2 - 3.5, self.yr0 - 200, width=2)
        self.create_line(self.xr0 + data.RU_LENGTH*10/2 + 3.5, self.yr0 - 115,
                         self.xr0 + data.RU_LENGTH*10/2 + 3.5, self.yr0 - 200, width=2)

        # water stream
        self.ru_ws = self.create_line(self.xr0 + data.RU_LENGTH*10/2, self.yr0 - 100, self.xr0 + data.RU_LENGTH*10/2,
                                      self.yr0, fill='', dash=(5, 3), width=5)

        self.update_model()

    def update_model(self):

        if open('left.txt', 'r').read() != '':
            self.root.hl.set(round(float(open('left.txt', 'r').readlines()[-1].split(',')[1][:-1]), 2))
            self.coords(self.l_water, self.xl0, self.yl0, self.xl1, self.yl1 - self.root.hl.get())
            self.coords(self.lu_ws, self.xl0 + data.LU_LENGTH*10/2, self.yl0 - 100,
                        self.xl0 + data.LU_LENGTH*10/2, self.yl0 - self.root.hl.get())
            if self.root.hl.get() <= 1:
                self.itemconfig(self.l_ws, fill='')
            else:
                self.itemconfig(self.l_ws, fill='blue')

        if open('right.txt', 'r').read() != '':
            self.root.hr.set(round(float(open('right.txt', 'r').readlines()[-1].split(',')[1][:-1]), 2))
            self.coords(self.r_water, self.xr0, self.yr0, self.xr1, self.yr1 - self.root.hr.get())
            if self.root.hr.get() <= 1:
                self.itemconfig(self.r_ws, fill='')
            else:
                self.itemconfig(self.r_ws, fill='blue')

        if open('bottom.txt', 'r').read() != '':
            self.root.hb.set(round(float(open('bottom.txt', 'r').readlines()[-1].split(',')[1][:-1]), 2))
            self.coords(self.b_water, self.xb0, self.yb0, self.xb1, self.yb1 - self.root.hb.get())
            self.coords(self.l_ws, self.xl1 - 25, self.yl0 + 15, self.xl1 - 25,
                        self.yl0 + 40 + (data.B_HEIGHT * 10) - self.root.hb.get() - 15)

            if self.root.l_kv.get() == 0.0 or self.root.hl.get() <= 0:
                self.itemconfig(self.l_ws, fill='')
            else:
                self.itemconfig(self.l_ws, fill='blue', width=self.root.l_kv.get() / 20)

            self.coords(self.r_ws, self.xr0 + 25, self.yr0 + 15, self.xr0 + 25,
                        self.yr0 + 40 + (data.B_HEIGHT * 10) - self.root.hb.get() - 15)
            if self.root.r_kv.get() == 0.0 or self.root.hr.get() <= 1:
                self.itemconfig(self.r_ws, fill='')
            else:
                self.itemconfig(self.r_ws, fill='blue', width=self.root.r_kv.get() / 20)

            if self.root.b_kv.get() == 0.0 or self.root.hb.get() <= 1:
                self.itemconfig(self.b_ws, fill='')
            else:
                self.itemconfig(self.b_ws, fill='blue', width=self.root.b_kv.get() / 20)

        if self.root.Ql:
            self.itemconfig(self.lv, fill='green')
            self.itemconfig(self.lu_ws, fill='blue')
        else:
            self.itemconfig(self.lv, fill='red')
            self.itemconfig(self.lu_ws, fill='')

        if self.root.Qr:
            self.itemconfig(self.rv, fill='green')
            self.itemconfig(self.ru_ws, fill='blue')
        else:
            self.itemconfig(self.rv, fill='red')
            self.itemconfig(self.ru_ws, fill='')

        self.warning_sign()
        self.after(100, self.update_model)

    def play_alarm(self):
        pygame.mixer.music.load('assets/alarm_sound.mp3')
        pygame.mixer.music.play(loops=-1)
        self.root.music_playing.set(True)

    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.root.music_playing.set(False)

    def warning_sign(self):
        if self.root.hl.get() >= data.LU_HEIGHT*10 or\
                self.root.hr.get() >= data.RU_HEIGHT*10 or self.root.hb.get() >= data.B_HEIGHT*10:
            if not self.root.music_playing.get():
                self.play_alarm()
            if self.img == 'assets/overflow_1.png':
                self.img = 'assets/overflow_2.png'
            else:
                self.img = 'assets/overflow_1.png'
        else:
            self.stop_alarm()
            self.img = ''
        self.label_img = tk.PhotoImage(file=self.img)
        lbl = tk.Label(self.root.frames[InformationPage], image=self.label_img)
        lbl.grid(column=0, row=6, columnspan=6)


class Menubar(tk.Menu):
    def __init__(self, controller):
        super().__init__()

        pages_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Chose Page', menu=pages_menu)
        pages_menu.add_command(label='Main Page', command=lambda: controller.show_frame(InformationPage))
        pages_menu.add_command(label='Schematic', command=lambda: controller.show_frame(Model))
        pages_menu.add_command(label='Graph', command=lambda: controller.show_frame(Graph))
