import pygame
import random
import sys
import math

# Inicializar Pygame
pygame.init()

# Configuraciones de la ventana
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cuadrado, Círculo y Vector de Distancia")

# Colores
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Configuraciones del juego
square_size = 50
circle_radius = 25
speed_x = 2
speed_y = 2
wall_width = 20

clock = pygame.time.Clock()

# Posiciones iniciales aleatorias
def random_positions():
    circle_x = random.randint(circle_radius, width - circle_radius)
    square_x = random.randint(square_size, width - square_size)

    # Asegurarse de que el círculo y el cuadrado estén en lados opuestos del muro
    if circle_x < width // 2:
        square_x = random.randint(width // 2 + wall_width, width - square_size)
    else:
        square_x = random.randint(0, width // 2 - wall_width - square_size)

    return circle_x, random.randint(circle_radius, height - circle_radius), square_x, random.randint(square_size, height - square_size)

circle_x, circle_y, square_x, square_y = random_positions()

# Función para reiniciar el juego
def restart_game():
    global circle_x, circle_y, square_x, square_y
    circle_x, circle_y, square_x, square_y = random_positions()

# Calcular distancia y vector de dirección
def calculate_distance_and_vector(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    vector = (x2 - x1, y2 - y1)
    return distance, vector

# Bucle principal del juego
running = True
font = pygame.font.SysFont(None, 30)
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                restart_game()

    # Mover el círculo hacia el cuadrado
    distance, vector = calculate_distance_and_vector(circle_x, circle_y, square_x, square_y)
    if distance > speed_x:
        circle_x += speed_x * (vector[0] / distance)
        circle_y += speed_y * (vector[1] / distance)
        print(vector[0], vector[1])

    # Dibujar elementos
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (square_x, square_y, square_size, square_size))  # Cuadrado azul
    pygame.draw.circle(screen, RED, (int(circle_x), int(circle_y)), circle_radius)  # Círculo rojo
     
    # Calcular y mostrar distancia y vector
    distance, _ = calculate_distance_and_vector(circle_x, circle_y, square_x, square_y)
    mid_x, mid_y = (circle_x + square_x) // 2, (circle_y + square_y) // 2
    distance_text = font.render(f"{int(distance)}px", True, WHITE)
    screen.blit(distance_text, (mid_x, mid_y))
    pygame.draw.line(screen, WHITE, (circle_x, circle_y), (square_x, square_y), 1)

    # Actualizar pantalla
    pygame.display.update()

# Salir de Pygame
pygame.quit()
sys.exit()
