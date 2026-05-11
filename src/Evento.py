class Evento:
    #Representa un evento en la cola de prioridad

    def __init__(self, punto, tipo, segmentos=None):
        self.punto = punto
        self.tipo = tipo
        self.segmentos = segmentos if segmentos else []

    def __lt__(self, other):
        epsilon = 1e-9
        if abs(self.punto.y - other.punto.y) > epsilon:
            return self.punto.y > other.punto.y
        return self.punto.x < other.punto.x

    def __eq__(self, other):
        return self.punto.es_igual_a(other.punto)

    def __str__(self):
        return f"Evento({self.tipo} en {self.punto})"

    def __repr__(self):
        return self.__str__()