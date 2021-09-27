import pygame
import sys

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)


class Screen:
    def __init__(self, width, height):
        scr_width = width
        scr_height = height
        self.window = pygame.display.set_mode((scr_width, scr_height))

    def draw_win(self):
        self.window.fill(white)


class Thing(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/man.png")
        self.rect = self.image.get_rect()
        self.thing_img = pygame.transform.scale(self.image, (55, 40))
        self.rect.center = [pos_x, pos_y]


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    # man test
    man = Thing(100, 100)
    man_group = pygame.sprite.Group()
    man_group.add(man)

    while True:
        clock.tick(50)
        man_group.draw(screen.window)
        screen.draw_win()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
pygame.quit()
