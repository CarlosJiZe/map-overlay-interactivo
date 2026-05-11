from src.LectorDCEL import leer_dcel
from MapOverlay import construir_overlay, exportar_overlay
from ConstructorCaras import construir_caras
from Visualizador_Overlay import visualizar_overlay


def imprimir_dcel(dcel, nombre):
    print(f"\n── {nombre} ──────────────────────────────")
    print(f"  Vértices  : {len(dcel.vertices)}")
    for n, v in dcel.vertices.items():
        print(f"    {n}: ({v.x}, {v.y})")
    print(f"  Half-edges: {len(dcel.half_edges)}")
    for n, he in dcel.half_edges.items():
        orig = he.origen.nombre    if he.origen    else '?'
        dest = he.destino().nombre if he.destino() else '?'
        print(f"    {n}: {orig} → {dest}")


def imprimir_overlay(overlay):
    print("\n── RESULTADO OVERLAY ──────────────────────────────")
    print(f"\n  Vértices ({len(overlay.vertices)}):")
    for nombre, v in overlay.vertices.items():
        print(f"    {nombre}: ({v.x:.4f}, {v.y:.4f})")

    print(f"\n  Half-edges ({len(overlay.half_edges)}):")
    for nombre, he in overlay.half_edges.items():
        orig = he.origen.nombre    if he.origen    else '?'
        dest = he.destino().nombre if he.destino() else '?'
        twin = he.pareja.nombre    if he.pareja    else 'None'
        sig  = he.siguiente.nombre if he.siguiente else 'None'
        ant  = he.anterior.nombre  if he.anterior  else 'None'
        print(f"    {nombre}: {orig}→{dest}  "
              f"| twin={twin}  next={sig}  prev={ant}")


if __name__ == '__main__':

    # ── 1. Cargar capas ───────────────────────────────────────
    dcel1 = leer_dcel('datos/layer04')
    dcel2 = leer_dcel('datos/layer05')

    imprimir_dcel(dcel1, "Layer04")
    imprimir_dcel(dcel2, "Layer05")

    # ── 2. Construir overlay ──────────────────────────────────
    overlay, _ = construir_overlay(dcel1, dcel2)
    imprimir_overlay(overlay)

    # ── 3. Construir caras ────────────────────────────────────
    construir_caras(overlay)

    # ── 4. Exportar archivos ──────────────────────────────────
    exportar_overlay(overlay, 'overlay_layer04_layer05')

    # ── 5. Visualizar ─────────────────────────────────────────
    visualizar_overlay(
        overlay,
        titulo='Map Overlay — Layer04 + Layer05',
        ruta_salida='resultados/overlay_layer04_layer05.png'
    )