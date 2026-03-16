import pygame
import sys
import random

class Fish:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (255, 165, 0)  # Orange
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.last_change_time = pygame.time.get_ticks()
        self.speed = 0.5

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_change_time > 2000:
            self.direction = random.choice(['up', 'down', 'left', 'right'])
            self.last_change_time = current_time

        if self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed

    def draw(self, surface):
        if self.direction == 'up':
            # Upper body (triangle, 3px height)
            pygame.draw.polygon(surface, self.color, [(self.x, self.y), (self.x - 2, self.y + 2), (self.x + 2, self.y + 2)])
            # Middle body (rectangle, 4px height)
            pygame.draw.rect(surface, self.color, (self.x - 2, self.y + 2, 5, 4))
            # Lower body (triangle, 3px height)
            pygame.draw.polygon(surface, self.color, [(self.x, self.y + 8), (self.x - 2, self.y + 6), (self.x + 2, self.y + 6)])
            # Side Fins
            pygame.draw.line(surface, self.color, (self.x - 3, self.y + 4), (self.x - 4, self.y + 4)) # Left fin
            pygame.draw.line(surface, self.color, (self.x + 3, self.y + 4), (self.x + 4, self.y + 4)) # Right fin
            # Tail
            pygame.draw.polygon(surface, self.color, [(self.x, self.y + 8), (self.x - 2, self.y + 10), (self.x + 2, self.y + 10)])
        elif self.direction == 'down':
            # Upper body (actually tail in this orientation)
            pygame.draw.polygon(surface, self.color, [(self.x, self.y), (self.x - 2, self.y - 2), (self.x + 2, self.y - 2)])
            # Middle body
            pygame.draw.rect(surface, self.color, (self.x - 2, self.y + 2, 5, 4))
            # Head (lower body in coord space)
            pygame.draw.polygon(surface, self.color, [(self.x, self.y + 8), (self.x - 2, self.y + 6), (self.x + 2, self.y + 6)])
            # Side Fins
            pygame.draw.line(surface, self.color, (self.x - 3, self.y + 4), (self.x - 4, self.y + 4)) 
            pygame.draw.line(surface, self.color, (self.x + 3, self.y + 4), (self.x + 4, self.y + 4))
        elif self.direction == 'left':
            # Horizontal body parts
            pygame.draw.rect(surface, self.color, (self.x + 2, self.y + 1, 4, 5))
            # Head (pointing left)
            pygame.draw.polygon(surface, self.color, [(self.x, self.y + 3), (self.x + 2, self.y + 1), (self.x + 2, self.y + 5)])
            # Tail (pointing right)
            pygame.draw.polygon(surface, self.color, [(self.x + 8, self.y + 1), (self.x + 8, self.y + 5), (self.x + 10, self.y + 3)])
        elif self.direction == 'right':
            # Horizontal body parts
            pygame.draw.rect(surface, self.color, (self.x + 2, self.y + 1, 4, 5))
            # Head (pointing right)
            pygame.draw.polygon(surface, self.color, [(self.x + 8, self.y + 3), (self.x + 6, self.y + 1), (self.x + 6, self.y + 5)])
            # Tail (pointing left)
            pygame.draw.polygon(surface, self.color, [(self.x, self.y + 3), (self.x + 2, self.y + 1), (self.x + 2, self.y + 5)])

def main():
    pygame.init()

    # Internal low resolution for pixel effect                                                                          
    internal_width = 160
    internal_height = 120
    scale = 5
    screen_width = 800
    screen_height = 600
                                                                                                                        
    screen = pygame.display.set_mode((screen_width, screen_height))                                                     
    display_surface = pygame.Surface((internal_width, internal_height))  
    pygame.display.set_caption("fish simulation")
    font = pygame.font.SysFont(None, 24)

    clock = pygame.time.Clock()
    running = True
    
    fish = Fish(80, 60)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        display_surface.fill((0, 0, 0))

        fish.update()
        fish.draw(display_surface)

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
