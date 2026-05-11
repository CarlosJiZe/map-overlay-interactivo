import math
import os
from src.DCEL import DCEL
from src.Segmento import Segmento
from src.Punto import Punto
from src.AlgoritmoBO import bentley_ottmann
from src.LectorDCEL import leer_dcel


# ─────────────────────────────────────────────────────────────
# 1. EXTRACCIÓN DE SEGMENTOS
# ─────────────────────────────────────────────────────────────

def extraer_segmentos(dcel):
    """Extrae segmentos únicos de una estructura DCEL."""
    segmentos, vistos = [], set()
    for nombre, he in dcel.half_edges.items():
        if he.origen is None or he.destino() is None: continue
        # Usamos frozenset para identificar la pareja sin importar el orden
        clave = frozenset([nombre, he.pareja.nombre if he.pareja else ''])
        if clave in vistos: continue
        vistos.add(clave)
        segmentos.append(Segmento(Punto(he.origen.x, he.origen.y), Punto(he.destino().x, he.destino().y)))
    return segmentos


# ─────────────────────────────────────────────────────────────
# 2. SUBDIVISIÓN POR INTERSECCIONES
# ─────────────────────────────────────────────────────────────

def subdividir(todos_segs, intersecciones):
    """Corta los segmentos originales en sub-segmentos usando los puntos de cruce."""
    puntos_en_seg = {id(s): [] for s in todos_segs}
    for pt_inter, segs_inv in intersecciones.items():
        for seg in segs_inv:
            if id(seg) in puntos_en_seg and not (pt_inter.es_igual_a(seg.p1) or pt_inter.es_igual_a(seg.p2)):
                puntos_en_seg[id(seg)].append(pt_inter)

    sub_segs = []
    for seg in todos_segs:
        dx, dy = seg.p2.x - seg.p1.x, seg.p2.y - seg.p1.y
        long2 = dx * dx + dy * dy
        # Ordenamos los puntos de intersección a lo largo de la trayectoria del segmento
        pts = sorted(puntos_en_seg[id(seg)],
                     key=lambda p: 0.0 if long2 < 1e-12 else ((p.x - seg.p1.x) * dx + (p.y - seg.p1.y) * dy) / long2)
        cadena = [seg.p1] + pts + [seg.p2]
        for i in range(len(cadena) - 1):
            sub_segs.append((cadena[i], cadena[i + 1]))
    return sub_segs


# ─────────────────────────────────────────────────────────────
# 3. CONSTRUCCIÓN DE TOPOLOGÍA (ENLACE ANGULAR)
# ─────────────────────────────────────────────────────────────

def enlazar_angular(resultado):
    """Organiza los punteros 'siguiente' y 'anterior' de cada arista por ángulo."""
    salientes_por_v = {id(v): [] for v in resultado.vertices.values()}
    for he in resultado.half_edges.values():
        if he.origen: salientes_por_v[id(he.origen)].append(he)

    for v in resultado.vertices.values():
        salientes = salientes_por_v[id(v)]
        if not salientes: continue
        # Ordenamos antihorariamente
        salientes.sort(key=lambda he: math.atan2(he.destino().y - v.y, he.destino().x - v.x))
        for i, e_i in enumerate(salientes):
            # La arista previa en el sentido CCW es la que cierra la cara a la izquierda
            e_prev = salientes[(i - 1) % len(salientes)]
            e_i.pareja.siguiente = e_prev
            e_prev.anterior = e_i.pareja


# ─────────────────────────────────────────────────────────────
# 4. FUNCIONES DE MAP OVERLAY (PIPELINE)
# ─────────────────────────────────────────────────────────────

def construir_overlay(dcel1, dcel2):
    """Realiza la superposición de dos estructuras DCEL."""
    segs = extraer_segmentos(dcel1) + extraer_segmentos(dcel2)
    intersecciones = bentley_ottmann(segs)
    sub_segs = subdividir(segs, intersecciones)

    res = DCEL()
    v_map, c_v, c_he = {}, [0], [0]

    def get_v(x, y):
        k = (round(x, 6), round(y, 6))
        if k not in v_map:
            c_v[0] += 1;
            v_map[k] = res.agregar_vertice(f"v{c_v[0]}", x, y)
        return v_map[k]

    for pi, pf in sub_segs:
        v1, v2 = get_v(pi.x, pi.y), get_v(pf.x, pf.y)
        c_he[0] += 1;
        h1 = res.agregar_half_edge(f"he{c_he[0]}")
        c_he[0] += 1;
        h2 = res.agregar_half_edge(f"he{c_he[0]}")
        h1.origen, h2.origen, h1.pareja, h2.pareja = v1, v2, h2, h1
        if not v1.incidente: v1.incidente = h1
        if not v2.incidente: v2.incidente = h2

    enlazar_angular(res)
    return res, intersecciones


def construir_overlay_n_capas(rutas):
    """Fusiona múltiples capas en una sola DCEL final."""
    if not rutas: return None
    print(f"\n[*] Procesando Pipeline de {len(rutas)} capas...")
    res = leer_dcel(rutas[0])
    for i in range(1, len(rutas)):
        print(f"    -> Fusionando con: {os.path.basename(rutas[i])}")
        res, _ = construir_overlay(res, leer_dcel(rutas[i]))
    return res


# ─────────────────────────────────────────────────────────────
# 5. EXPORTACIÓN DE RESULTADOS
# ─────────────────────────────────────────────────────────────

def exportar_overlay(dcel, nombre, carpeta='resultados'):
    """Guarda la geometría resultante en archivos de texto."""
    os.makedirs(carpeta, exist_ok=True)
    base = os.path.join(carpeta, nombre)

    with open(base + '.vertices', 'w', encoding='utf-8') as f:
        f.write("Nombre  x       y       Incidente\n")
        for n, v in dcel.vertices.items():
            f.write(f"{n:<8}{v.x:<8}{v.y:<8}{v.incidente.nombre if v.incidente else 'None'}\n")

    with open(base + '.aristas', 'w', encoding='utf-8') as f:
        f.write("Nombre  Origen  Pareja  Cara    Sigue   Antes\n")
        for n, h in dcel.half_edges.items():
            f.write(f"{n:<8}{h.origen.nombre:<8}{h.pareja.nombre:<8}{h.cara.nombre if h.cara else 'None'}"
                    f"{h.siguiente.nombre if h.siguiente else 'None':<8}{h.anterior.nombre if h.anterior else 'None'}\n")

    with open(base + '.caras', 'w', encoding='utf-8') as f:
        f.write("Nombre  Interno Externo\n")
        for n, c in dcel.caras.items():
            f.write(f"{n:<8}{[h.nombre for h in c.internas]}   {c.externa.nombre if c.externa else 'None'}\n")

    print(f"[*] Geometría exportada exitosamente en '{carpeta}/'")