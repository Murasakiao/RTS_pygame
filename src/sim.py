import pygame
import sys

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    # Internal low resolution for pixel effect
    internal_width = 64
    internal_height = 48
    
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
        # Upper body (triangle, 3px height)
        pygame.draw.polygon(display_surface, fish_color, [(32, 20), (30, 23), (34, 23)])
        # Middle body (rectangle, 10-6 = 4px height)
        pygame.draw.rect(display_surface, fish_color, (30, 23, 5, 4))
        # Lower body (triangle, 3px height)
        pygame.draw.polygon(display_surface, fish_color, [(30, 27), (34, 27), (32, 30)])
        # Side Fins                                                                                                     
        pygame.draw.line(display_surface, fish_color, (29, 25), (28, 25)) # Left fin                                    
        pygame.draw.line(display_surface, fish_color, (35, 25), (36, 25)) # Right fin                                   
        # Tail                                                                                                          
        pygame.draw.polygon(display_surface, fish_color, [(32, 30), (30, 32), (34, 32)])   

        # Scale the low-res surface to the screen size
        scaled_surface = pygame.transform.scale(display_surface, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
