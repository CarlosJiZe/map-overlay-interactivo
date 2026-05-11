import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

plt.style.use('dark_background')

COLORES_CARAS = [
    '#4FC3F7', '#81C784', '#FFB74D', '#F48FB1',
    '#CE93D8', '#80DEEA', '#A5D6A7', '#FF8A65',
]


def _coords_ciclo(he_inicio):
    """Recorre el ciclo de half-edges y devuelve las coordenadas de los vértices."""
    coords, vis, actual = [], set(), he_inicio
    while actual and id(actual) not in vis:
        coords.append((actual.origen.x, actual.origen.y))
        vis.add(id(actual))
        actual = actual.siguiente
        if actual is he_inicio:
            break
    return coords


def visualizar_overlay(dcel, titulo='Map Overlay',
                        ruta_salida='resultados/overlay.png'):

    os.makedirs(os.path.dirname(ruta_salida) or '.', exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 11))
    fig.patch.set_facecolor('#1E1E2E')
    ax.set_facecolor('#1E1E2E')

    # ── Caras coloreadas ─────────────────────────────────────
    color_idx = 0
    for nombre, cara in dcel.caras.items():
        if nombre == 'C_inf' or cara.externa is None:
            continue

        coords = _coords_ciclo(cara.externa)
        if len(coords) < 2:
            continue

        color = COLORES_CARAS[color_idx % len(COLORES_CARAS)]
        color_idx += 1

        if len(coords) >= 3:
            ax.add_patch(MplPolygon(coords, closed=True,
                                    facecolor=color, alpha=0.30,
                                    edgecolor=color, linewidth=2.5,
                                    zorder=2))

        # Etiqueta de la cara en el centroide
        cx = sum(c[0] for c in coords) / len(coords)
        cy = sum(c[1] for c in coords) / len(coords)
        ax.text(cx, cy, nombre,
                ha='center', va='center',
                fontsize=13, fontweight='bold', color='white', zorder=6,
                bbox=dict(facecolor='#222244', alpha=0.85,
                          edgecolor='none', boxstyle='round,pad=0.35'))

    # ── Half-edges con flechas ───────────────────────────────
    for nombre, he in dcel.half_edges.items():
        if he.origen is None or he.destino() is None:
            continue

        x1, y1 = he.origen.x, he.origen.y
        x2, y2 = he.destino().x, he.destino().y

        dx, dy = x2 - x1, y2 - y1
        lng = math.sqrt(dx * dx + dy * dy)
        if lng < 1e-9:
            continue

        # Offset perpendicular para separar pares gemelos
        ox = -dy / lng * 0.13
        oy =  dx / lng * 0.13

        # Acortamos la flecha para no tapar los vértices
        trim = 0.13
        sx = x1 + ox + dx * trim
        sy = y1 + oy + dy * trim
        ex = x2 + ox - dx * trim
        ey = y2 + oy - dy * trim

        ax.annotate('',
                    xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(
                        arrowstyle='->',
                        color='#7777AA',
                        lw=1.1,
                        mutation_scale=11,
                    ),
                    zorder=4)

        # Nombre de la half-edge a mitad del segmento
        mx = (sx + ex) / 2 + ox * 1.2
        my = (sy + ey) / 2 + oy * 1.2
        ax.text(mx, my, nombre,
                ha='center', va='center',
                fontsize=6.5, color='#9999CC', zorder=5)

    # ── Vértices ─────────────────────────────────────────────
    for nombre, v in dcel.vertices.items():
        ax.plot(v.x, v.y, 'o',
                color='#FFEB3B', markersize=9,
                zorder=7, markeredgecolor='white', markeredgewidth=1.3)
        ax.text(v.x, v.y + 0.28, nombre,
                ha='center', va='bottom',
                fontsize=9, color='#FFEB3B', fontweight='bold', zorder=8)

    # ── Vista ────────────────────────────────────────────────
    xs = [v.x for v in dcel.vertices.values()]
    ys = [v.y for v in dcel.vertices.values()]
    dx_r = (max(xs) - min(xs)) or 10
    dy_r = (max(ys) - min(ys)) or 10
    mg   = max(dx_r, dy_r) * 0.22

    ax.set_xlim(min(xs) - mg, max(xs) + mg)
    ax.set_ylim(min(ys) - mg, max(ys) + mg)
    ax.set_aspect('equal')
    ax.grid(True, color='#333355', linestyle=':', alpha=0.4)
    ax.set_title(titulo, color='white', fontsize=15, pad=14)
    ax.tick_params(colors='#AAAACC')
    for spine in ax.spines.values():
        spine.set_edgecolor('#444466')

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, facecolor='#1E1E2E')
    plt.close()
    print(f"\n[Visual] Imagen guardada en: {ruta_salida}")
