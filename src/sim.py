import pygame
import sys

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("fish simulation")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Draw a simple pixel fish
        fish_color = (255, 165, 0) # Orange
        pygame.draw.ellipse(screen, fish_color, (380, 290, 40, 20)) # Body
        pygame.draw.polygon(screen, fish_color, [(380, 300), (365, 285), (365, 315)]) # Tail

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
