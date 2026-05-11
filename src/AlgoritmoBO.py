import heapq
from src.Evento import Evento
from src.Punto import Punto
from src.LineaBarridoBO import LineaBarridoBO


def obtener_extremo_superior(segmento):
    epsilon = 1e-9
    if abs(segmento.p1.y - segmento.p2.y) > epsilon:
        return segmento.p1 if segmento.p1.y > segmento.p2.y else segmento.p2
    return segmento.p1 if segmento.p1.x < segmento.p2.x else segmento.p2


def obtener_extremo_inferior(segmento):
    epsilon = 1e-9
    if abs(segmento.p1.y - segmento.p2.y) > epsilon:
        return segmento.p1 if segmento.p1.y < segmento.p2.y else segmento.p2
    return segmento.p1 if segmento.p1.x > segmento.p2.x else segmento.p2


def es_horizontal(seg):
    return abs(seg.p1.y - seg.p2.y) < 1e-9


def agregar_punto_unico(R, R_index, punto, segmentos_involucrados):
    clave = (round(punto.x, 7), round(punto.y, 7))
    if clave in R_index:
        punto_clave = R_index[clave]
    else:
        punto_clave = punto
        R_index[clave] = punto_clave
        R[punto_clave] = []

    existentes = set(R[punto_clave])
    for seg in segmentos_involucrados:
        if seg not in existentes:
            R[punto_clave].append(seg)
            existentes.add(seg)


def encuentra_eventos(sl, sr, p, Q, eventos_agregados):
    if sl is None or sr is None: return
    if es_horizontal(sl) or es_horizontal(sr): return

    resultado = sl.interseccion(sr)

    # DETECCIÓN DE COLINEALES/SOLAPAMIENTO
    if resultado == "Son paralelas":
        try:
            dist = sr.aLinea().distancia_a_punto(sl.p1)
        except:
            dist = 1.0
        if dist < 1e-9:
            puntos_colineales = []
            if sr.punto_esta_en_segmento(sl.p1): puntos_colineales.append(sl.p1)
            if sr.punto_esta_en_segmento(sl.p2): puntos_colineales.append(sl.p2)
            if sl.punto_esta_en_segmento(sr.p1): puntos_colineales.append(sr.p1)
            if sl.punto_esta_en_segmento(sr.p2): puntos_colineales.append(sr.p2)
            for pt in puntos_colineales:
                clave = (round(pt.x, 7), round(pt.y, 7))
                if clave not in eventos_agregados:
                    heapq.heappush(Q, Evento(pt, 'INTERSECCION', [sl, sr]))
                    eventos_agregados.add(clave)
        return

    if resultado == "No se intersectan": return

    punto_inter = resultado
    epsilon = 1e-9
    if punto_inter.y < p.y - epsilon:
        pass
    elif abs(punto_inter.y - p.y) < epsilon:
        if punto_inter.x > p.x + epsilon:
            pass
        else:
            return
    else:
        return

    clave = (round(punto_inter.x, 7), round(punto_inter.y, 7))
    if clave in eventos_agregados: return

    heapq.heappush(Q, Evento(punto_inter, 'INTERSECCION', [sl, sr]))
    eventos_agregados.add(clave)


def procesa_evento_horizontal(seg_h, p, T, R, R_index, Q, eventos_agregados, horizontales_activos, h_by_right):
    x_min_h = min(seg_h.p1.x, seg_h.p2.x)
    x_max_h = max(seg_h.p1.x, seg_h.p2.x)
    y_h = seg_h.p1.y

    cruzados = T.segmentos_en_rango_x(x_min_h, x_max_h)
    for seg in cruzados:
        if seg is seg_h: continue
        inter = seg_h.interseccion(seg)
        if inter != "Son paralelas" and inter != "No se intersectan":
            agregar_punto_unico(R, R_index, inter, [seg_h, seg])

    # Intersección entre horizontales (Caso 3)
    epsilon = 1e-7
    for other_h in list(horizontales_activos):
        if other_h is seg_h: continue
        if abs(other_h.p1.y - y_h) > epsilon: continue

        x_min_o = min(other_h.p1.x, other_h.p2.x)
        x_max_o = max(other_h.p1.x, other_h.p2.x)

        if x_min_h > x_max_o + epsilon or x_min_o > x_max_h + epsilon: continue

        # Puntos de contacto
        pts = []
        if x_min_o - epsilon <= x_min_h <= x_max_o + epsilon: pts.append(Punto(x_min_h, y_h))
        if x_min_o - epsilon <= x_max_h <= x_max_o + epsilon: pts.append(Punto(x_max_h, y_h))
        if x_min_h - epsilon <= x_min_o <= x_max_h + epsilon: pts.append(Punto(x_min_o, y_h))
        if x_min_h - epsilon <= x_max_o <= x_max_h + epsilon: pts.append(Punto(x_max_o, y_h))

        for pt in pts: agregar_punto_unico(R, R_index, pt, [seg_h, other_h])

    horizontales_activos.add(seg_h)


def procesa_evento(p, T, R, R_index, Q, eventos_agregados, punto_a_segs_sup, punto_a_segs_inf, horizontales_activos,
                   segmentos_c=None):
    clave_p = (round(p.x, 7), round(p.y, 7))
    U = punto_a_segs_sup.get(clave_p, [])
    U_horizontal = [s for s in U if es_horizontal(s)]
    U_normal = [s for s in U if not es_horizontal(s)]
    L = punto_a_segs_inf.get(clave_p, [])
    C = segmentos_c if segmentos_c else []

    # ── FIX: DETECCIÓN DE T-JUNCTIONS (Puntos sobre aristas) ──
    # Atrapa los segmentos de la línea de barrido que contienen a 'p' en su interior
    # pero cuya intersección fue ignorada porque 'p' ya era un vértice conocido.
    candidatos_C = T.segmentos_en_rango_x(p.x - 1e-7, p.x + 1e-7)
    for seg in candidatos_C:
        if seg not in U and seg not in L and seg not in C:
            if seg.punto_esta_en_segmento(p):
                C.append(seg)
    # ──────────────────────────────────────────────────────────

    L_normal = [s for s in L if not es_horizontal(s)]

    todos = list(set(U_normal + U_horizontal + L + C))
    if len(todos) > 1: agregar_punto_unico(R, R_index, p, todos)

    for seg_h in U_horizontal:
        procesa_evento_horizontal(seg_h, p, T, R, R_index, Q, eventos_agregados, horizontales_activos, None)

    for seg in L:
        if es_horizontal(seg): horizontales_activos.discard(seg)

    # LÓGICA DE GAP (VECINOS ANTES DE BORRAR)
    sl_outer, sr_outer = None, None
    remover = L_normal + C
    if remover and not (U_normal + C):  # Solo si se crea un hueco
        remover_wrappers = []
        for seg in remover:
            if seg in T._mapa: remover_wrappers.append(T._mapa[seg])
        if remover_wrappers:
            remover_wrappers.sort(key=lambda w: T._x_at_y(w.segmento))
            item_left = T.vecino_izquierdo(remover_wrappers[0].segmento)
            item_right = T.vecino_derecho(remover_wrappers[-1].segmento)
            sl_outer = item_left
            sr_outer = item_right

    for seg in remover: T.eliminar(seg)

    T.actualizar_y(p.y - 1e-8)

    insertar = U_normal + C
    for seg in insertar: T.insertar(seg)

    if not insertar:
        # Si se creó un hueco, los vecinos externos ahora son adyacentes
        if sl_outer and sr_outer:
            encuentra_eventos(sl_outer, sr_outer, p, Q, eventos_agregados)
    else:
        # Verificar nuevos adyacentes
        s_prima = min(insertar, key=lambda s: T._x_at_y(s))
        s_doble_prima = max(insertar, key=lambda s: T._x_at_y(s))

        sl = T.vecino_izquierdo(s_prima)
        if sl: encuentra_eventos(sl, s_prima, p, Q, eventos_agregados)

        sr = T.vecino_derecho(s_doble_prima)
        if sr: encuentra_eventos(s_doble_prima, sr, p, Q, eventos_agregados)


def bentley_ottmann(segmentos):
    Q = []
    T = LineaBarridoBO()
    R = {}
    R_index = {}
    eventos_agregados = set()
    horizontales_activos = set()
    punto_a_segs_sup = {}
    punto_a_segs_inf = {}

    for seg in segmentos:
        sup = obtener_extremo_superior(seg)
        inf = obtener_extremo_inferior(seg)
        clave_sup = (round(sup.x, 7), round(sup.y, 7))
        clave_inf = (round(inf.x, 7), round(inf.y, 7))
        punto_a_segs_sup.setdefault(clave_sup, []).append(seg)
        punto_a_segs_inf.setdefault(clave_inf, []).append(seg)

        if clave_sup not in eventos_agregados:
            heapq.heappush(Q, Evento(sup, 'SUPERIOR'))
            eventos_agregados.add(clave_sup)
        if clave_inf not in eventos_agregados:
            heapq.heappush(Q, Evento(inf, 'INFERIOR'))
            eventos_agregados.add(clave_inf)

    while Q:
        evento = heapq.heappop(Q)
        p = evento.punto
        segmentos_c = evento.segmentos if evento.tipo == 'INTERSECCION' else []
        T.actualizar_y(p.y)
        procesa_evento(p, T, R, R_index, Q, eventos_agregados, punto_a_segs_sup, punto_a_segs_inf, horizontales_activos,
                       segmentos_c)

    return R