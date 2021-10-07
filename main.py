import pygame
import sys
import random

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
steel_blue = (27, 51, 71)
cyan = (0, 255, 255)
orange = (255, 215, 0)


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
    def __init__(self, width, height, block_1_file, block_2_file):
        self.window_size = (width, height)
        self.screen = pygame.display.set_mode(self.window_size)
        self.display = pygame.Surface((width // 2, height // 2))
        self.block_1 = block_1_file
        self.block_2 = block_2_file
        self.tile_rects = []

    def draw_win(self):
        pass

    def scale(self):
        new_surface = pygame.transform.scale(self.display, self.window_size)
        self.screen.blit(new_surface, (0, 0))

    def draw_map(self):  # taken from: https://www.youtube.com/watch?v=5q7tmIlXROg
        tile_size = 16
        block_1 = pygame.image.load(self.block_1)
        block_2 = pygame.image.load(self.block_2)


        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    self.display.blit(block_1, (x * tile_size, y * tile_size))
                if tile == '2':
                    self.display.blit(block_2, (x * tile_size, y * tile_size))
                if tile != '0':
                    self.tile_rects.append(pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size))
                x += 1
            y += 1


class Player(pygame.sprite.Sprite):  # sprite class
    def __init__(self, pos_x, pos_y, image, key_left, key_right, key_down, key_up):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.img = pygame.transform.scale(self.image, (55, 40))
        self.rect.center = [pos_x, pos_y]
        self.left = key_left
        self.right = key_right
        self.down = key_down
        self.up = key_up


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700, "assets/test_block1.png", "assets/test_block2.png")

    # players
    player = Player(200, 200, "assets/player_1.png", "a", "d", "s", "w")
    player_group = pygame.sprite.Group()
    player_group.add(player)
    bg = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    while True:

        clock.tick(60)

        screen.draw_win()

        player_group.draw(screen.display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_y]:
                bg = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                screen.display.fill(bg)

        screen.scale()
        screen.draw_map()
        pygame.display.update()


if __name__ == "__main__":
    main()
pygame.quit()
