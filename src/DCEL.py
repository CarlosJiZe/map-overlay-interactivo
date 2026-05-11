
class Vertice:
    def __init__(self, nombre, x, y):
        self.nombre = nombre
        self.x = float(x)
        self.y = float(y)
        self.incidente = None          # Half-edge que sale de este vértice

    def __repr__(self):
        return f"Vertice({self.nombre}, {self.x}, {self.y})"


class HalfEdge:
    def __init__(self, nombre):
        self.nombre = nombre
        self.origen = None             # Vertice
        self.pareja = None             # HalfEdge gemelo
        self.cara = None               # Cara a la que pertenece
        self.siguiente = None          # HalfEdge siguiente en el ciclo
        self.anterior = None           # HalfEdge anterior en el ciclo

    def destino(self):
        """El vértice destino es el origen de la pareja."""
        return self.pareja.origen if self.pareja else None

    def ciclo(self):
        """Recorre el ciclo de half-edges de esta cara a partir de self."""
        resultado = []
        actual = self
        visitados = set()
        while actual is not None and id(actual) not in visitados:
            resultado.append(actual)
            visitados.add(id(actual))
            actual = actual.siguiente
            if actual is self:
                break
        return resultado

    def __repr__(self):
        orig = self.origen.nombre if self.origen else "?"
        dest = self.destino().nombre if self.destino() else "?"
        return f"HalfEdge({self.nombre}: {orig}→{dest})"


class Cara:
    def __init__(self, nombre):
        self.nombre = nombre
        self.externa = None            # HalfEdge que define el borde exterior
        self.internas = []             # Lista de HalfEdges para holes/internos

    def vertices(self):
        """
        Devuelve la lista de vértices del ciclo exterior de la cara.
        Retorna [] si es la cara exterior (externa = None).
        """
        if self.externa is None:
            return []
        return [he.origen for he in self.externa.ciclo()]

    def __repr__(self):
        return f"Cara({self.nombre})"


class DCEL:
    def __init__(self):
        self.vertices = {}     # nombre -> Vertice
        self.half_edges = {}   # nombre -> HalfEdge
        self.caras = {}        # nombre -> Cara

    def agregar_vertice(self, nombre, x, y):
        v = Vertice(nombre, x, y)
        self.vertices[nombre] = v
        return v

    def agregar_half_edge(self, nombre):
        he = HalfEdge(nombre)
        self.half_edges[nombre] = he
        return he

    def agregar_cara(self, nombre):
        c = Cara(nombre)
        self.caras[nombre] = c
        return c

    def __repr__(self):
        return (f"DCEL(vértices={len(self.vertices)}, "
                f"half_edges={len(self.half_edges)}, "
                f"caras={len(self.caras)})")