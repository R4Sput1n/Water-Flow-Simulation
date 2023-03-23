import tkinter as tk
import classes
import data
import pygame


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        pygame.mixer.init()
        self.l_kv = tk.DoubleVar()
        self.r_kv = tk.DoubleVar()
        self.b_kv = tk.DoubleVar()
        self.Ql = tk.BooleanVar()
        self.Qr = tk.BooleanVar()
        self.hl = tk.DoubleVar()
        self.hr = tk.DoubleVar()
        self.hb = tk.DoubleVar()
        self.music_playing = tk.BooleanVar()

        menubar = classes.Menubar(self)
        self.config(menu=menubar)
        self.sim_running = False

        self.frames = {}

        for F in (classes.InformationPage, classes.Model, classes.Graph):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nesw')

        self.show_frame(classes.InformationPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()

    def start_stop_sim(self):
        if self.sim_running:
            self.sim_running = False
        else:
            self.sim_running = True

    def left_valve(self):
        if self.Ql:
            return data.Q
        else:
            return 0

    def right_valve(self):
        if self.Qr:
            return data.Q
        else:
            return 0

    def animate(self, unused):
        if self.sim_running is True:
            classes.left_upper_tank.iteration(self.left_valve(), self.l_kv.get(), 'left.txt')
            classes.right_upper_tank.iteration(self.right_valve(), self.r_kv.get(), 'right.txt')
            q_out_sum = classes.left_upper_tank.q_out + classes.right_upper_tank.q_out
            classes.lower_tank.iteration(q_out_sum, self.b_kv.get(), 'bottom.txt')

        get_data_left = open('left.txt', 'r').read()
        get_data_right = open('right.txt', 'r').read()
        get_data_bottom = open('bottom.txt', 'r').read()

        data_list_left = get_data_left.split('\n')
        data_list_right = get_data_right.split('\n')
        data_list_bottom = get_data_bottom.split('\n')

        x_left = []
        y_left = []
        x_right = []
        y_right = []
        x_bottom = []
        y_bottom = []

        for line in data_list_left:
            if len(line) > 0:
                x_char, y_char = line.split(',')
                x_left.append(float(x_char))
                y_left.append(float(y_char))

        for line in data_list_right:
            if len(line) > 0:
                x_char, y_char = line.split(',')
                x_right.append(float(x_char))
                y_right.append(float(y_char))

        for line in data_list_bottom:
            if len(line) > 0:
                x_char, y_char = line.split(',')
                x_bottom.append(float(x_char))
                y_bottom.append(float(y_char))

        data.sub.clear()
        data.sub.plot(x_left, y_left, label='left')
        data.sub.plot(x_right, y_right, label='right')
        data.sub.plot(x_bottom, y_bottom, label='bottom')
        data.sub.legend()


if __name__ == '__main__':
    for file in ('left.txt', 'right.txt', 'bottom.txt'):
        f = open(file, 'w')
        f.close()

    root = MainApp()
    root.mainloop()
