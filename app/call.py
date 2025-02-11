import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from datetime import datetime
from libraries.tempos import g, sched
from libraries.graphics import LIGHTGREEN, RED, WHITE, BLACK
from libraries.fonts import roboto8, roboto22, roboto10

BUTTON_WIDTH = 80
BUTTON_HEIGHT = 30
BUTTON_Y = 155
ACCEPT_X = 135
DECLINE_X = 30
RADIUS = 8

class IncomingCallScreen:
    # Init the class and add the listener to the left click
    def __init__(self, g, root, controller):
        self.g = g
        self.root = root
        self.controller = controller
        self.minute = -1
        self.day = -1
        self.g.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key-space>", self.on_key_pressed)
        self.app_init()
    
    # Function to display the current time and date
    def display_time_and_date(self):
        # Take and format data
        now = datetime.now()
        if self.minute != now.minute:
            self.minute = now.minute
            time_str = now.strftime("%H:%M")
            
            # Clear up screen
            self.g.fill_rect(0, 0, 120, 30, BLACK)
            
            # Display time on the top left
            self.g.setfont(roboto10)
            self.g.setfontalign(-1, -1)
            self.g.text(time_str, 10, 10, WHITE)

            if self.day != now.day:
                self.day = now.day
                self.display_date(now)

            # Show the screen
            self.g.show()

    def display_date(self, now):
        # Clear up screen
        self.g.fill_rect(120, 0, 120, 30, BLACK)
        date_str = now.strftime("%d %b %Y")

        # Display date on the top right
        self.g.setfontalign(1, -1)
        self.g.text(date_str, 230, 10, WHITE)

    # Function to display the main interface
    def setup_screen(self):        
        # Central text for the incoming call message
        self.g.setfontalign(0, 0)
        self.g.setfont(roboto22)
        self.g.text("Incoming\ndoorbell call", 120, 90, WHITE, tk.CENTER)
        
        # Red button for "Decline"
        self.g.fill_rounded_rect(DECLINE_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, RADIUS, RED)
        self.g.setfont(roboto8)
        self.g.text("Decline", 70, 170, WHITE)
        
        # Green button for "Accept"
        self.g.fill_rounded_rect(ACCEPT_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, RADIUS, LIGHTGREEN)
        self.g.text("Accept", 175, 170, WHITE)

    def app_init(self):
        # Clear the screen
        self.g.fill(BLACK)
        self.setup_screen()
        self.display_time_and_date()
        self.ticker_flag, self.ticker_thread = sched.setInterval(100, self.display_time_and_date)

    def app_end(self):
        if self.ticker_thread:
            sched.clearInterval(self.ticker_flag, self.ticker_thread)
        self.g.fill(BLACK)

    def on_click(self, event):
        # Check if click is within the Decline or Accept button area
        if DECLINE_X <= event.x <= DECLINE_X + BUTTON_WIDTH and BUTTON_Y <= event.y <= BUTTON_Y + BUTTON_HEIGHT:
            self.controller.show_nifty_clock_screen()
        elif ACCEPT_X <= event.x <= ACCEPT_X + BUTTON_WIDTH and BUTTON_Y <= event.y <= BUTTON_Y + BUTTON_HEIGHT:
            self.controller.show_doorbell_screen()

    def on_key_pressed(self, event):
        # Change the page to the Call screen
        self.controller.show_nifty_clock_screen()

if __name__ == "__main__":
    root = tk.Tk()
    g = g(root)
    IncomingCallScreen(g)  # Create and display the incoming call screen
    root.mainloop()
