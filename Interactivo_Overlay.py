import pygame
import sys
import os
from src.LectorDCEL import leer_dcel
from MapOverlay import construir_overlay_n_capas, exportar_overlay
from ConstructorCaras import construir_caras
from Visualizador_Overlay import visualizar_overlay

# =============================================================================
# CONFIGURACIÓN DEL PROYECTO
# =============================================================================
CAPAS_A_COMBINAR = [
    "datos/layer01",
    "datos/layer02",
    "datos/layer03",
    'datos/layer04',
    'datos/layer05',
    'datos/layer07'
]
NOMBRE_SALIDA = "analisis_multicapa_panamericana"
# =============================================================================

# Configuración Estética
COLOR_FONDO_INACTIVO = (15, 15, 25)
COLOR_FONDO_HOVER = (40, 40, 60)
COLOR_FONDO_ACTIVO = (60, 60, 90)
COLOR_UI_BG = (30, 30, 50, 220)
COLOR_TEXTO = (220, 220, 255)
COLOR_VERTICE = (255, 255, 0)
COLOR_ARISTA_BORDE = (150, 150, 170, 200)

PALETA_CARAS = [
    (81, 45, 168, 180), (0, 121, 107, 180), (230, 81, 0, 180),
    (194, 24, 91, 180), (56, 142, 60, 180),
]


# ─────────────────────────────────────────────────────────────
# UTILIDADES MATEMÁTICAS
# ─────────────────────────────────────────────────────────────

def area_poligono(vertices):
    if len(vertices) < 3: return 0.0
    return abs(sum(vertices[i].x * vertices[(i + 1) % len(vertices)].y -
                   vertices[(i + 1) % len(vertices)].x * vertices[i].y
                   for i in range(len(vertices))) / 2.0)


def punto_en_poligono_wn(x, y, vertices):
    wn = 0
    n = len(vertices)
    for i in range(n):
        p1, p2 = vertices[i], vertices[(i + 1) % n]
        if p1.y <= y:
            if p2.y > y and (p2.x - p1.x) * (y - p1.y) - (x - p1.x) * (p2.y - p1.y) > 0: wn += 1
        elif p2.y <= y and (p2.x - p1.x) * (y - p1.y) - (x - p1.x) * (p2.y - p1.y) < 0:
            wn -= 1
    return wn != 0


def punto_en_cara(x, y, cara):
    v_ext = cara.vertices()
    if not v_ext or not punto_en_poligono_wn(x, y, v_ext): return False
    for h_int in cara.internas:
        if punto_en_poligono_wn(x, y, [h.origen for h in h_int.ciclo()]): return False
    return True


# ─────────────────────────────────────────────────────────────
# CONTROL DE CÁMARA
# ─────────────────────────────────────────────────────────────

class Viewport:
    def __init__(self, w, h):
        self.scale = 35.0
        self.off_x = w // 2 - 150
        self.off_y = h // 2 + 100
        self.drag = False
        self.last_pos = (0, 0)

    def transformar(self, x, y):
        return int(self.off_x + x * self.scale), int(self.off_y - y * self.scale)

    def destransformar(self, tx, ty):
        return (tx - self.off_x) / self.scale, (self.off_y - ty) / self.scale

    def manejar_evento(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 3: self.drag, self.last_pos = True, ev.pos
            if ev.button == 4: self.scale *= 1.1
            if ev.button == 5: self.scale *= 0.9
        elif ev.type == pygame.MOUSEBUTTONUP:
            if ev.button == 3: self.drag = False
        elif ev.type == pygame.MOUSEMOTION and self.drag:
            self.off_x += ev.pos[0] - self.last_pos[0]
            self.off_y += ev.pos[1] - self.last_pos[1]
            self.last_pos = ev.pos


# ─────────────────────────────────────────────────────────────
# BUCLE PRINCIPAL
# ─────────────────────────────────────────────────────────────

def ejecutar_interactivo():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Map Overlay N-Layers — Sistema Interactivo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 14, bold=True)

    print(f"[*] Iniciando fusión de {len(CAPAS_A_COMBINAR)} capas...")
    overlay = construir_overlay_n_capas(CAPAS_A_COMBINAR)
    construir_caras(overlay)

    exportar_overlay(overlay, NOMBRE_SALIDA)
    visualizar_overlay(overlay, ruta_salida=f"resultados/{NOMBRE_SALIDA}.png")

    view = Viewport(1280, 720)
    seleccionadas = set()
    hover_cara = 'C_inf'

    # NUEVA VARIABLE DE ESTADO PARA VÉRTICES
    mostrar_vertices = True

    caras_info = []
    idx_col = 0
    for nombre, cara in overlay.caras.items():
        if nombre == 'C_inf': continue
        v = cara.vertices()
        if len(v) >= 3:
            caras_info.append({'area': area_poligono(v), 'nombre': nombre, 'cara': cara, 'color_idx': idx_col})
            idx_col += 1

    caras_deteccion = sorted(caras_info, key=lambda x: x['area'])
    caras_dibujo = sorted(caras_info, key=lambda x: x['area'], reverse=True)

    print("\n[!] Sistema listo para inspección.")

    while True:
        mx, my = view.destransformar(*pygame.mouse.get_pos())

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            view.manejar_evento(ev)

            if ev.type == pygame.KEYDOWN:
                # Toggle de Vértices con la tecla 'V'
                if ev.key == pygame.K_v:
                    mostrar_vertices = not mostrar_vertices

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if hover_cara:
                    if hover_cara in seleccionadas:
                        seleccionadas.remove(hover_cara)
                    else:
                        seleccionadas.add(hover_cara)

        hover_cara = 'C_inf'
        for ci in caras_deteccion:
            if punto_en_cara(mx, my, ci['cara']):
                hover_cara = ci['nombre']
                break

        bg_color = COLOR_FONDO_INACTIVO
        if 'C_inf' in seleccionadas:
            bg_color = COLOR_FONDO_ACTIVO
        elif hover_cara == 'C_inf':
            bg_color = COLOR_FONDO_HOVER
        screen.fill(bg_color)

        for ci in caras_dibujo:
            pts = [view.transformar(v.x, v.y) for v in ci['cara'].vertices()]

            if ci['nombre'] in seleccionadas or ci['nombre'] == hover_cara:
                color = list(PALETA_CARAS[ci['color_idx'] % len(PALETA_CARAS)])
                if ci['nombre'] == hover_cara and ci['nombre'] not in seleccionadas:
                    color[3] = 100
            else:
                color = (0, 0, 0, 255)

            s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(s, color, pts)
            pygame.draw.polygon(s, COLOR_ARISTA_BORDE, pts, 2)
            screen.blit(s, (0, 0))

        # DIBUJAR VÉRTICES (Ahoracontrolado por la variable)
        if mostrar_vertices:
            for v in overlay.vertices.values():
                pos = view.transformar(v.x, v.y)
                pygame.draw.circle(screen, COLOR_VERTICE, pos, 4)
                screen.blit(font.render(v.nombre, True, COLOR_VERTICE), (pos[0] + 8, pos[1] - 8))

        ui = pygame.Surface((420, 200), pygame.SRCALPHA);
        ui.fill(COLOR_UI_BG)
        screen.blit(ui, (15, 15))

        info = [
            f"PROYECTO: {NOMBRE_SALIDA}",
            f"CAPAS PROCESADAS: {len(CAPAS_A_COMBINAR)}",
            f"VÉRTICES TOTALES: {len(overlay.vertices)}",
            f"ARISTAS TOTALES:  {len(overlay.half_edges)}",
            "---------------------------------------",
            f"[V] Vértices: {'ON' if mostrar_vertices else 'OFF'}",  # Indicador UI agregado
            f"HOVER ACTUAL: {hover_cara}",
            f"SELECCIONADAS: {len(seleccionadas)}",
            "CLICK IZQ: Seleccionar | DER: Pan"
        ]
        for i, texto in enumerate(info):
            # Cambiamos un poquito el color si el switch está encendido para destacarlo
            color_txt = (150, 255, 150) if "ON" in texto else COLOR_TEXTO
            screen.blit(font.render(texto, True, color_txt), (30, 30 + i * 18))

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    ejecutar_interactivo()