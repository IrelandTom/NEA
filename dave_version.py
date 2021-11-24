import pygame
import sys
import random

from pygame.locals import *

pygame.init()

# colours easy access

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
steel_blue = (27, 51, 71)

#  below function taken from: https://www.youtube.com/watch?v=5q7tmIlXROg


def load_map():
    file = open("assets/map.txt")
    data = file.read()
    file.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


game_mapy = load_map()

tile_rects = []


class Screen:
    def __init__(self, width, height):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((width // 2, height // 2))
        self.cheese = "123"

    def scale(self):
        # changing the screen to allow for better pixel art rendering
        new_surface = pygame.transform.scale(self.display, self.window_size)
        self.screen.blit(new_surface, (0, 0))

    def draw_map(self):  # taken from: https://www.youtube.com/watch?v=5q7tmIlXROg
        tile_size = 16
        block_1 = pygame.image.load("assets/test_block1.png")
        block_2 = pygame.image.load("assets/test_block2.png")

        y = 0
        for layer in game_mapy:
            x = 0
            for tile in layer:
                if tile == '1':
                    self.display.blit(block_1, (x * tile_size, y * tile_size))
                if tile == '2':
                    self.display.blit(block_2, (x * tile_size, y * tile_size))
                if tile != '0':
                    tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))
                x += 1
            y += 1


class Player(pygame.sprite.Sprite):  # sprite class
    def __init__(self, pos_x, pos_y, image, key_left, key_right, key_down, key_up):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.left = key_left
        self.right = key_right
        self.down = key_down
        self.up = key_up
        self.moving_right = False
        self.moving_left = False
        self.moving_up = True
        self.hit_list = []
        self.y_velocity = 0
        self.air_timer = 0
        self.player_movement = [0, 0]
        self.x_velocity = 0
        self.falling = False
        self.collision_types = {"top": False, "bottom": False, "right": False, "left": False}

    def collision_test(self, rect, tiles):
        # takes list of all tile rects then checks if they have collided with the players
        for tile in tiles:
            if rect.colliderect(tile):
                self.hit_list.append(tile)

        return self.hit_list

    def move(self, tiles):
        # todo tidy this all up looks messy
        self.collision_types["top"] = False
        self.collision_types["bottom"] = False
        self.collision_types["left"] = False
        self.collision_types["right"] = False
        # __________________________________ #

        if self.moving_up:
            # gravity
            self.y_velocity += 0.3
            if self.y_velocity > 4:
                self.y_velocity = 4
            if self.y_velocity >= 0:
                self.falling = True

        # update x position then check for collisions
        self.rect.x += self.x_velocity
        # access collision test function to use colliderect
        hit_list = self.collision_test(self.rect, tiles)
        # looks through the tiles that are being collided with
        for tile in hit_list:
            # if you are moving right you must have hit the tile on the left so collision type is right
            if self.moving_right:
                # x position of the right side of the rect is made same as the left of the tile x pos so collision
                self.rect.right = tile.left
                self.collision_types["right"] = True
                # moving left so must have hit the tile on the right side of the rect so collision type is left
            elif self.moving_left:
                # x position of the left side of the rect is made same as the right side of the tile x pos so collision
                self.rect.left = tile.right
                self.collision_types["left"] = True
        # update y pos then check for collisions again
        self.rect.y += self.y_velocity
        for tile in hit_list:
            # if the y velocity less than 0 then going up so collision type must be top
            if self.y_velocity < 0:
                if self.rect.top <= tile.bottom:
                    # same as before but for a top collision
                    self.rect.top = tile.bottom + 1
                    self.collision_types["top"] = True
            # so if falling you must have hit the top of the tile so collision type bottom
            if self.falling:
                if self.rect.bottom > tile.top:
                    # same as before bottom rect is top tile
                    self.rect.bottom = tile.top
                    self.y_velocity = 0
                    self.collision_types["bottom"] = True

    def key_events(self, event):
        # key down section will allow for things to be toggled when key pressed down
        if event.type == KEYDOWN:
            if event.key == self.right:
                self.moving_right = True
                self.x_velocity = 2
                print(self.x_velocity)
            if event.key == self.left:
                self.moving_left = True
                self.x_velocity = -2
                print(self.x_velocity)
            if event.key == self.down:
                pass
            if event.key == self.up:
                print(self.y_velocity)
                self.moving_up = True
                self.falling = False
                if self.air_timer < 6:
                    self.y_velocity = -5
        # can un-toggle the stuff from key downs or bind to new toggles
        if event.type == KEYUP:
            if event.key == self.right:
                self.x_velocity = 0
                self.moving_right = False
            if event.key == self.left:
                self.x_velocity = 0
                self.moving_left = False
            if event.key == self.down:
                pass
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


# rect_y = pygame.Rect(200, 107, 16, 16)


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    # players
    player_1 = Player(200, 100, "assets/player_1.png", pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w)
    player_2 = Player(250, 100, "assets/player_2.png", pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP)
    player_group = pygame.sprite.Group()
    player_group.add(player_1, player_2)

    while True:

        clock.tick(60)

        screen.draw_map()

        # pygame.draw.rect(screen.display, (255, 0, 0), rect_y)

        player_group.draw(screen.display)

        player_1.move(tile_rects)
        player_2.move(tile_rects)

        for event in pygame.event.get():
            player_1.key_events(event)
            player_2.key_events(event)
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_y]:
                bg = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                screen.display.fill(bg)

        screen.scale()
        screen.display.fill(steel_blue)
        tile_rects.clear()
        pygame.display.update()


if __name__ == "__main__":
    main()