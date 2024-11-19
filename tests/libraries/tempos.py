import math
import tkinter as tk
from datetime import datetime
#from threading import Timer, Event
import threading
import time

# Constants for touch inputs
SWIPE_RIGHT = 1
SWIPE_LEFT = 2
SWIPE_UP = 3
SWIPE_DOWN = 4

class g:
    def __init__(self, root):
        self.width = 240
        self.height = 240
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()
        self.fg = "white"
        self.bg = "white"
        self.font = ("Arial", 24)
        self.align_x = 0
        self.align_y = 0

    def fill_rect(self, x, y, width, height, color):
        self.canvas.create_rectangle(x, y, x + width, y + height, fill=color)

    def rect(self, x, y, width, height, color):
        self.canvas.create_rectangle(x, y, x + width, y + height, outline=color)

    def text(self, text, x, y, color=None, justify=None):
        fill_color = color if color is not None else self.fg
        text_justify = justify if justify is not None else tk.LEFT
        self.canvas.create_text(x, y, text=text, fill=fill_color, font=self.font, anchor=self.anchor, justify=text_justify)

    def setcolor(self, fg, bg=None):
        self.fg = fg
        if bg is not None:
            self.bg = bg

    def setfont(self, font):
        self.font = font

    def setfontalign(self, align_x, align_y):
        # Asignar la alineación horizontal (X)
        if align_x == -1:  # Izquierda
            self.align_x = "w"
        elif align_x == 0:  # Centro
            self.align_x = ""
        elif align_x == 1:  # Derecha
            self.align_x = "e"
        
        # Asignar la alineación vertical (Y)
        if align_y == -1:  # Arriba
            self.align_y = "n"
        elif align_y == 0:  # center
            self.align_y = ""
        elif align_y == 1:  # Down
            self.align_y = "s"
        
        self.anchor = self.align_y + self.align_x
        if self.anchor == "":
            self.anchor = "center"

    def line(self, x1, y1, x2, y2, color):
        self.canvas.create_line(x1, y1, x2, y2, fill=color)

    def fill(self, color):
        self.canvas.configure(bg=color)
        self.canvas.delete("all")  # Clear canvas

    def show(self):
        self.canvas.update()

    def ellipse(self, x, y, rx, ry, color, fill):
        # Cálculo de las coordenadas para dibujar la elipse usando el centro y los radios
        x0, y0 = x - rx, y - ry
        x1, y1 = x + rx, y + ry

        # Condicional para rellenar o solo dibujar el contorno
        if fill:
            self.canvas.create_oval(x0, y0, x1, y1, outline=color, fill=color)
        else:
            self.canvas.create_oval(x0, y0, x1, y1, outline=color)

    def fill_rounded_rect(self, x, y, width, height, radius, color):
        # Draw the borders
        self.canvas.create_arc(x, y, x + 2 * radius, y + 2 * radius, start=90, extent=90, fill=color, outline=color)
        self.canvas.create_arc(x + width - 2 * radius, y, x + width, y + 2 * radius, start=0, extent=90, fill=color, outline=color)
        self.canvas.create_arc(x, y + height - 2 * radius, x + 2 * radius, y + height, start=180, extent=90, fill=color, outline=color)
        self.canvas.create_arc(x + width - 2 * radius, y + height - 2 * radius, x + width, y + height, start=270, extent=90, fill=color, outline=color)

        # Draw straight rectangles
        self.canvas.create_rectangle(x + radius, y, x + width - radius, y + height + 1, fill=color, outline="")
        self.canvas.create_rectangle(x, y + radius, x + width + 1, y + height - radius, fill=color, outline="")

    def poly(self, x, y, coord, color, fill, angle=0):
        # Aplicar rotación a las coordenadas
        rotated_coords = []
        rad_angle = math.radians(angle)
        cos_angle = math.cos(rad_angle)
        sin_angle = math.sin(rad_angle)
        
        for i in range(0, len(coord), 2):
            # Rotar cada punto alrededor del origen (x, y)
            x_offset = coord[i]
            y_offset = coord[i + 1]
            rotated_x = x + x_offset * cos_angle - y_offset * sin_angle
            rotated_y = y + x_offset * sin_angle + y_offset * cos_angle
            rotated_coords.append(rotated_x)
            rotated_coords.append(rotated_y)

        # Dibujar el polígono rotado
        if fill:
            self.canvas.create_polygon(rotated_coords, outline=color, fill=color)
        else:
            self.canvas.create_polygon(rotated_coords, outline=color, fill="")


class tc:
    @staticmethod
    def addListener(callback):
        print("Adding touch listener")

    @staticmethod
    def removeListener(callback):
        print("Removing touch listener")

class sched:
    @staticmethod
    def setTimeout(timeout, callback, *args):
        time.sleep(timeout / 1000)  # Convert miliseconds to seconds
        callback(*args)

    @staticmethod
    def setInterval(interval, callback, *args):
        # Variable to stop the loop
        stop_flag = threading.Event()

        # Function to call the callback
        def loop():
            while not stop_flag.is_set():  # Keep executing while the flag is no activated
                callback(*args)
                time.sleep(interval / 1000)  # Convert from miliseconds to seconds

        # Start a thread that will execute `loop()` in irregular itnervals
        t = threading.Thread(target=loop)
        t.daemon = True  # Make sure the thread ends when the program closes
        t.start()
        
        # Return the flag and the thread
        return stop_flag, t

    @staticmethod
    def clearInterval(stop_flag, thread):
        # Activate the flag to stop the loop
        stop_flag.set()
        # Wait until the thread ends
        thread.join()

class loader:
    @staticmethod
    def setapplock(lock):
        state = "locked" if lock else "unlocked"
        print(f"Application lock is now {state}")

class RTC:
    def datetime(self):
        now = datetime.now()
        return (now.year, now.month, now.day, now.weekday(), now.hour, now.minute, now.second)

rtc = RTC()