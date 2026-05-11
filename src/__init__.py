# src/__init__.py
from .Evento import Evento
from .Punto import Punto
from .Linea import Linea
from .Segmento import Segmento
from .Vector import Vector
from .SegmentoComparable import SegmentoComparable
from .LineaBarridoBO import LineaBarridoBO
from .AlgoritmoBO import bentley_ottmann
from .DCEL import DCEL, Vertice, HalfEdge, Cara
from .LectorDCEL import leer_dcel

__all__ = [
    'Punto', 'Linea', 'Segmento', 'Vector',
    'Evento', 'SegmentoComparable', 'LineaBarridoBO',
    'bentley_ottmann','DCEL', 'Vertice', 'HalfEdge', 'Cara', 'leer_dcel',
]
