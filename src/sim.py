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

        # Draw a simple pixel fish (top-down view)
        fish_color = (255, 165, 0) # Orange
        # Body
        pygame.draw.ellipse(screen, fish_color, (385, 280, 30, 40))
        # Side Fins
        pygame.draw.polygon(screen, fish_color, [(385, 295), (375, 290), (375, 300)]) # Left fin
        pygame.draw.polygon(screen, fish_color, [(415, 295), (425, 290), (425, 300)]) # Right fin
        # Tail
        pygame.draw.polygon(screen, fish_color, [(400, 320), (385, 335), (415, 335)])

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
