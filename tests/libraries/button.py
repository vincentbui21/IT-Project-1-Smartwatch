# button.py

class Button:
    def __init__(self, label, x, y, width, height, font):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.callback_func = None

    def callback(self, func):
        self.callback_func = func
        print(f"Callback set for button '{self.label}'")

class ButtonMan:
    def __init__(self):
        self.buttons = []

    def add(self, button):
        self.buttons.append(button)
        print(f"Button '{button.label}' added")

    def start(self):
        print("Buttons activated")

    def stop(self):
        print("Buttons deactivated")
