import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from libraries.micropython import const
from libraries.tempos import g, rtc, sched
from libraries.graphics import WHITE, BLACK, CYAN
from libraries.fonts import hugefont, roboto24
import tkinter as tk

X = const(25)

days = ["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class NiftyClockScreen:
    def __init__(self, g, root, controller):
        self.g = g
        self.controller = controller
        self.root = root
        self.ticker = None
        self.minute = -1
        self.app_init()

    def drawTime(self):
        t = rtc.datetime()
        if self.minute != t[5]:
            self.minute = t[5]
            self.g.fill(BLACK)
            self.g.setfontalign(-1, -1)
            self.g.setfont(hugefont)
            self.g.text("{:02}".format(t[4]), X, 35, WHITE)
            self.g.text("{:02}".format(t[5]), X, 125, WHITE)
            self.g.fill_rect(X + 110, 40, 4, 170, CYAN)
            self.g.setfont(roboto24)
            self.g.text(str(t[0]), X + 124, 40, WHITE)
            self.g.text("{:02}".format(t[1]), X + 124, 64, WHITE)
            self.g.text("{:02}".format(t[2]), X + 124, 88, WHITE)
            self.g.text(months[t[1] - 1], X + 124, 154, WHITE)
            self.g.text(days[t[3]], X + 124, 178, WHITE)
            self.g.show()

    def app_init(self):
        self.drawTime()
        self.ticker_flag, self.ticker_thread = sched.setInterval(100, self.drawTime)

    def app_end(self):
        if self.ticker_thread:
            sched.clearInterval(self.ticker_flag, self.ticker_thread)
        self.g.fill(BLACK)

if __name__ == "__main__":
    root = tk.Tk()
    g = g(root)
    NiftyClockScreen(g, root, None)  # Create and display the incoming call screen
    root.mainloop()