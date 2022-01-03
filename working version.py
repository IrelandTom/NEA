import pygame
import sys
import random
from pygame.locals import *

pygame.init()

FPS = 60
# colours easy access
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
steel_blue = (27, 51, 71)
tongue_purple = (172, 61, 177)
tongue_blue = (11, 205, 221)
green = (10, 161, 126)
pink = (245, 94, 129)
# TODO, dodge mechanic
# TODO, add some sound effects
# TODO, add different attacks
# TODO, sort out animations for when walking and attacking at the same time
# TODO, make it so that when a player looses their health they die
# TODO, title screen


class Screen:
    def __init__(self, width, height, caption):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.caption = pygame.display.set_caption(caption)
        self.display = pygame.Surface((width // 2, height // 2))

    def scale(self):  # scales the screen to a more suitable size to allow for better representation of pixel art
        new_surface = pygame.transform.scale(self.display, self.window_size)
        self.screen.blit(new_surface, (0, 0))


class Map:  # separate map class allows for future map development. this makes it easy for developers to add new maps
    def __init__(self, map_file):
        self.map_file = map_file
        self.tile_rects = []
        self.game_map = []

    def load_map(self):  # below function adapted from: https://www.youtube.com/watch?v=5q7tmIlXROg
        file = open(self.map_file)
        data = file.read()
        file.close()
        data = data.split("\n")
        for row in data:
            self.game_map.append(list(row))
        return self.game_map

    def draw_map(self, screen):  # adapted from: https://www.youtube.com/watch?v=5q7tmIlXROg
        tile_size = 16
        block_1 = pygame.image.load("assets/test_block1.png")
        block_2 = pygame.image.load("assets/test_block2.png")
        y = 0
        for layer in self.game_map:
            x = 0
            for tile in layer:
                if tile == "1":
                    screen.display.blit(block_1, (x * tile_size, y * tile_size))
                if tile == "2":
                    screen.display.blit(block_2, (x * tile_size, y * tile_size))
                if tile != "0":
                    self.tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))
                x += 1
            y += 1


class Player(pygame.sprite.Sprite):  # sprite class
    def __init__(self, pos_x, pos_y, player_images, walking_images_left, walking_images_right, attack_images, key_left,
                 key_right, key_down, key_up, key_attack, tongue_colour, ducking_images, name):
        pygame.sprite.Sprite.__init__(self)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # images section
        self.image = player_images[2]
        self.images_list = player_images
        self.walking_images_left = walking_images_left
        self.walking_images_right = walking_images_right
        self.ducking_images = ducking_images
        self.attacking_images = attack_images
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # rect and position of player
        self.rect = self.image.get_rect()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect.center = [self.pos_x, self.pos_y]
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # defining the keys
        self.left = key_left
        self.right = key_right
        self.down = key_down
        self.up = key_up
        self.attack_button = key_attack
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # movement Bools
        self.attacking = False
        self.moving_right = False
        self.moving_left = False
        self.moving_up = True
        self.jumping = False
        self.ducking = False
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        self.hit_list = []
        self.player_y_velocity = 0
        self.air_timer = 0
        self.x_velocity = 0
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # animation
        self.animation_counter = 0
        self.frame_counter = 0
        self.player_orientation = {"left": False, "right": True, "up": False, "down": False, "default": True}
        self.collision_types = {"top": False, "bottom": False, "right": False, "left": False}
        self.attack_rect = pygame.Rect(0, 0, 0, 0)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # attacking
        self.tongue_colour = tongue_colour
        self.length = 0
        self.mini_hit_list = []
        self.max_tongue_length = 50
        self.tongue_height = 3
        self.attack_timer = 0
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
        # health and other stats
        self.health = 100
        self.hit_bool = False
        self.invincibility_timer = 0
        self.healthbar_decreaser = False
        self.dodging = False
        self.lives = 2
        self.loser = False
        self.winner = False
        self.name = name
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def colour_key(self):  # creates a greenscreen effect that removes all the white colour on images
        # loops through all lists of images given then appends them to a larger list
        for item in self.ducking_images:
            self.images_list.append(item)
        for item in self.walking_images_left:
            self.images_list.append(item)
        for item in self.walking_images_right:
            self.images_list.append(item)
        for item in self.attacking_images:
            self.images_list.append(item)
        # after all the images are accounted for, the white screen can be used on all of them
        for image in self.images_list:
            image.set_colorkey(white)

    def collision_test(self, tiles):
        # takes list of all tile rects then checks if they have collided with the players
        self.hit_list = []
        self.mini_hit_list = []
        for tile in tiles:  # each tile in the list tile is a rect, this gives python the data to use colliderect()
            if self.rect.colliderect(tile):  # inbuilt function that tests for rect collisions
                self.hit_list.append(tile)
            if self.attack_rect.colliderect(tile):
                self.mini_hit_list.append(tile)
        return self.hit_list, self.mini_hit_list  # return the lists of collisions for later use

    def move(self, tiles, screen_rect):

        # making sure the player can't move off the screen
        self.rect.clamp_ip(screen_rect)

        # gravity. After the player has jumped they experience a constant acceleration towards the ground resulting
        # in a simple simulation of gravity
        self.player_y_velocity += 0.3
        if self.player_y_velocity > 4:
            self.player_y_velocity = 4

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
                self.rect.right = tile.left
                self.collision_types["right"] = True

                # moving left so must have hit the tile on the right side of the rect so collision type is left
            elif self.moving_left and tile.right <= self.rect.left:

                # x position of the left side of the rect is made same as the right side of the tile x pos so collision
                self.rect.left = tile.right
                self.collision_types["left"] = True

            elif self.player_y_velocity < 0:  # going up...
                if self.rect.top <= tile.bottom:  # ...and you've gone through tile

                    # same as before but for a top collision
                    self.rect.top = tile.bottom
                    self.collision_types["top"] = True
                    self.player_y_velocity = 0

            # so if falling you must have hit the top of the tile so collision type bottom
            elif self.player_y_velocity > 0:  # falling
                if self.rect.bottom > tile.top:  # fallen through tile

                    # same as before bottom rect is top tile
                    self.rect.bottom = tile.top
                    self.collision_types["bottom"] = True
                    self.player_y_velocity = 0
                    self.jumping = False

        for tile in self.mini_hit_list:  # an attempt at having collisions work for the tongues

            if self.attack_rect.right == tile.left:
                self.attack_rect.right = tile.left

    def events(self, event, user_event, opponent):
        # key down section will allow for things to be toggled when key pressed down
        if event.type == KEYDOWN:
            if event.key == self.left:  # pressed left
                self.moving_left = True
                self.moving_right = False
                self.x_velocity = -2
                self.player_orientation["default"] = False
                self.player_orientation["right"] = False
                self.player_orientation["left"] = True

            if event.key == self.right:  # pressed right
                self.moving_right = True
                self.moving_left = False
                self.x_velocity = 2
                self.player_orientation["default"] = False
                self.player_orientation["left"] = False
                self.player_orientation["right"] = True

            if event.key == self.up:  # pressed up key
                self.player_orientation["default"] = False
                self.player_orientation["up"] = True
                self.player_orientation["down"] = False
                self.ducking = False
                if not self.jumping:
                    if self.player_y_velocity > 0:
                        self.jumping = True
                        self.player_y_velocity = -5

            if event.key == self.down and not self.jumping:  # pressed down key. (can't duck when jumping)
                self.x_velocity = 0
                self.moving_left = False
                self.moving_right = False
                self.ducking = True
                self.player_orientation["left"] = False
                self.player_orientation["right"] = False
                self.player_orientation["default"] = False
                self.player_orientation["down"] = True
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
            # can't attack if you walk first
            if event.key == self.right and self.attacking:
                self.attacking = False

            if event.key == self.left and self.attacking:
                self.attacking = False

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

            if event.key == self.attack_button:  # released attack key
                self.attacking = True

            if event.key == pygame.K_RETURN and self.winner or self.loser:  # end screen, detects if the player has
                # pressed enter
                self.lives = 3
                opponent.lives = 3
                self.health = 100
                opponent.health = 100
                self.loser = False
                opponent.loser = False
                self.winner = False
                opponent.winner = False
                self.rect.center = [self.pos_x, self.pos_y]

        # can un-toggle the Bools from key downs or bind to new toggles
        if event.type == KEYUP:
            if event.key == self.left:  # released left key
                self.x_velocity = 0
                self.moving_left = False
                self.player_orientation["default"] = True

            if event.key == self.right:  # released right key
                self.x_velocity = 0
                self.moving_right = False
                self.player_orientation["default"] = True

            if event.key == self.up:  # released up key
                self.player_orientation["up"] = False
                self.player_orientation["default"] = True

            if event.key == self.down:  # released down key
                self.rect = self.rect
                self.ducking = False
                self.player_orientation["default"] = True

            if event.key == self.attack_button:  # released attack key
                self.attacking = False
                self.length = 0

        if event.type == user_event:  # user event is when the opponent player has been hit
            self.health -= 25
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit("goodbye hope you enjoyed this game!")

    def player_animations(self):

        if self.player_orientation["left"]:  # section for the player animations for moving left
            self.frame_counter += 1  # used to slow down animation sequence
            if self.moving_left:
                if self.frame_counter % 4 == 0:  # every 4th frame change the image
                    self.animation_counter = (self.animation_counter + 1) % len(self.walking_images_left)
                    # count up to the length of the list of images, then divide the subsequent numbers by the
                    # length of the length of the list. this allows for a constant loop that always returns to 0
                    self.image = self.walking_images_left[self.animation_counter]
            if not self.moving_left:
                self.image = self.images_list[1]
            if self.attacking:
                self.image = self.attacking_images[1]
            if not self.attacking:
                pass

        if self.player_orientation["right"]:  # same as the above but for a different orientation
            self.frame_counter += 1
            if self.moving_right:
                if self.frame_counter % 4 == 0:
                    self.animation_counter = (self.animation_counter + 1) % len(self.walking_images_right)
                    self.image = self.walking_images_right[self.animation_counter]
            if not self.moving_right:
                self.image = self.images_list[0]
            if self.attacking:
                self.image = self.attacking_images[0]

        if self.player_orientation["down"]:  # ducking sequence with plans for a full duck animation
            self.frame_counter += 1
            if self.ducking:
                if self.frame_counter % 5 == 0:  # same as previous
                    self.animation_counter = (self.animation_counter + 1) % len(self.ducking_images)
                    self.image = self.ducking_images[self.animation_counter]
            if not self.ducking:
                self.image = self.images_list[0]
                self.player_orientation["down"] = False

    def attack(self, surface):

        if self.player_orientation["left"]:  # attacking while facing left
            if self.attacking:
                self.length += 3  # increment the length of the tongue by a small fraction every frame
                self.attack_rect = pygame.Rect(self.rect.centerx - self.length, self.rect.centery - 1,
                                               self.length, self.tongue_height)  # set up the size of the tongue
                pygame.draw.rect(surface.display, self.tongue_colour, self.attack_rect)  # draw the tongue
                if self.length >= self.max_tongue_length:  # set a maximum length for the tongue
                    self.length = self.max_tongue_length
            if not self.attacking:
                self.attack_rect = pygame.Rect(0, 0, 0, 0)  # when the player is not attacking make the rect disappear

        if self.player_orientation["right"]:  # same but for a different player orientation
            if self.attacking:
                self.length += 3
                self.attack_rect = pygame.Rect(self.rect.centerx - 1, self.rect.centery - 1, self.length,
                                               self.tongue_height)
                pygame.draw.rect(surface.display, self.tongue_colour, self.attack_rect)
                if self.length >= self.max_tongue_length:
                    self.length = self.max_tongue_length
            if not self.attacking:
                self.attack_rect = pygame.Rect(0, 0, 0, 0)

    def hit_detector(self, opponent, user_event):
        # if the rect of the tongue hits the player rect
        opp_hitbox_rect = pygame.Rect(opponent.rect.x, opponent.rect.y, opponent.rect.width, opponent.rect.height)
        if self.attack_rect.colliderect(opp_hitbox_rect) and self.invincibility_timer == 0 and not opponent.ducking:
            self.hit_bool = True
            # make the player invincible after they have been hit
            self.invincibility_timer = FPS
        if self.hit_bool:
            # post the event that the player has been hit (event will make player lose health)
            pygame.event.post(pygame.event.Event(user_event))
            self.hit_bool = False
            self.healthbar_decreaser = True
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

    def death(self, opponent):
        # sets the criteria for how a player is to die
        if opponent.health <= 0:
            opponent.lives -= 1
            opponent.health = 100
            self.rect.center = [self.pos_x, self.pos_y]
        if opponent.lives <= 0:
            opponent.lives = 0
            opponent.health = 0
            opponent.loser = True
        if opponent.loser:
            opponent.winner = True


class HandleWinning:
    def __init__(self, player):
        self.font = pygame.font.Font("freesansbold.ttf", 15)
        self.player = player

    def winner_screen(self, screen, colour):
        # displays the text that says who won in the middle of the screen. the colour of the screen also changes to
        # the colour of whichever player won
        if self.player.winner:
            screen.display.fill(colour)
            winner_text = self.font.render(self.player.name + " Won!", 1, red)
            screen.display.blit(winner_text, (screen.display.get_width() // 2 - 60, screen.display.get_height() // 2))
            resume_text = self.font.render("press enter to play again", 1, red)
            screen.display.blit(resume_text,
                                (screen.display.get_width() // 2 - 60, screen.display.get_height() // 2 + 30))


class PlayerStats:
    def __init__(self, images, healthbar_posx, healthbar_posy, health_rect_posx, health_rect_posy):
        self.stats_img_list = images
        self.health_rect = pygame.Rect(0, 0, 0, 0)
        self.healthbar_height = 14
        self.healthbar_width = 52
        self.healthbar_width_div_4 = 13  # amount taken off the health bar each time the player is hit.
        self.healthbar_posx = healthbar_posx
        self.healthbar_posy = healthbar_posy
        self.health_rect_posx = health_rect_posx
        self.health_rect_posy = health_rect_posy
        self.font = pygame.font.Font("freesansbold.ttf", 10)
        for image in self.stats_img_list:  # uses a sort of green screen effect to remove any white from the image
            image.set_colorkey(white)

    def health_stats(self, screen, player):
        # will display the healthbar graphic and the animated red rectangle which displays the player's health
        screen.display.blit(self.stats_img_list[0], (self.healthbar_posx, self.healthbar_posy))
        self.health_rect = pygame.Rect(self.health_rect_posx, self.health_rect_posy, self.healthbar_width,
                                       self.healthbar_height)
        if player.healthbar_decreaser:
            self.healthbar_width -= self.healthbar_width_div_4
            player.healthbar_decreaser = False
        if player.health == 0 and player.lives > 0:
            self.healthbar_width = 52
        pygame.draw.rect(screen.display, red, self.health_rect)

    def other_stats(self, screen, player):
        # displays how long the player is invincible for
        invincibility_stats = self.font.render("invincible " + str(player.invincibility_timer), 1, red)
        screen.blit(invincibility_stats, (self.healthbar_posx, self.healthbar_posy + 30))
        # displays how many lives the player has left
        lives_stats = self.font.render("lives " + str(player.lives), 1, red)
        screen.blit(lives_stats, (self.healthbar_posx, self.healthbar_posy + 60))


def main():

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # create objects

    clock = pygame.time.Clock()
    screen = Screen(1377, 705, "Froggy Fighters")
    screen_rect = screen.display.get_rect()

    # Map loading
    map = Map("assets/map.txt")
    map.load_map()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # players section

    # player1 images lists
    player_1_images = [pygame.image.load("assets/frog_p1_right.png"), pygame.image.load("assets/frog_p1_left.png"),
                       pygame.image.load("assets/dead_img.png")]
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
    player_1_ducking_sequence = [pygame.image.load("assets/frog_p1_duck.png")]
    player_1_attack_sequence = [pygame.image.load("assets/frog_p1_attack_right.png"),
                                pygame.image.load("assets/frog_p1_attack_left.png")]

    # player2 images lists
    player_2_images = [pygame.image.load("assets/frog_p2_right.png"), pygame.image.load("assets/frog_p2_left.png"),
                       pygame.image.load("assets/dead_img.png")]

    player_2_walking_sequence = [pygame.image.load("assets/frog_p2_left_walk1.png"),
                                 pygame.image.load("assets/frog_p2_left_walk2.png"),
                                 pygame.image.load("assets/frog_p2_right_walk1.png"),
                                 pygame.image.load("assets/frog_p2_right_walk2.png")]
    player_2_ducking_sequence = [pygame.image.load("assets/frog_p2_duck.png")]
    player_2_attack_sequence = [pygame.image.load("assets/frog_p2_attack_right.png"),
                                pygame.image.load("assets/frog_p2_attack_left.png")]

    # def the player objects
    player_1 = Player(200, 100, player_1_images, player_1_walking_sequence_left, player_1_walking_sequence_right,
                      player_1_attack_sequence, pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w, pygame.K_LSHIFT,
                      tongue_purple, player_1_ducking_sequence, "Green Froggy")
    player_2 = Player(500, 100, player_2_images, player_2_walking_sequence, player_2_walking_sequence,
                      player_2_attack_sequence, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP,
                      pygame.K_RSHIFT, tongue_blue, player_2_ducking_sequence, "Pink Froggy")
    player_1.colour_key()
    player_2.colour_key()
    player_group = pygame.sprite.Group()
    player_group.add(player_1, player_2)

    # user events
    player_1_hit = pygame.USEREVENT + 1
    player_2_hit = pygame.USEREVENT + 2

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # stats section
    # stats images
    stats_images = [pygame.image.load("assets/healthbar.png")]

    # def the stats class
    screen_width = screen.display.get_width()
    screen_height = screen.display.get_height()
    stats_p1 = PlayerStats(stats_images, 5, 5, (5 + 6), (5 + 1))
    # health bar is 64 pixels long
    stats_p2 = PlayerStats(stats_images, (screen_width - 64 - 5), (screen_height - screen_height + 5),
                           ((screen_width - 64 - 5) + 6), ((screen_height - screen_height + 5) + 1))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # winning section

    handle_winning_p1 = HandleWinning(player_1)
    handle_winning_p2 = HandleWinning(player_2)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    while True:  # game loop, executes all functions and procedures

        clock.tick(FPS)

        map.draw_map(screen)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # all things that need to be called in the main loop for each player to work properly

        stats_p1.health_stats(screen, player_2)
        stats_p2.health_stats(screen, player_1)
        stats_p1.other_stats(screen.display, player_2)
        stats_p2.other_stats(screen.display, player_1)
        player_1.attack(screen)
        player_2.attack(screen)
        player_1.hit_detector(player_2, player_2_hit)
        player_2.hit_detector(player_1, player_1_hit)
        player_group.draw(screen.display)
        player_1.move(map.tile_rects, screen_rect)
        player_2.move(map.tile_rects, screen_rect)
        player_1.death(player_2)
        player_2.death(player_1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # event loop, used for looping though the player events such as key presses.

        for event in pygame.event.get():
            player_1.events(event, player_2_hit, player_2)
            player_2.events(event, player_1_hit, player_1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        player_1.player_animations()
        player_2.player_animations()
        handle_winning_p1.winner_screen(screen, green)
        handle_winning_p2.winner_screen(screen, pink)
        screen.scale()
        map.tile_rects.clear()  # without clearing this list the game would become extremely slow
        screen.display.fill(steel_blue)
        pygame.display.flip()  # an alternative and more efficient way of updating the screen in pygame


if __name__ == "__main__":  # used to help make this file run within other files
    main()
