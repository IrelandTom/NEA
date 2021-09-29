from typing import Tuple

import pygame
import sys

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
steel_blue = (27, 51, 71)

# below function taken from: https://www.youtube.com/watch?v=5q7tmIlXROg

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


class Screen:
    def __init__(self, width, height):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((width // 2, height // 2))

    def draw_win(self):
        pass

    def scale(self):
        new_surface = pygame.transform.scale(self.display, self.window_size)
        self.screen.blit(new_surface, (0, 0))

    def draw_map(self):  # taken from: https://www.youtube.com/watch?v=5q7tmIlXROg
        tile_size = 16
        block_1 = pygame.image.load("assets/test_block1.png")
        block_2 = pygame.image.load("assets/test_block2.png")

        tile_rects = []
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
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/man.png").convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.thing_img = pygame.transform.scale(self.image, (55, 40))
        self.rect.center = [pos_x, pos_y]

    def player_move(self):
        pass


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    # man test
    man = Player(200, 200)
    man_group = pygame.sprite.Group()
    man_group.add(man)

    screen.display.fill(steel_blue)

    screen.draw_map()

    while True:
        clock.tick(50)
        screen.draw_win()

        man_group.draw(screen.display)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        screen.scale()


if __name__ == "__main__":
    main()
pygame.quit()
