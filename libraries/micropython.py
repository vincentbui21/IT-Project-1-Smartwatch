# micropython.py

class const:
    def __init__(self, value):
        self._value = value  # Store the value in a private variable

    def __repr__(self):
        return f"{self._value}"

    def __int__(self):
        return self._value  # Allow conversion to int

    def __index__(self):
        return self._value  # Allow use in slice operations and range

    def __add__(self, other):
        return self._value + int(other)  # Support addition with other types

    def __sub__(self, other):
        return self._value - int(other)  # Support subtraction with other types

    def __mul__(self, other):
        return self._value * int(other)  # Support multiplication with other types

    def __truediv__(self, other):
        return self._value / int(other)  # Support division with other types

    def __floordiv__(self, other):
        return self._value // int(other)  # Support floor division with other types

    def __mod__(self, other):
        return self._value % int(other)  # Support modulo operation

    # You can add more operations as needed
