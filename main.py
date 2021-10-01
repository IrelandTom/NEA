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

    def player_move(self, keys_pressed):
        velocity = 2
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[self.left]:  # LEFT
            self.rect.x -= velocity
        if keys_pressed[self.right]:  # RIGHT
            self.rect.x += velocity
        if keys_pressed[self.down]:  # DOWN
            self.rect.y += velocity
        if keys_pressed[self.up]:  # UP
            self.rect.y -= velocity


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    # players
    player_1 = Player(200, 200, "assets/player_1.png", pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w)
    player_2 = Player(250, 200, "assets/player_2.png", pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP)
    player_group = pygame.sprite.Group()
    player_group.add(player_1, player_2)

    while True:


        clock.tick(60)

        screen.draw_win()

        player_group.draw(screen.display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys_pressed = pygame.key.get_pressed()
        player_1.player_move(keys_pressed)
        player_2.player_move(keys_pressed)
        screen.scale()
        screen.display.fill(steel_blue)
        screen.draw_map()
        pygame.display.update()


if __name__ == "__main__":
    main()
pygame.quit()
