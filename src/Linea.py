import math
from .Punto import Punto

class Linea:
    def __init__(self,A,B,C):
        self.A = float(A)
        self.B = float(B)
        self.C = float(C)

    def __str__(self):
        resultado = "Linea: "
        if self.A >=0:
            resultado += f" {self.A}x "
        else:
            resultado += f"- {abs(self.A)}x "

        if self.B >= 0:
            resultado += f"+ {self.B}y "
        else:
            resultado += f"- {abs(self.B)}y "

        if self.C >= 0:
            resultado += f"+ {self.C} "
        else:
            resultado += f"- {abs(self.C)} "

        resultado += f" = 0 "
        return resultado

    def interseccion(self,other):
        D = self.A*other.B - other.A*self.B
        if D == 0:
            return "Son paralelas"
        else:
            Dx = -self.C*other.B-(-other.C*self.B)
            Dy = self.A*(-other.C)-other.A*(-self.C)
            x = Dx/D
            y = Dy/D
            return Punto(x,y)

    def distancia_a_punto(self,punto):
        #lparalela = Linea(-self.B,self.A,self.B*punto.x-self.A*punto.y)
        #inter = self.interseccion(lparalela)
        inter = self.inter_Paralela_por_punto(punto)
        return inter.distancia(punto)

    def inter_Paralela_por_punto(self,punto):
        lparalela = Linea(-self.B, self.A, self.B * punto.x - self.A * punto.y)
        return self.interseccion(lparalela)


