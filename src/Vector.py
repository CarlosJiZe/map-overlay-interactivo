from .Punto import Punto

class Vector:
    def __init__(self,p1,p2):
        self.x = (p2.x-p1.x)
        self.y = (p2.y-p1.y)

    def __str__(self):
        return f"Vector ({self.x}, {self.y})"

    def signo_angulo_dos_vectores(self,other):
        signo = self.x*other.y - other.x*self.y
        if signo > 0:
            return True
        else:
            return False






