from src.DCEL import Cara


# ─────────────────────────────────────────────────────────────
# PASO 1: EXTRACCIÓN DE CICLOS
# ─────────────────────────────────────────────────────────────

def extraer_ciclos(dcel):
    """
    Recorre todas las half-edges siguiendo el puntero .siguiente
    y agrupa las que pertenecen al mismo ciclo.

    Retorna lista de listas de HalfEdge.
    """
    visitados = set()
    ciclos = []

    for nombre, he_inicio in dcel.half_edges.items():
        if nombre in visitados:
            continue

        ciclo = []
        actual = he_inicio
        while True:
            if actual is None or actual.nombre in visitados:
                break
            ciclo.append(actual)
            visitados.add(actual.nombre)
            actual = actual.siguiente
            if actual is he_inicio:
                break

        if ciclo:
            ciclos.append(ciclo)

    return ciclos


# ─────────────────────────────────────────────────────────────
# PASO 2: CLASIFICAR CICLOS
# ─────────────────────────────────────────────────────────────

def area_con_signo(ciclo):
    """
    Fórmula de Shoelace sobre el ciclo.
    Resultado positivo → CCW → ciclo INTERNO (borde de cara acotada).
    Resultado negativo → CW  → ciclo EXTERNO (cara infinita o agujero).
    """
    area = 0.0
    for he in ciclo:
        x1, y1 = he.origen.x, he.origen.y
        x2, y2 = he.destino().x, he.destino().y
        area += (x1 * y2 - x2 * y1)
    return area / 2.0


def clasificar_ciclos(ciclos):
    """
    Devuelve lista de dicts con:
        ciclo, tipo (INTERNO|EXTERNO), area, he_izq, cara
    """
    resultado = []
    for ciclo in ciclos:
        area   = area_con_signo(ciclo)
        he_izq = min(ciclo, key=lambda he: (he.origen.x, he.origen.y))
        tipo   = 'INTERNO' if area > 0 else 'EXTERNO'
        resultado.append({
            'ciclo'  : ciclo,
            'tipo'   : tipo,
            'area'   : area,
            'he_izq' : he_izq,
            'cara'   : None,
        })
    return resultado


# ─────────────────────────────────────────────────────────────
# PASO 3: GRAFO DE CARAS — RAY CASTING
# ─────────────────────────────────────────────────────────────

def encontrar_contenedor(he_izq, ciclos_info, idx_actual):
    """
    Lanza un rayo horizontal hacia la izquierda desde el vértice
    más izquierdo del ciclo EXTERNO.

    Encuentra la half-edge más cercana a la izquierda que cruza
    el rayo, y devuelve el índice del ciclo al que pertenece.
    Si no hay ninguna → None (ciclo conecta a la cara infinita).
    """
    vx      = he_izq.origen.x
    vy      = he_izq.origen.y
    epsilon = 1e-9

    mejor_x   = -float('inf')
    mejor_idx = None

    for idx, info in enumerate(ciclos_info):
        if idx == idx_actual:
            continue
        for he in info['ciclo']:
            y1, y2 = he.origen.y, he.destino().y
            x1, x2 = he.origen.x, he.destino().x

            # Condición de cruce: un extremo ≤ vy, el otro > vy
            # (evita contar dos veces un vértice exactamente sobre el rayo)
            if not ((y1 <= vy < y2) or (y2 <= vy < y1)):
                continue

            t      = (vy - y1) / (y2 - y1)
            x_inter = x1 + t * (x2 - x1)

            # Solo nos interesan intersecciones a la izquierda de vx
            if x_inter < vx - epsilon and x_inter > mejor_x:
                mejor_x   = x_inter
                mejor_idx = idx

    return mejor_idx


# ─────────────────────────────────────────────────────────────
# PASOS 4 y 5: REGISTRAR CARAS Y ACTUALIZAR HALF-EDGES
# ─────────────────────────────────────────────────────────────

def construir_caras(dcel):
    """
    Aplica los 5 pasos del algoritmo de construcción de caras
    sobre el DCEL overlay y los registra en dcel.caras.

    Modifica el DCEL en sitio y lo devuelve.
    """
    print("\n" + "=" * 50)
    print("  CONSTRUCCIÓN DE CARAS")
    print("=" * 50)

    # ── 1. Extraer ciclos ────────────────────────────────────
    ciclos = extraer_ciclos(dcel)
    print(f"\n  Paso 1 — Ciclos encontrados: {len(ciclos)}")

    # ── 2. Clasificar ────────────────────────────────────────
    ciclos_info = clasificar_ciclos(ciclos)
    print(f"\n  Paso 2 — Clasificación:")
    for i, info in enumerate(ciclos_info):
        verts = [he.origen.nombre for he in info['ciclo']]
        print(f"    Ciclo {i}: {info['tipo']:8s} | "
              f"área={info['area']:9.4f} | {verts}")

    # ── 3. Grafo de caras ────────────────────────────────────
    grafo = {}
    print(f"\n  Paso 3 — Grafo de caras (ray casting):")
    for idx, info in enumerate(ciclos_info):
        if info['tipo'] == 'EXTERNO':
            cont = encontrar_contenedor(info['he_izq'], ciclos_info, idx)
            grafo[idx] = cont
            dest = f"Ciclo {cont}" if cont is not None else "INFINITO"
            print(f"    Ciclo {idx} (EXTERNO) → {dest}")

    # ── 4. Crear objetos Cara ────────────────────────────────
    cont_cara = [0]
    def nuevo_nombre():
        cont_cara[0] += 1
        return f"C{cont_cara[0]}"

    # Cara infinita
    cara_inf          = dcel.agregar_cara('C_inf')
    cara_inf.externa  = None
    cara_inf.internas = []

    # Una Cara por cada ciclo INTERNO (CCW)
    cara_de_ciclo = {}
    for idx, info in enumerate(ciclos_info):
        if info['tipo'] == 'INTERNO':
            cara          = dcel.agregar_cara(nuevo_nombre())
            cara.externa  = info['ciclo'][0]
            cara.internas = []
            cara_de_ciclo[idx] = cara
            info['cara']       = cara

    # ── 5. Conectar ciclos EXTERNOS a su cara padre ──────────
    for idx_ext, idx_cont in grafo.items():
        info_ext = ciclos_info[idx_ext]
        he_rep   = info_ext['ciclo'][0]

        if idx_cont is not None and idx_cont in cara_de_ciclo:
            cara_padre = cara_de_ciclo[idx_cont]
        else:
            cara_padre = cara_inf

        cara_padre.internas.append(he_rep)
        info_ext['cara'] = cara_padre

    # ── 6. Asignar cara a cada half-edge ─────────────────────
    for info in ciclos_info:
        cara = info.get('cara') or cara_inf
        for he in info['ciclo']:
            he.cara = cara

    # ── Resumen ───────────────────────────────────────────────
    print(f"\n  Paso 4/5 — Caras registradas: {len(dcel.caras)}")
    for nombre, cara in dcel.caras.items():
        ext  = cara.externa.nombre if cara.externa else 'None'
        ints = [he.nombre for he in cara.internas]
        print(f"    {nombre}: externa={ext}  internas={ints}")

    return dcel
