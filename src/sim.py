import pygame
import sys

def main():
    pygame.init()

    # Internal low resolution for pixel effect
    internal_width = 64
    internal_height = 48
    scale = 12
    screen_width = internal_width * scale
    screen_height = internal_height * scale
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    display_surface = pygame.Surface((internal_width, internal_height))
    pygame.display.set_caption("fish simulation")
    font = pygame.font.SysFont(None, 24)

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
        pygame.draw.polygon(display_surface, fish_color, [(32, 20), (30, 22), (34, 22)])
        # Middle body (rectangle, 10-6 = 4px height)
        pygame.draw.rect(display_surface, fish_color, (30, 22, 5, 4))
        # Lower body (triangle, 3px height)
        pygame.draw.polygon(display_surface, fish_color, [(32, 30), (30, 28), (34, 28)])
        # Side Fins                                                                                                     
        pygame.draw.line(display_surface, fish_color, (29, 25), (28, 25)) # Left fin                                    
        pygame.draw.line(display_surface, fish_color, (35, 25), (36, 25)) # Right fin                                   
        # Tail                                                                                                          
        pygame.draw.polygon(display_surface, fish_color, [(32, 30), (30, 32), (34, 32)])   

        # Scale the low-res surface to the screen size
        scaled_surface = pygame.transform.scale(display_surface, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))

        # Mouse coordinate tracker
        raw_mouse_x, raw_mouse_y = pygame.mouse.get_pos()
        mouse_x = raw_mouse_x // scale
        mouse_y = raw_mouse_y // scale
        coord_text = font.render(f"Pos: {mouse_x}, {mouse_y}", True, (255, 255, 255))
        screen.blit(coord_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
