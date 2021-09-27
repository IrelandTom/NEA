import pygame

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)


class Screen:
    def __init__(self, width, height):
        width1 = width
        height1 = height
        self.window = pygame.display.set_mode((width1, height1))

    def draw_win(self):
        self.window.fill(white)
        pygame.display.update()


class Thing:
    pass


def main():
    # create objects
    clock = pygame.time.Clock()
    screen = Screen(1360, 700)

    run = True
    while run:
        clock.tick(50)
        screen.draw_win()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


if __name__ == "__main__":
    main()
pygame.quit()
