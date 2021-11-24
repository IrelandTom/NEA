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



class Screen:
    def __init__(self, width, height):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((width // 2, height // 2))

    def scale(self):
        new_surface = pygame.transform.scale(self.display, self.window_size)
        self.screen.blit(new_surface, (0, 0))


class Map:
    def __init__(self, map_file):
        self.map_file = map_file
        self.tile_rects = []
        self.game_map = []

    def load_map(self):  # below function taken from: https://www.youtube.com/watch?v=5q7tmIlXROg
        file = open(self.map_file)
        data = file.read()
        file.close()
        data = data.split("\n")
        for row in data:
            self.game_map.append(list(row))
        return self.game_map

    def draw_map(self, screen):  # taken from: https://www.youtube.com/watch?v=5q7tmIlXROg
        tile_size = 16
        block_1 = pygame.image.load("assets/test_block1.png")
        block_2 = pygame.image.load("assets/test_block2.png")
        y = 0
        for layer in self.game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    screen.display.blit(block_1, (x * tile_size, y * tile_size))
                if tile == '2':
                    screen.display.blit(block_2, (x * tile_size, y * tile_size))
                if tile != '0':
                    self.tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))
                x += 1
            y += 1


class Player(pygame.sprite.Sprite):  # sprite class
    def __init__(self, pos_x, pos_y, player_images, walking_images_left, walking_images_right, attack_images, key_left, key_right, key_down,
                 key_up, key_attack):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_images[0]
        self.images_list = player_images
        self.walking_images_left = walking_images_left
        self.walking_images_right = walking_images_right
        self.images_attack = attack_images
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.left = key_left
        self.right = key_right
        self.down = key_down
        self.up = key_up
        self.attack_button = key_attack
        self.attacking = False
        self.moving_right = False
        self.moving_left = False
        self.moving_up = True
        self.hit_list = []
        self.player_y_velocity = 0
        self.air_timer = 0
        self.x_velocity = 0
        self.falling = False
        self.jumping = False
        self.animation_counter = 0
        self.frame_counter = 0
        self.player_orientation = {"left": False, "right": False, "up": False, "down": False, "default": True}
        self.collision_types = {"top": False, "bottom": False, "right": False, "left": False}

    def colour_key(self):
        for item in self.walking_images_left:
            self.images_list.append(item)
        for item in self.walking_images_right:
            self.images_list.append(item)
        for item in self.images_attack:
            self.images_list.append(item)
        for image in self.images_list:
            image.set_colorkey(white)

    def collision_test(self, tiles):
        # takes list of all tile rects then checks if they have collided with the players
        self.hit_list = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                self.hit_list.append(tile)
        return self.hit_list

    def move(self, tiles, screen_rect):
        # todo tidy this all up looks messy
        self.collision_types["top"] = False
        self.collision_types["bottom"] = False
        self.collision_types["left"] = False
        self.collision_types["right"] = False
        # __________________________________ #

        # making sure the player can't move off the screen
        self.rect.clamp_ip(screen_rect)

        self.player_y_velocity += 0.3
        if self.player_y_velocity > 4:
            self.player_y_velocity = 4
        if self.player_y_velocity >= 0:
            self.falling = True

        # update x position then check for collisions
        self.rect.x += self.x_velocity

        # update y pos then check for collisions
        self.rect.y += self.player_y_velocity

        # access collision test function to use colliderect
        self.collision_test(tiles)

        # looks through the tiles that are being collided with
        for tile in self.hit_list:

            # if you are moving right and the tile is to your right then you must have hit the tile on its left so
            # collision type is right
            if self.moving_right and tile.left >= self.rect.right:

                # x position of the right side of the rect is made same as the left of the tile x pos so collision
                self.rect.right = tile.left - 1
                self.collision_types["right"] = True

                # moving left so must have hit the tile on the right side of the rect so collision type is left
            if self.moving_left and tile.right <= self.rect.left:

                # x position of the left side of the rect is made same as the right side of the tile x pos so collision
                self.rect.left = tile.right + 1
                self.collision_types["left"] = True

            if self.player_y_velocity < 0:  # going up...
                if self.rect.top <= tile.bottom:  # ...and you've gone through tile

                    # same as before but for a top collision
                    self.rect.top = tile.bottom + 1
                    self.collision_types["top"] = True
                    self.player_y_velocity = 0

            # so if falling you must have hit the top of the tile so collision type bottom
            if self.player_y_velocity > 0:  # falling
                if self.rect.bottom > tile.top:  # fallen through tile

                    # same as before bottom rect is top tile
                    self.rect.bottom = tile.top
                    self.collision_types["bottom"] = True
                    self.player_y_velocity = 0
                    self.jumping = False

    def key_events(self, event):
        # key down section will allow for things to be toggled when key pressed down
        if event.type == KEYDOWN:
            if event.key == self.left:
                self.moving_left = True
                self.moving_right = False
                self.x_velocity = -2
                self.player_orientation["default"] = False
                self.player_orientation["right"] = False
                self.player_orientation["left"] = True
            if event.key == self.right:
                self.moving_right = True
                self.moving_left = False
                self.x_velocity = 2
                self.player_orientation["default"] = False
                self.player_orientation["left"] = False
                self.player_orientation["right"] = True
            if event.key == self.up:
                self.player_orientation["default"] = False
                self.player_orientation["up"] = True
                if not self.jumping:
                    if self.player_y_velocity > 0:
                        self.jumping = True
                        self.player_y_velocity = -5
            if event.key == self.down:
                self.player_orientation["default"] = False
                self.player_orientation["down"] = True
            if event.key == self.attack_button:
                self.attacking = True

        # can un-toggle the stuff from key downs or bind to new toggles
        if event.type == KEYUP:
            if event.key == self.left:
                self.x_velocity = 0
                self.moving_left = False
                self.player_orientation["default"] = True
            if event.key == self.right:
                self.x_velocity = 0
                self.moving_right = False
                self.player_orientation["default"] = True
            if event.key == self.up:
                self.player_orientation["up"] = False
                self.player_orientation["default"] = True
            if event.key == self.down:
                self.player_orientation["down"] = False
                self.player_orientation["default"] = True
            if event.key == self.attack_button:
                self.attacking = False
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def player_animations(self):
        if self.player_orientation["left"]:
            self.frame_counter += 1
            if self.moving_left:
                if self.frame_counter % 5 == 0:
                    self.animation_counter = (self.animation_counter + 1) % len(self.walking_images_left)
                    self.image = self.walking_images_left[self.animation_counter]
            if not self.moving_left:
                self.image = self.images_list[1]
            if self.attacking:
                self.image = self.images_attack[1]
            if not self.attacking:
                pass

        if self.player_orientation["right"]:
            self.frame_counter += 1
            if self.moving_right:
                if self.frame_counter % 5 == 0:
                    self.animation_counter = (self.animation_counter + 1) % len(self.walking_images_right)
                    self.image = self.walking_images_right[self.animation_counter]
            if not self.moving_right:
                self.image = self.images_list[0]
            if self.attacking:
                self.image = self.images_attack[0]

    def player_attack(self):
        pass


def main():

    # create objects
    fps = 60
    clock = pygame.time.Clock()
    screen = Screen(1377, 705)
    screen_rect = screen.display.get_rect()
    # Map loading
    map = Map("assets/map.txt")
    game_map = map.load_map()
    # players
    # player images lists
    player_1_images = [pygame.image.load("assets/frog_p1_right.png"), pygame.image.load("assets/frog_p1_left.png")]
    player_1_walking_sequence_left = [pygame.image.load("assets/frog_p1_left_walk1.0.png"),
                                      pygame.image.load("assets/frog_p1_left_walk1.25.png"),
                                      pygame.image.load("assets/frog_p1_left_walk1.50.png"),
                                      pygame.image.load("assets/frog_p1_left_walk1.75.png"),
                                      pygame.image.load("assets/frog_p1_left_walk2.0.png"),
                                      pygame.image.load("assets/frog_p1_left_walk2.25.png"),
                                      pygame.image.load("assets/frog_p1_left_walk2.50.png"),
                                      pygame.image.load("assets/frog_p1_left_walk2.75.png"),
                                      pygame.image.load("assets/frog_p1_left_walk2.76.png"),
                                      pygame.image.load("assets/frog_p1_left_walk2.78.png")]

    player_1_walking_sequence_right = [pygame.image.load("assets/frog_p1_right_walk1.0.png"),
                                       pygame.image.load("assets/frog_p1_right_walk1.25.png"),
                                       pygame.image.load("assets/frog_p1_right_walk1.50.png"),
                                       pygame.image.load("assets/frog_p1_right_walk1.75.png"),
                                       pygame.image.load("assets/frog_p1_right_walk2.0.png"),
                                       pygame.image.load("assets/frog_p1_right_walk2.25.png"),
                                       pygame.image.load("assets/frog_p1_right_walk2.50.png"),
                                       pygame.image.load("assets/frog_p1_right_walk2.75.png"),
                                       pygame.image.load("assets/frog_p1_right_walk2.76.png"),
                                       pygame.image.load("assets/frog_p1_right_walk2.78.png")]
    player_1_attack_sequence = [pygame.image.load("assets/frog_p1_attack_right.png"),
                                pygame.image.load("assets/frog_p1_attack_left.png")]

    player_2_images = [pygame.image.load("assets/frog_p2_right.png"), pygame.image.load("assets/frog_p2_left.png")]

    player_2_walking_sequence = [pygame.image.load("assets/frog_p2_left_walk1.png"),
                                 pygame.image.load("assets/frog_p2_left_walk2.png"),
                                 pygame.image.load("assets/frog_p2_right_walk1.png"),
                                 pygame.image.load("assets/frog_p2_right_walk2.png")]
    player_2_attack_sequence = [pygame.image.load("assets/frog_p2_attack_right.png"),
                                pygame.image.load("assets/frog_p2_attack_left.png") ]

    player_1 = Player(200, 100, player_1_images, player_1_walking_sequence_left, player_1_walking_sequence_right, player_1_attack_sequence, pygame.K_a,
                      pygame.K_d, pygame.K_s, pygame.K_w, pygame.K_LSHIFT)
    player_2 = Player(250, 100, player_2_images, player_2_walking_sequence, player_2_walking_sequence, player_2_attack_sequence, pygame.K_LEFT,
                      pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP, pygame.K_RSHIFT)
    player_1.colour_key()
    player_2.colour_key()
    player_group = pygame.sprite.Group()
    player_group.add(player_1, player_2)

    while True:


        clock.tick(fps)
        map.draw_map(screen)

        player_group.draw(screen.display)
        player_1.move(map.tile_rects, screen_rect)
        player_2.move(map.tile_rects, screen_rect)
        for event in pygame.event.get():
            player_1.key_events(event)
            player_2.key_events(event)
        player_1.player_animations()
        player_2.player_animations()
        screen.scale()
        map.tile_rects.clear()
        screen.display.fill(steel_blue)
        pygame.display.flip()


if __name__ == "__main__":
    main()
