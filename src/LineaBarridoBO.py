from sortedcontainers import SortedList
from .SegmentoComparable import SegmentoComparable


class LineaBarridoBO:
    def __init__(self):
        self.y_actual = None
        self._sl = SortedList()
        self._mapa = {}

    def _x_at_y(self, seg):
        epsilon = 1e-9
        if abs(seg.p1.x - seg.p2.x) < epsilon:
            return seg.p1.x
        elif abs(seg.p1.y - seg.p2.y) < epsilon:
            return (seg.p1.x + seg.p2.x) / 2.0
        else:
            m = (seg.p2.y - seg.p1.y) / (seg.p2.x - seg.p1.x)
            return seg.p1.x + (self.y_actual - seg.p1.y) / m

    def actualizar_y(self, nuevo_y):
        self.y_actual = nuevo_y

    def insertar(self, segmento):
        if segmento in self._mapa: return
        item = SegmentoComparable(segmento, self)
        self._sl.add(item)
        self._mapa[segmento] = item

    def eliminar(self, segmento):
        if segmento in self._mapa:
            item = self._mapa[segmento]
            try:
                self._sl.remove(item)
            except ValueError:
                for i, w in enumerate(self._sl):
                    if w is item:
                        del self._sl[i]
                        break
            del self._mapa[segmento]

    def vecino_izquierdo(self, segmento):
        if segmento not in self._mapa: return None
        item = self._mapa[segmento]
        try:
            idx = self._sl.index(item)
            if idx > 0: return self._sl[idx - 1].segmento
        except ValueError:
            pass
        return None

    def vecino_derecho(self, segmento):
        if segmento not in self._mapa: return None
        item = self._mapa[segmento]
        try:
            idx = self._sl.index(item)
            if idx < len(self._sl) - 1: return self._sl[idx + 1].segmento
        except ValueError:
            pass
        return None

    def segmentos_en_rango_x(self, x_min, x_max):
        res = []
        for wrapper in self._sl:
            x = self._x_at_y(wrapper.segmento)
            if x >= x_min - 1e-7 and x <= x_max + 1e-7:
                res.append(wrapper.segmento)
        return res

    def __len__(self):
        return len(self._sl)

    @property
    def segmentos(self):
        return [w.segmento for w in self._sl]