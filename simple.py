import pygame
import random
import sys
from pynput.keyboard import Key, Controller
import time
import threading
import math

# Inicializar Pygame
pygame.init()

# Configuraciones de la ventana
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cuadrado, Círculo, Muro y Vector de Distancia")

# Inicializar el controlador de teclado de pynput
keyboard = Controller()

# Colores
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Configuraciones del juego
square_size = 50
circle_radius = 25
speed = 5

# Modos de control
manual_mode = True

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

# Función para mover el círculo automáticamente
def move_circle_automatically():
  global circle_x, circle_y
  if circle_x < square_x:
    # press_key(Key.right)
    circle_x += speed

  elif circle_x > square_x:
    # press_key(Key.left)
    circle_x -= speed

  if circle_y < square_y:
    # press_key(Key.down)
    circle_y += speed

  elif circle_y > square_y:
    # press_key(Key.up)
    circle_y -= speed


def press_key(key):
  print(key)
  keyboard.press(key)
  time.sleep(0.1)
  keyboard.release(key)

def pressed_key(keys):
  global circle_x, circle_y
  if keys[pygame.K_LEFT]:
    circle_x -= speed
    
  if keys[pygame.K_RIGHT]:
    circle_x += speed
    
  if keys[pygame.K_UP]:
    circle_y -= speed
    
  if keys[pygame.K_DOWN]:
    circle_y += speed
    
# Calcular distancia y vector de dirección
def calculate_distance_and_vector(x1, y1, x2, y2):
  distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
  vector = (x2 - x1, y2 - y1)
  return distance, vector

# Iniciar el hilo para el movimiento automático
auto_move_thread = threading.Thread(target=move_circle_automatically())
auto_move_thread.daemon = True  # Esto hará que el hilo se cierre cuando se cierre el programa
auto_move_thread.start()

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
      elif event.key == pygame.K_h:
        manual_mode = not manual_mode

    if manual_mode:
      keys = pygame.key.get_pressed()
      pressed_key(keys)
    else:
      # Modo automático
      move_circle_automatically()

    # Mantener el círculo dentro del tablero
    circle_x = max(min(circle_x, width - circle_radius), circle_radius)
    circle_y = max(min(circle_y, height - circle_radius), circle_radius)

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
