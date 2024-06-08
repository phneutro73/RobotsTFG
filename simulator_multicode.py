import pygame
import os
import math

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1540, 800
ROOF_WIDTH, ROOF_HEIGHT = 1280, 720
ROBOT_WIDTH, ROBOT_HEIGHT = 120, 165
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED) #| pygame.FULLSCREEN)
pygame.display.set_caption("Simulator")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

FPS = 60
VEL = 5

MARKER_IMAGE_0 = pygame.image.load(os.path.join("assets", "aruco_10.png"))
MARKER_0 = pygame.transform.scale(MARKER_IMAGE_0, (55, 55))
MARKER_IMAGE_1 = pygame.image.load(os.path.join("assets", "aruco_11.png"))
MARKER_1 = pygame.transform.scale(MARKER_IMAGE_1, (55, 55))
MARKER_IMAGE_2 = pygame.image.load(os.path.join("assets", "aruco_12.png"))
MARKER_2 = pygame.transform.scale(MARKER_IMAGE_2, (55, 55))
MARKER_IMAGE_3 = pygame.image.load(os.path.join("assets", "aruco_13.png"))
MARKER_3 = pygame.transform.scale(MARKER_IMAGE_3, (55, 55))
MARKER_IMAGE_4 = pygame.image.load(os.path.join("assets", "aruco_14.png"))
MARKER_4 = pygame.transform.scale(MARKER_IMAGE_4, (55, 55))

ROBOT_IMAGE_1 = pygame.image.load(os.path.join("assets","robot_0.png"))
ROBOT_1 = pygame.transform.rotate(pygame.transform.scale(ROBOT_IMAGE_1, (ROBOT_WIDTH, ROBOT_HEIGHT)), 90)

def robot_handle_movement(keys_pressed, robot):
  if keys_pressed[pygame.K_LEFT] and robot.x - VEL > 0:  # LEFT
    robot.x -= VEL
  if keys_pressed[pygame.K_RIGHT] and robot.x + VEL + robot.width < WIDTH-ROBOT_WIDTH +50:  # RIGHT
    robot.x += VEL
  if keys_pressed[pygame.K_UP] and robot.y - VEL > 0:  # UP
    robot.y -= VEL
  if keys_pressed[pygame.K_DOWN] and robot.y + VEL + robot.height - 40 < HEIGHT - ROBOT_HEIGHT + 150:  # DOWN
    robot.y += VEL

def draw_window(robot):
  WIN.fill(WHITE)
  WIN.blit(MARKER_0, (WIDTH/2, HEIGHT/2))
  WIN.blit(MARKER_1, (10, 10))
  WIN.blit(MARKER_2, (WIDTH-ROBOT_WIDTH+50, 10))
  WIN.blit(MARKER_3, (WIDTH-ROBOT_WIDTH+50, HEIGHT-ROBOT_HEIGHT+90))
  WIN.blit(MARKER_4, (10, HEIGHT-ROBOT_HEIGHT+90))
  WIN.blit(ROBOT_1, (robot.x, robot.y))
  pygame.display.update()

def main():
  robot = pygame.Rect(WIDTH/2-100, HEIGHT/2-50, ROBOT_WIDTH, ROBOT_HEIGHT)
  
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