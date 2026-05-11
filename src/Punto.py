import math

class Punto:
    #Constructor
    def __init__(self,x,y):
        self.x = float(x)
        self.y = float(y)
    #Le damos un formato bonito
    def __str__(self):
        return f"Punto ({self.x}, {self.y})"
    #Hacemos la traslados en dx y dy
    def trasladar(self,dx,dy):
        puntoTras = Punto(self.x+dx,self.y+dy)
        return puntoTras
    #Hacemos la rotación en base al origen en grados
    def rotar(self,angulo):
        angulo = math.radians(angulo)
        puntoRot = Punto(round((self.x*math.cos(angulo))-(self.y*math.sin(angulo)),10),
                         round((self.x*math.sin(angulo))+(self.y*math.cos(angulo)),10))
        return puntoRot
    #Convertimos a polares
    def convertir_Polares(self):
        r = math.sqrt((self.x)**2+(self.y)**2)
        theta = math.atan2(self.y,self.x)
        thetagrados = math.degrees(theta)
        return (r,theta,thetagrados)
    #Comparar 2 puntos
    def es_igual_a(self,other):
        epsilon = 1e-6
        if abs(self.x - other.x) < epsilon and abs(self.y - other.y) < epsilon:
            return True
        else:
            return False

    def distancia(self,other):
        distancia = math.sqrt((self.x-other.x)**2+(self.y-other.y)**2)
        return distancia
