import math

from .Punto import Punto
from .Linea import Linea


class Segmento:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return f"Segmento: (Punto({self.p1.x},{self.p1.y}) -> (Punto({self.p2.x},{self.p2.y}))"

    def longitud(self):
        longitud = self.p1.distancia(self.p2)
        return longitud

    def angulo(self):
        dx = (self.p2.x - self.p1.x)
        dy = (self.p2.y - self.p1.y)
        angulo = math.atan2(dy, dx)
        angulo = math.degrees(angulo)
        return angulo

    def aLinea(self):
        A = self.p1.y - self.p2.y
        B = self.p2.x - self.p1.x
        C = (self.p1.x * self.p2.y - self.p1.y * self.p2.x)
        lin = Linea(A, B, C)
        return lin

    def interseccion(self, other):
        l1 = self.aLinea()
        l2 = other.aLinea()
        inter = l1.interseccion(l2)
        if inter == "Son paralelas":
            return "Son paralelas"
        else:
            # Ahora usa el 'punto_esta_en_segmento' mejorado con epsilon
            if self.punto_esta_en_segmento(inter) and other.punto_esta_en_segmento(inter):
                return inter
            else:
                return "No se intersectan"

    def punto_esta_en_segmento(self, punto):
        epsilon = 1e-7

        x_min = min(self.p1.x, self.p2.x) - epsilon
        x_max = max(self.p1.x, self.p2.x) + epsilon
        y_min = min(self.p1.y, self.p2.y) - epsilon
        y_max = max(self.p1.y, self.p2.y) + epsilon

        if x_min <= punto.x <= x_max and y_min <= punto.y <= y_max:
            return True
        else:
            return False

    def distancia(self, punto):
        l1 = self.aLinea()
        inter = l1.inter_Paralela_por_punto(punto)
        if self.punto_esta_en_segmento(inter):
            return l1.distancia_a_punto(punto)
        else:
            min_dist = min(self.p1.distancia(punto), self.p2.distancia(punto))
            return min_dist

    def punto_mas_cercano(self, punto):
        l1 = self.aLinea()
        inter = l1.inter_Paralela_por_punto(punto)
        if self.punto_esta_en_segmento(inter):
            return inter
        else:
            dist1 = self.p1.distancia(punto)
            dist2 = self.p2.distancia(punto)
            return self.p1 if dist1 < dist2 else self.p2

    def interactua_con_barrido(self, y_barrido):
        """
        Retorna True si la coordenada Y de la línea de barrido
        está dentro del rango vertical del segmento.
        """
        epsilon = 1e-7
        y_min = min(self.p1.y, self.p2.y) - epsilon
        y_max = max(self.p1.y, self.p2.y) + epsilon

        return y_min <= y_barrido <= y_max

