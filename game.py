import pygame, sys, os, random
from time import time

#Pygame stuff
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

#Variables about the display
monitor = pygame.display.Info()
USER_RESOLUTION = [monitor.current_w, monitor.current_h]
RESOLUTION = [1920, 1080]
WINDOW = pygame.display.set_mode(USER_RESOLUTION)
SCREEN = pygame.Surface(RESOLUTION)
pygame.mouse.set_visible(False)

#GAME CONSTANTS
RADIUS = 20
PLAYER_SPEED = 500
PLAYER_SPAWN_LOCATION = [RESOLUTION[0] // 2, RESOLUTION[1] - 100]
BALL_SPEED = 300
BALL_SPAWN_LOCATION = [RESOLUTION[0] // 2, RESOLUTION[1] - 400]
RESPAWN_TIME = 2

#IMAGES
BOX_IMG = pygame.image.load("assets/images/box.png").convert_alpha()
GREY_FILTER_IMG = pygame.image.load("assets/images/grey_filter.png")
GREY_FILTER_IMG.set_alpha(128)

#SOUNDS
COLLISION_SOUND = pygame.mixer.Sound("assets/sounds/collision_sound.mp3")
DEATH_SOUND = pygame.mixer.Sound("assets/sounds/death_sound.mp3")
GAME_OVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over_sound.mp3")

def generate_bricks():
    bricks = []
    colours = ['pink', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'light blue']
    x = RESOLUTION[0] // 13
    for column in range(13):
        for row in range(8):
            brick = pygame.Rect((x * column) + 20, (60 * row) + 20, x - 40, 50)
            bricks.append([brick, colours[row]])
    return bricks

#Ball Class
class Ball:
    def __init__(self, pos, radius, speed_x, speed_y):
        self.rect = pygame.Rect(0, 0, radius, radius)
        self.rect.center = pos
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius

    def draw(self, surface, colour):
        pygame.draw.circle(surface, colour, self.rect.center, self.radius)

    def move(self, x, y, items):
        collision_list = [] #List of items that the ball has collided with
        collision_directions = [False, False] #[y direction, x direction] of whether the ball has collided in that direction

        #Moves the ball in the y direction and then checks for collisions
        self.rect.y += y
        for item in items:
            if self.rect.colliderect(item[0]):
                COLLISION_SOUND.play()
                collision_directions[0] = True
                collision_list.append(item)
                if y > 0: #This checks whether the ball is going up or going down
                    self.rect.bottom = item[0].top
                else:
                    self.rect.top = item[0].bottom

        #Moves the ball in the x direction and then checks for collisions
        self.rect.x += x
        for item in items:
            if self.rect.colliderect(item[0]):
                collision_directions[1] = True
                collision_list.append(item)
                if x > 0: #This checks whether the ball is going left or going right
                    self.rect.right = item[0].left
                else:
                    self.rect.left = item[0].right

        return collision_list, collision_directions
    

class Game:
    def __init__(self):
        self.last_time = time()
        self.fps = 60
        self.moving_left = self.moving_right = False
        self.ball = Ball(BALL_SPAWN_LOCATION, RADIUS, BALL_SPEED, BALL_SPEED)
        self.bricks = generate_bricks()
        self.paused = self.game_over = False
        self.respawn_timer = 0

        player_rect = pygame.Rect(0, 0, 200, 20)
        player_rect.center = PLAYER_SPAWN_LOCATION
        self.player = [player_rect, 0, 3] #player[rect, score, lives]


    def update_display(self):
        SCREEN.fill((0, 0, 0))

        for brick in self.bricks:
            pygame.draw.rect(SCREEN, pygame.Color(brick[1]), brick[0])

        colours = ["red", "red", "yellow" ,"green"]
        pygame.draw.rect(SCREEN, pygame.Color(colours[self.player[2]]), self.player[0])

        self.ball.draw(SCREEN, (255, 255, 255))

        #Shows the FPS
        font = pygame.font.SysFont("Impact", 25)
        fps_text = font.render(f"FPS: {round(self.fps)}", 1, pygame.Color("blue"))
        SCREEN.blit(fps_text, (10, 10))


        if self.paused:
            font = pygame.font.SysFont("Impact", 100)
            SCREEN.blit(pygame.transform.scale(GREY_FILTER_IMG, RESOLUTION), (0, 0))
            SCREEN.blit(BOX_IMG, ((RESOLUTION[0] // 2) - (BOX_IMG.get_width() // 2), (RESOLUTION[1] // 2) - (BOX_IMG.get_height() // 2)))

            font = pygame.font.SysFont("Impact", 50)
            y = (RESOLUTION[1] // 2) - 50
            for data in [["Score", self.player[1]], ["Lives", self.player[2]]]:
                text = font.render(f"{data[0]}:", 1, pygame.Color("white"))
                SCREEN.blit(text, ((RESOLUTION[0] // 2) - (BOX_IMG.get_width() // 2) + 50, y))
                text = font.render(f"{data[1]}", 1, pygame.Color("white"))
                SCREEN.blit(text, ((RESOLUTION[0] // 2) + (BOX_IMG.get_width() // 2) - 50 - text.get_width(), y))
                y += 75

            paused_text = font.render(f"Paused", 1, (255, 202, 24))
            SCREEN.blit(paused_text, ((RESOLUTION[0] // 2) - (paused_text.get_width() // 2), (RESOLUTION[1] // 2) - 150))


        if self.game_over:
            font = pygame.font.SysFont("Impact", 100)
            SCREEN.blit(pygame.transform.scale(GREY_FILTER_IMG, RESOLUTION), (0, 0))
            SCREEN.blit(BOX_IMG, ((RESOLUTION[0] // 2) - (BOX_IMG.get_width() // 2), (RESOLUTION[1] // 2) - (BOX_IMG.get_height() // 2)))

            font = pygame.font.SysFont("Impact", 50)
            y = (RESOLUTION[1] // 2) - 50
            for data in [["Final Score", self.player[1]], ["Lives", self.player[2]]]:
                text = font.render(f"{data[0]}:", 1, pygame.Color("white"))
                SCREEN.blit(text, ((RESOLUTION[0] // 2) - (BOX_IMG.get_width() // 2) + 50, y))
                text = font.render(f"{data[1]}", 1, pygame.Color("white"))
                SCREEN.blit(text, ((RESOLUTION[0] // 2) + (BOX_IMG.get_width() // 2) - 50 - text.get_width(), y))
                y += 75

            game_over_text = font.render(f"Game Over", 1, (255, 202, 24))
            SCREEN.blit(game_over_text, ((RESOLUTION[0] // 2) - (game_over_text.get_width() // 2), (RESOLUTION[1] // 2) - 150))

        #Ouputs the display in the user resolution
        WINDOW.blit(pygame.transform.scale(SCREEN, USER_RESOLUTION), (0, 0))
        pygame.display.update()



    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LEFT:
                    self.moving_left = True
                if event.key == pygame.K_RIGHT:
                    self.moving_right = True
                if event.key == pygame.K_TAB: #Checks to see if the key being pressed is escape
                    self.paused = not self.paused

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.moving_left = False
                if event.key == pygame.K_RIGHT:
                    self.moving_right = False

    def move_player(self, dt):
        if self.moving_left:
            self.player[0].x -= PLAYER_SPEED * dt
        if self.moving_right:
            self.player[0].x += PLAYER_SPEED * dt

        if self.player[0].left <= 0:
            self.player[0].left = 0
        elif self.player[0].right >= RESOLUTION[0]:
            self.player[0].right = RESOLUTION[0]

    def change_ball_direction(self, collision_directions):
        #Changes direction if hitting a brick or player
        if collision_directions[0]:
            self.ball.speed_y *= -1
        if collision_directions[1]:
            self.ball.speed_x *= -1
        #Checks if ball is hitting the borders and changes direction
        if self.ball.rect.left <= 0:
            self.ball.speed_x *= -1
            self.ball.rect.left = 0
        if self.ball.rect.right >= RESOLUTION[0]:
            self.ball.speed_x *= -1
            self.ball.rect.right = RESOLUTION[0]
        if self.ball.rect.top <= 0:
            self.ball.speed_y *= -1
            self.ball.rect.top = 0
        if self.ball.rect.bottom >= RESOLUTION[1]:
            self.player[2] -= 1
            self.ball.rect.center = BALL_SPAWN_LOCATION
            DEATH_SOUND.play()
            self.respawn_timer = RESPAWN_TIME

    def delete_bricks(self, collision_list):
        for item in collision_list:
            if item in self.bricks:
                self.bricks.remove(item)
                self.player[1] += 1 #Adds 1 to the score

    def game_loop(self):
        dt = (time() - self.last_time)
        self.last_time = time()

        if not self.paused and not self.game_over:
            self.move_player(dt)
            if self.respawn_timer > 0:
                self.respawn_timer -= dt
            else:
                collidables = self.bricks.copy()
                collidables.append(self.player)
                collision_list, collision_directions = self.ball.move(self.ball.speed_x * dt, self.ball.speed_y * dt, collidables)

                self.change_ball_direction(collision_directions)
                self.delete_bricks(collision_list)

                if self.player[2] == 0:
                    self.game_over = True
                    GAME_OVER_SOUND.play()

        self.handle_events()
        self.update_display()
        clock.tick()
        self.fps = clock.get_fps()


game = Game()

while True:
    game.game_loop()