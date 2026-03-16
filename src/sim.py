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
        self.change_interval = random.randint(500, 3000)
        self.speed = 0.5
        
        # Create a base surface for the fish (upward facing)
        self.base_surf = pygame.Surface((11, 11), pygame.SRCALPHA)
        # Coordinates relative to surface center (approx 5, 5)
        # Drawing the upward fish centered on the surface
        pygame.draw.polygon(self.base_surf, self.color, [(5, 0), (3, 2), (7, 2)])
        pygame.draw.rect(self.base_surf, self.color, (3, 2, 5, 4))
        pygame.draw.polygon(self.base_surf, self.color, [(5, 8), (3, 6), (7, 6)])
        pygame.draw.line(self.base_surf, self.color, (2, 4), (1, 4)) # Left
        pygame.draw.line(self.base_surf, self.color, (8, 4), (9, 4)) # Right
        pygame.draw.polygon(self.base_surf, self.color, [(5, 8), (3, 10), (7, 10)])

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_change_time > self.change_interval:
            self.direction = random.choice(['up', 'down', 'left', 'right'])
            self.last_change_time = current_time
            self.change_interval = random.randint(500, 3000)

        if self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed

    def draw(self, surface):
        angle_map = {'up': 0, 'down': 180, 'left': 90, 'right': 270}
        rotated_surf = pygame.transform.rotate(self.base_surf, angle_map[self.direction])
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect.topleft)

def main():
    pygame.init()

    # Internal low resolution for pixel effect                                                                          
    internal_width = 400
    internal_height = 300
    scale = 2
    screen_width = 800
    screen_height = 600
                                                                                                                        
    screen = pygame.display.set_mode((screen_width, screen_height))                                                     
    display_surface = pygame.Surface((internal_width, internal_height))  
    pygame.display.set_caption("fish simulation")
    font = pygame.font.SysFont(None, 24)

    clock = pygame.time.Clock()
    running = True
    
    fish = Fish(200, 150)

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
