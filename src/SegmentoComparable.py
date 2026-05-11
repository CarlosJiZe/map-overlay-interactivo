class SegmentoComparable:
    def __init__(self, segmento, linea_barrido):
        self.segmento = segmento
        self.lb = linea_barrido

    def __lt__(self, other):
        x1 = self.lb._x_at_y(self.segmento)
        x2 = self.lb._x_at_y(other.segmento)
        if abs(x1 - x2) < 1e-9:
            return id(self.segmento) < id(other.segmento)
        return x1 < x2

    def __eq__(self, other):
        return self.segmento == other.segmento

    def __hash__(self):
        return id(self.segmento)

    def __repr__(self):
        return str(self.segmento)