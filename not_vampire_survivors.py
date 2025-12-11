import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Not Vampire Survivors")
clock = pygame.time.Clock()
running = True

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player_sprite.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(300, 200))
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= 3
        if keys[pygame.K_a]:
            self.rect.x -= 3
        if keys[pygame.K_s]:
            self.rect.y += 3
        if keys[pygame.K_d]:
            self.rect.x += 3

player = Player()
all_sprites = pygame.sprite.Group(player)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    screen.fill((0, 0, 0)) # Fill the screen with black
    all_sprites.update()
    all_sprites.draw(screen) 
    pygame.display.flip() # Update the display
    clock.tick(60) # Limit to 60 frames per second