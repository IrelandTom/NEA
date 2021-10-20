import pygame
import sys

from pygame import *

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


game_map = load_map()

tile_rects = []


class Screen:
    def __init__(self, width, height):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((width // 2, height // 2))
        self.cheese = "123"

    def scale(self):
        new_surface = pygame.transform.scale(self.display, self.window_size)
        self.screen.blit(new_surface, (0, 0))

    def draw_map(self):  # taken from: https://www.youtube.com/watch?v=5q7tmIlXROg
        tile_size = 16
        block_1 = pygame.image.load("assets/test_block1.png")
        block_2 = pygame.image.load("assets/test_block2.png")

        y = 0
        for layer in game_map:
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
        self.moving_up = False
        self.hit_list = []
        self.player_y_momentum = 0
        self.air_timer = 0
        self.player_movement = [0, 0]

    def collision_test(self, rect, tiles):
        for tile in tiles:
            if rect.colliderect(tile):
                self.hit_list.append(tile)
        return self.hit_list

    def move(self, rect, movement, tiles):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        rect.x += movement[0]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile.left
                collision_types["right"] = True
            elif movement[0] < 0:
                rect.left = tile.right
                collision_types["left"] = True
        rect.y += movement[1]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True
        return rect, collision_types

    def player_move(self):
#        velocity = 2
#        keys_pressed = pygame.key.get_pressed()
#        if keys_pressed[self.left]:  # LEFT
#            self.rect.x -= velocity
#            self.l = True
#        if keys_pressed[self.right]:  # RIGHT
#            self.rect.x += velocity
#            self.r = True
#        if keys_pressed[self.down]:  # DOWN
#            self.rect.y += velocity
#            self.d = True
#        if keys_pressed[self.up]:  # UP
#             self.rect.y -= velocity
#            self.u = True

        if self.moving_right:
            self.player_movement[0] += 2
        if self.moving_left:
            self.player_movement[0] -= 2
            self.player_movement[1] += self.player_y_momentum
        self.player_y_momentum += 0.2
        if self.player_y_momentum > 3:
            self.player_y_momentum = 3

    def key_events(self):

        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == self.right:
                    self.moving_right = True
                if event.key == self.left:
                    self.moving_left = True
                if event.key == self.down:
                    pass
                if event.key == self.up:
                    if self.air_timer < 6:
                        self.player_y_momentum = -5
            if event.type == KEYUP:
                if event.key == self.right:
                    self.moving_right = False
                if event.key == self.left:
                    self.moving_left = False
                if event.key == self.down:
                    pass


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    # players
    player_1 = Player(200, 200, "assets/player_1.png", pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w)
    player_2 = Player(250, 200, "assets/player_2.png", pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP)
    player_group = pygame.sprite.Group()
    player_group.add(player_1, player_2)
    player_rect1 = player_1.rect

    while True:

        clock.tick(60)

        screen.draw_map()

        player_group.draw(screen.display)

        player_1.player_move()
        player_2.player_move()

        player_rect1, collisions1 = player_1.move(player_rect1, player_1.player_movement, tile_rects)

        if collisions1["bottom"]:
            player_1.player_y_momentum = 0
            player_1.air_timer = 0
        else:
            player_1.air_timer += 1

        screen.display.blit(player_1.image, (player_1.rect.x, player_1.rect.y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys_pressed = pygame.key.get_pressed()
        player_1.key_events()
        player_2.key_events()
        screen.scale()
        screen.display.fill(steel_blue)

        pygame.display.update()

        print(tile_rects)


if __name__ == "__main__":
    main()
pygame.quit()
