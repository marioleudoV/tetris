import pygame
import random
import numpy as np

# Configuraciones iniciales
ANCHO = 800
ALTO = 600
TAMANO_CUADRICULA = 30
COLUMNAS = 10
FILAS = 20

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
NARANJA = (255, 165, 0)
MORADO = (128, 0, 128)

COLORES_PIEZAS = [ROJO, VERDE, AZUL, AMARILLO, NARANJA, MORADO]

class Pieza:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(COLORES_PIEZAS)
        # Crear una pieza de 3x3
        self.forma = np.zeros((3, 3), dtype=int)
        self.crear_forma_aleatoria()
        
    def crear_forma_aleatoria(self):
        # Generar una forma aleatoria dentro de una cuadrícula 3x3
        for i in range(3):
            for j in range(3):
                self.forma[i][j] = random.randint(0, 1)
        
        # Asegurar que haya al menos un bloque
        if np.sum(self.forma) == 0:
            self.forma[1][1] = 1
    
    def rotar(self):
        # Rotar la pieza 90 grados
        self.forma = np.rot90(self.forma)
        
class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Tetris Modificado")
        self.reloj = pygame.time.Clock()
        
        # Estado del juego
        self.grid = np.zeros((FILAS, COLUMNAS), dtype=int)
        self.pieza_actual = None
        self.puntos = 0
        self.tiempo_caida = 0
        self.velocidad_caida = 500  # milisegundos
        
        # Fuente para puntuación
        self.fuente = pygame.font.Font(None, 36)
        
    def nueva_pieza(self):
        # Comenzar en la parte superior central
        self.pieza_actual = Pieza(COLUMNAS // 2 - 1, 0)
    
    def dibujar_fondo_ladrillos(self):
        # Dibujar un fondo de ladrillos
        for y in range(0, ALTO, TAMANO_CUADRICULA * 2):
            for x in range(0, ANCHO, TAMANO_CUADRICULA * 2):
                # Dibujar ladrillo
                pygame.draw.rect(self.pantalla, (139, 69, 19), 
                                 (x, y, TAMANO_CUADRICULA*2, TAMANO_CUADRICULA*2))
                pygame.draw.rect(self.pantalla, (165, 42, 42), 
                                 (x, y, TAMANO_CUADRICULA*2, TAMANO_CUADRICULA*2), 2)
    
    def dibujar(self):
        self.pantalla.fill(NEGRO)
        self.dibujar_fondo_ladrillos()
        
        # Dibujar grid
        for y in range(FILAS):
            for x in range(COLUMNAS):
                rect = pygame.Rect(x * TAMANO_CUADRICULA, y * TAMANO_CUADRICULA, 
                                   TAMANO_CUADRICULA, TAMANO_CUADRICULA)
                pygame.draw.rect(self.pantalla, BLANCO, rect, 1)
        
        # Dibujar pieza actual
        if self.pieza_actual:
            for y in range(3):
                for x in range(3):
                    if self.pieza_actual.forma[y][x]:
                        rect = pygame.Rect(
                            (self.pieza_actual.x + x) * TAMANO_CUADRICULA,
                            (self.pieza_actual.y + y) * TAMANO_CUADRICULA,
                            TAMANO_CUADRICULA, TAMANO_CUADRICULA
                        )
                        pygame.draw.rect(self.pantalla, self.pieza_actual.color, rect)
        
        # Dibujar puntuación
        texto_puntos = self.fuente.render(f"Puntos: {self.puntos}", True, BLANCO)
        self.pantalla.blit(texto_puntos, (ANCHO - 200, 20))
        
        pygame.display.flip()
    
    def mover(self, dx):
        if self.pieza_actual:
            self.pieza_actual.x += dx
            # Verificar colisiones con bordes
            if self.colision():
                self.pieza_actual.x -= dx
    
    def colision(self):
        # Verificar colisiones con bordes y otras piezas
        for y in range(3):
            for x in range(3):
                if self.pieza_actual.forma[y][x]:
                    nx = self.pieza_actual.x + x
                    ny = self.pieza_actual.y + y
                    
                    # Verificar bordes
                    if (nx < 0 or nx >= COLUMNAS or 
                        ny >= FILAS):
                        return True
        return False
    
    def fijar_pieza(self):
        # Fijar la pieza actual en el grid
        for y in range(3):
            for x in range(3):
                if self.pieza_actual.forma[y][x]:
                    nx = self.pieza_actual.x + x
                    ny = self.pieza_actual.y + y
                    
                    if 0 <= nx < COLUMNAS and 0 <= ny < FILAS:
                        self.grid[ny][nx] = 1
        
        # Verificar eliminación de líneas del mismo color
        self.eliminar_lineas_color()
        
        # Crear nueva pieza
        self.nueva_pieza()
    
    def eliminar_lineas_color(self):
        # Eliminar líneas con 3 piezas del mismo color
        for y in range(FILAS):
            colores_fila = [self.grid[y][x] for x in range(COLUMNAS)]
            if len(set(colores_fila)) == 1 and colores_fila[0] != 0:
                # Eliminar fila y añadir puntos
                del self.grid[y]
                self.grid.insert(0, np.zeros(COLUMNAS, dtype=int))
                self.puntos += 100
    
    def caer(self):
        if self.pieza_actual:
            self.pieza_actual.y += 1
            
            # Verificar colisión al caer
            if self.colision():
                # Revertir caída
                self.pieza_actual.y -= 1
                # Fijar pieza
                self.fijar_pieza()
    
    def jugar(self):
        self.nueva_pieza()
        corriendo = True
        
        while corriendo:
            # Control de tiempo para caída
            tiempo_actual = pygame.time.get_ticks()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_LEFT:
                        self.mover(-1)
                    elif evento.key == pygame.K_RIGHT:
                        self.mover(1)
                    elif evento.key == pygame.K_SPACE:
                        # Rotar pieza
                        self.pieza_actual.rotar()
                        if self.colision():
                            # Revertir rotación si hay colisión
                            self.pieza_actual.rotar()
                            self.pieza_actual.rotar()
                            self.pieza_actual.rotar()
            
            # Caída automática
            if tiempo_actual - self.tiempo_caida > self.velocidad_caida:
                self.caer()
                self.tiempo_caida = tiempo_actual
            
            # Dibujar
            self.dibujar()
            
            # Verificar fin del juego (base llena)
            if np.all(self.grid[FILAS-1]):
                print("¡Juego Terminado!")
                corriendo = False
            
            self.reloj.tick(10)
        
        pygame.quit()

# Iniciar juego
if __name__ == "__main__":
    juego = Juego()
    juego.jugar()