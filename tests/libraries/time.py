import time as tm

class time:
    def __init__(self):
        self.start_time = tm.time() * 1000  # Tiempo en milisegundos
        self.current_time = self.start_time

    def ticks_ms(self):
        # Retorna el tiempo actual en milisegundos desde el inicio
        return int(tm.time() * 1000)  # Multiplicamos por 1000 para obtener milisegundos

    def ticks_diff(self, end, start):
        # Calcula la diferencia entre dos tiempos en milisegundos
        return end - start