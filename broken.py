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


game_map = load_map()

tile_rects = []


class Screen:
    def __init__(self, width, height):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((width // 2, height // 2))

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
        self.player_y_velocity = 0
        self.air_timer = 0
        self.player_movement = [0, 0]
        self.x_velocity = 0
        self.falling = False
        self.collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}

    def handle_player_movement(self):
        # if we are holding down the key to move right we move right
        if self.moving_right:
            self.player_movement[0] += 2
        # if we are holding down the key to move left we move left
        if self.moving_left:
            self.player_movement[0] += -2
        # if we are holding down the key to move up we move up
        self.player_movement[1] += self.player_y_velocity
        # self.player_y_velocity += 0.2
        # if self.player_y_velocity >= 4:
        #     self.player_y_velocity = 4

    def collision_test(self, rect, tiles):
        for tile in tiles:
            # pygame.Rect(tile)
            if rect.colliderect(tile):
                self.hit_list.append(tile)

        return self.hit_list

    def collision_physics(self, rect, tiles):
        rect.x += self.player_movement[0]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if self.player_movement[0] > 0:
                rect.right = tile.left
                self.collision_types['right'] = True
            elif self.player_movement[0] < 0:
                rect.left = tile.right
                self.collision_types['left'] = True
        rect.y += self.player_movement[1]
        hit_list = self.collision_test(rect, tiles)
        for tile in hit_list:
            if self.player_movement[1] > 0:
                rect.bottom = tile.top
                self.collision_types['bottom'] = True
            elif self.player_movement[1] < 0:
                rect.top = tile.bottom
                self.collision_types['top'] = True
        return tiles, self.collision_types
    # def move(self, movement, tiles):
    #     collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    #     # self.rect.x += movement[0]
    #     # hit_list = self.collision_test(self.rect, tiles)
    #     # for tile in hit_list:
    #     #     if movement[0] > 0:
    #     #         self.rect.right = tile.left
    #     #         collision_types["right"] = True
    #     #     elif movement[0] < 0:
    #     #         self.rect.left = tile.right
    #     #         collision_types["left"] = True
    #     # self.rect.y += movement[1]
    #     # hit_list = self.collision_test(self.rect, tiles)
    #     # for tile in hit_list:
    #     #     if movement[1] > 0:
    #     #         self.rect.bottom = tile.top
    #     #         collision_types['bottom'] = True
    #     #     elif movement[1] < 0:
    #     #         self.rect.top = tile.bottom
    #     #         collision_types['top'] = True
    #     # return self.rect, collision_types
    #
    #     hit_list = self.collision_test(self.rect, tiles)
    #     for tile in hit_list:
    #         if self.moving_right:
    #             self.x_velocity = 0
    #             self.rect.right = tile.left
    #             collision_types['right'] = True
    #         elif self.moving_left:
    #             self.x_velocity = 0
    #             self.rect.left = tile.right
    #             collision_types['left'] = True
    #     for tile in hit_list:
    #         if self.player_y_velocity < 0:
    #             if self.rect.top <= tile.bottom:
    #                 self.rect.top = tile.bottom + 1
    #                 collision_types['bottom'] = True
    #         if self.falling:
    #             if self.rect.bottom > tile.top:
    #                 self.rect.bottom = tile.top
    #                 collision_types['bottom'] = True
    #
    # def player_move(self):
    #     if self.moving_right:
    #         self.rect.x += self.x_velocity
    #         # self.player_movement[0] += 2
    #     if self.moving_left:
    #         # self.player_movement[0] -= 2
    #         self.rect.x += self.x_velocity
    #     self.rect.y += self.player_y_velocity
    #     self.player_y_velocity += 0.3
    #     if self.player_y_velocity > 4:
    #         self.player_y_velocity = 4
    #     if self.player_y_velocity >= 0:
    #         self.falling = True

    def key_events(self, event):

        if event.type == KEYDOWN:
            if event.key == self.right:
                self.x_velocity = 1
                self.moving_right = True
            if event.key == self.left:
                self.x_velocity = -1
                self.moving_left = True
            if event.key == self.down:
                pass
            if event.key == self.up:
                self.moving_up = True
                # if self.air_timer < 6:
                self.player_y_velocity = - 5
        if event.type == KEYUP:
            if event.key == self.right:
                # self.x_velocity = 0
                self.moving_right = False
            if event.key == self.left:
                # self.x_velocity = 0
                self.moving_left = False
            if event.key == self.down:
                pass
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


recty = pygame.Rect(200, 107, 16, 16)


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    # players
    player_1 = Player(230, 100, "assets/player_1.png", pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w)
    player_2 = Player(250, 100, "assets/player_2.png", pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP)
    player_group = pygame.sprite.Group()
    player_group.add(player_1, player_2)

    while True:

        clock.tick(60)

        screen.draw_map()

        pygame.draw.rect(screen.display, (255, 0, 0), recty)

        player_group.draw(screen.display)

        # player_1.move(player_1.player_movement, tile_rects)
        # player_2.move(player_2.player_movement, tile_rects)
        player_1.handle_player_movement()
        player_2.handle_player_movement()
        player_1.collision_physics(player_1.rect, tile_rects)
        player_2.collision_physics(player_2.rect, tile_rects)

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
