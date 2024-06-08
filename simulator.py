import pygame
import os
import math

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1540, 800
ROBOT_WIDTH, ROBOT_HEIGHT = 120, 165
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED) #| pygame.FULLSCREEN)
pygame.display.set_caption("Simulator")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

FPS = 60
VEL = 5

MARKER_IMAGE = pygame.image.load(os.path.join("assets", "aruco_11.png"))
MARKER = pygame.transform.scale(MARKER_IMAGE, (100, 100))

ROBOT_IMAGE = pygame.image.load(os.path.join("assets","robot.png"))
ROBOT = pygame.transform.rotate(pygame.transform.scale(ROBOT_IMAGE, (ROBOT_WIDTH, ROBOT_HEIGHT)), 90)

def robot_handle_movement(keys_pressed, robot):
  if keys_pressed[pygame.K_LEFT] and robot.x - VEL > 0:  # LEFT
    robot.x -= VEL
  if keys_pressed[pygame.K_RIGHT] and robot.x + VEL + robot.width + 40 < WIDTH:  # RIGHT
    robot.x += VEL
  if keys_pressed[pygame.K_UP] and robot.y - VEL > 0:  # UP
    robot.y -= VEL
  if keys_pressed[pygame.K_DOWN] and robot.y + VEL + robot.height - 40 < HEIGHT:  # DOWN
    robot.y += VEL

def draw_window(robot):
  WIN.fill(WHITE)
  WIN.blit(MARKER, (1000, HEIGHT/2 ))
  WIN.blit(ROBOT, (robot.x, robot.y))
  pygame.display.update()

def calculate_distance_and_vector(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    vector = (x2 - x1, y2 - y1)
    return distance, vector

def main():
  robot = pygame.Rect(100, 100, ROBOT_WIDTH, ROBOT_HEIGHT)
  marker = pygame.Rect(1000, HEIGHT/2, 100, 100)

  clock = pygame.time.Clock()
  run = True

  while run:
    clock.tick(FPS)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_ESCAPE]:
      run = False
    robot_handle_movement(keys_pressed, robot)
    draw_window(robot)
    pygame.display.update()

  pygame.quit()


if __name__ == "__main__":
  main()