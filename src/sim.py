import pygame
import sys

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    # Internal low resolution for pixel effect
    internal_width = 160
    internal_height = 120
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    display_surface = pygame.Surface((internal_width, internal_height))
    pygame.display.set_caption("fish simulation")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        display_surface.fill((0, 0, 0))

        # Draw a simple pixel fish (top-down view)
        fish_color = (255, 165, 0) # Orange
        # Body
        pygame.draw.ellipse(display_surface, fish_color, (75, 55, 10, 15))
        # Side Fins
        pygame.draw.polygon(display_surface, fish_color, [(75, 62), (72, 60), (72, 64)]) # Left fin
        pygame.draw.polygon(display_surface, fish_color, [(85, 62), (88, 60), (88, 64)]) # Right fin
        # Tail
        pygame.draw.polygon(display_surface, fish_color, [(80, 70), (75, 75), (85, 75)])

        # Scale the low-res surface to the screen size
        scaled_surface = pygame.transform.scale(display_surface, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
