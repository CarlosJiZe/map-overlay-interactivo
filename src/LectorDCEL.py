#LectorDCEL.py — Lector de archivos DCEL


import re
from .DCEL import DCEL


def _es_linea_datos(linea):
    """Ignora encabezados, separadores y líneas vacías."""
    linea = linea.strip()
    if not linea:
        return False
    if linea.startswith('#'):
        return False
    # Primera línea descriptiva ("Archivo de vértices", etc.)
    if linea.lower().startswith('archivo'):
        return False
    # Línea de encabezado de columnas (contiene palabras como Nombre, x, y...)
    palabras_header = {'nombre', 'x', 'y', 'incidente', 'origen', 'pareja',
                       'cara', 'sigue', 'antes', 'interno', 'externo'}
    primera_palabra = linea.split()[0].lower()
    if primera_palabra in palabras_header:
        return False
    return True


def _parsear_lista_aristas(texto):
    """
    Parsea el campo 'Interno' de caras, que puede ser:
      - None
      - [s11]
      - [s11, s22, s33]
    Devuelve lista de nombres de half-edges.
    """
    texto = texto.strip()
    if texto == 'None' or texto == '[]':
        return []
    # Quitar corchetes y separar por comas
    interior = re.sub(r'[\[\]]', '', texto)
    partes = [p.strip() for p in interior.split(',') if p.strip()]
    return partes


def leer_dcel(ruta_base):
    """
    Lee los tres archivos DCEL dado el prefijo de ruta.
    Ejemplo: leer_dcel('datos/layer01') buscará:
      datos/layer01.vertices
      datos/layer01.aristas
      datos/layer01.caras

    Retorna una instancia de DCEL completamente enlazada.
    """
    dcel = DCEL()

    # ── 1. VÉRTICES ──────────────────────────────────────────────────────────
    ruta_v = ruta_base + '.vertices'
    incidentes_v = {}   # nombre_vertice -> nombre_half_edge incidente

    try:
        with open(ruta_v, 'r', encoding='utf-8') as f:
            for linea in f:
                if not _es_linea_datos(linea):
                    continue
                partes = linea.split()
                if len(partes) < 4:
                    continue
                nombre, x, y, incidente = partes[0], partes[1], partes[2], partes[3]
                dcel.agregar_vertice(nombre, x, y)
                incidentes_v[nombre] = incidente
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_v}")

    # ── 2. ARISTAS (primera pasada: crear objetos) ────────────────────────────
    ruta_a = ruta_base + '.aristas'
    # Guardamos los nombres para enlazar en segunda pasada
    datos_aristas = {}   # nombre -> (origen, pareja, cara, sigue, antes)

    try:
        with open(ruta_a, 'r', encoding='utf-8') as f:
            for linea in f:
                if not _es_linea_datos(linea):
                    continue
                partes = linea.split()
                if len(partes) < 6:
                    continue
                nombre = partes[0]
                origen, pareja, cara, sigue, antes = partes[1], partes[2], partes[3], partes[4], partes[5]
                dcel.agregar_half_edge(nombre)
                datos_aristas[nombre] = (origen, pareja, cara, sigue, antes)
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_a}")

    # ── 3. CARAS ──────────────────────────────────────────────────────────────
    ruta_c = ruta_base + '.caras'
    datos_caras = {}   # nombre -> (lista_internas, externo)

    try:
        with open(ruta_c, 'r', encoding='utf-8') as f:
            for linea in f:
                if not _es_linea_datos(linea):
                    continue
                # El campo Interno puede tener espacios dentro de los corchetes
                # Usamos regex para separar correctamente
                m = re.match(r'(\S+)\s+(\[.*?\]|None)\s+(\S+)', linea.strip())
                if not m:
                    continue
                nombre = m.group(1)
                interno_str = m.group(2)
                externo_str = m.group(3)
                dcel.agregar_cara(nombre)
                datos_caras[nombre] = (_parsear_lista_aristas(interno_str), externo_str)
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_c}")

    # ── 4. ENLAZAR TODO ───────────────────────────────────────────────────────

    # Enlazar vértices con su half-edge incidente
    for nombre_v, nombre_he in incidentes_v.items():
        v = dcel.vertices[nombre_v]
        he = dcel.half_edges.get(nombre_he)
        v.incidente = he

    # Enlazar half-edges
    for nombre_he, (origen, pareja, cara, sigue, antes) in datos_aristas.items():
        he = dcel.half_edges[nombre_he]
        he.origen    = dcel.vertices.get(origen)
        he.pareja    = dcel.half_edges.get(pareja)
        he.cara      = dcel.caras.get(cara)
        he.siguiente = dcel.half_edges.get(sigue)
        he.anterior  = dcel.half_edges.get(antes)

    # Enlazar caras
    for nombre_cara, (internas, externo_str) in datos_caras.items():
        cara = dcel.caras[nombre_cara]
        # Arista externa (la que define el borde del polígono)
        if externo_str != 'None':
            cara.externa = dcel.half_edges.get(externo_str)
        # Aristas internas (holes)
        cara.internas = [dcel.half_edges[n] for n in internas if n in dcel.half_edges]

    return dcel
