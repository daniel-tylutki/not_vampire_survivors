import pygame
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Not Vampire Survivors")
clock = pygame.time.Clock()
running = True

# -------------------------
# PLAYER
# -------------------------
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
        if keys[pygame.K_s]:
            self.rect.y += 3
        if keys[pygame.K_a]:
            self.rect.x -= 3
            self.image = pygame.image.load("player_sprite_flipped.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        if keys[pygame.K_d]:
            self.rect.x += 3
            self.image = pygame.image.load("player_sprite.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))

player = Player()
all_sprites = pygame.sprite.Group(player)

# -------------------------
# ENEMY
# -------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("enemy_sprite.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Simple AI: move towards the player
        if self.rect.centerx < player.rect.centerx:
            self.rect.x += 1
        elif self.rect.centerx > player.rect.centerx:
            self.rect.x -= 1
        if self.rect.centery < player.rect.centery:
            self.rect.y += 1
        elif self.rect.centery > player.rect.centery:
            self.rect.y -= 1

# -------------------------
# CAMERA
# -------------------------
camera_offset = pygame.Vector2()

# -------------------------
# WORLD GENERATION SETTINGS
# -------------------------
TILE_SIZE = 25  # size of each tile in pixels
CHUNK_SIZE = 8  # 8x8 tiles per chunk
RENDER_DISTANCE = 2  # how many chunks around the player to keep

generated_chunks = {}

def generateChunk(cx, cy):
    """Generate one chunk with random grass colors."""
    tiles = []
    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            color = random.choice([
                (20, 160, 20),   # grass
                (15, 120, 15),   # darker grass
                (25, 180, 25)    # even darker grass
            ])
            tiles.append((x, y, color))
    generated_chunks[(cx, cy)] = tiles

def unload_far_chunks(player_chunk_x, player_chunk_y):
    """Remove chunks that are outside the render distance."""
    remove_list = []
    for (cx, cy) in generated_chunks.keys():
        if abs(cx - player_chunk_x) > RENDER_DISTANCE or abs(cy - player_chunk_y) > RENDER_DISTANCE:
            remove_list.append((cx, cy))

    for key in remove_list:
        del generated_chunks[key]

# -------------------------
# GAME LOOP
# -------------------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- Update player
    all_sprites.update()

    # ---- Update camera
    camera_offset.x = player.rect.centerx - screen.get_width() // 2
    camera_offset.y = player.rect.centery - screen.get_height() // 2

    # ---- Calculate player's current chunk
    player_chunk_x = player.rect.centerx // (TILE_SIZE * CHUNK_SIZE)
    player_chunk_y = player.rect.centery // (TILE_SIZE * CHUNK_SIZE)

    # ---- Generate new chunks around player (3x3 area)
    for cy in range(player_chunk_y - RENDER_DISTANCE, player_chunk_y + RENDER_DISTANCE + 1):
        for cx in range(player_chunk_x - RENDER_DISTANCE, player_chunk_x + RENDER_DISTANCE + 1):
            if (cx, cy) not in generated_chunks:
                generateChunk(cx, cy)

    # ---- Unload chunks too far away
    unload_far_chunks(player_chunk_x, player_chunk_y)

    # ---- Draw everything
    screen.fill((0, 0, 0))

    # Draw chunks (the world)
    for (cx, cy), tiles in generated_chunks.items():
        for tx, ty, color in tiles:
            world_x = (cx * CHUNK_SIZE + tx) * TILE_SIZE
            world_y = (cy * CHUNK_SIZE + ty) * TILE_SIZE

            pygame.draw.rect(
                screen,
                color,
                (
                    world_x - camera_offset.x,
                    world_y - camera_offset.y,
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

    # Draw player
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.topleft - camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
