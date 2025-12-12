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
        self.normal_img = pygame.transform.scale(
            pygame.image.load("player_sprite.png").convert_alpha(), (50, 50)
        )
        self.flipped_img = pygame.transform.scale(
            pygame.image.load("player_sprite_flipped.png").convert_alpha(), (50, 50)
        )

        self.image = self.normal_img
        self.rect = self.image.get_rect(center=(300, 200))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= 3
        if keys[pygame.K_s]:
            self.rect.y += 3
        if keys[pygame.K_a]:
            self.rect.x -= 3
            self.image = self.flipped_img
        if keys[pygame.K_d]:
            self.rect.x += 3
            self.image = self.normal_img


player = Player()
all_sprites = pygame.sprite.Group(player)

# -------------------------
# ENEMY
# -------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("enemy_sprite.png").convert_alpha(), (30, 30)
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1.2

    def update(self):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx * dx + dy * dy) ** 0.5

        if distance != 0:
            dx /= distance
            dy /= distance

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed


enemy_spawn_delay = 1000  # milliseconds
last_enemy_spawn = pygame.time.get_ticks()  # tracks the last spawn time
enemies = pygame.sprite.Group()

# -------------------------
# CAMERA
# -------------------------
camera_offset = pygame.Vector2()

# -------------------------
# WORLD GENERATION SETTINGS
# -------------------------
TILE_SIZE = 25
CHUNK_SIZE = 8
RENDER_DISTANCE = 2

generated_chunks = {}

def generateChunk(cx, cy):
    tiles = []
    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            color = random.choice([
                (20, 160, 20),
                (15, 120, 15),
                (25, 180, 25)
            ])
            tiles.append((x, y, color))
    generated_chunks[(cx, cy)] = tiles


def spawn_enemy_in_chunk(cx, cy, player_cx, player_cy):
    # Don't spawn in player's current chunk
    if (cx, cy) == (player_cx, player_cy):
        return

    world_x = cx * CHUNK_SIZE * TILE_SIZE
    world_y = cy * CHUNK_SIZE * TILE_SIZE

    ex = world_x + random.randint(0, CHUNK_SIZE * TILE_SIZE)
    ey = world_y + random.randint(0, CHUNK_SIZE * TILE_SIZE)

    enemy = Enemy(ex, ey)
    enemies.add(enemy)
    all_sprites.add(enemy)


def unload_far_chunks(px, py):
    remove_list = []
    for (cx, cy) in generated_chunks.keys():
        if abs(cx - px) > RENDER_DISTANCE or abs(cy - py) > RENDER_DISTANCE:
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

    all_sprites.update()

    # ---- Enemy spawn timer ----
    now = pygame.time.get_ticks()
    if now - last_enemy_spawn >= enemy_spawn_delay:
        last_enemy_spawn = now

        spawn_distance = 400
        sx = player.rect.centerx + random.randint(-spawn_distance, spawn_distance)
        sy = player.rect.centery + random.randint(-spawn_distance, spawn_distance)

        enemy = Enemy(sx, sy)
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Camera
    camera_offset.x = player.rect.centerx - screen.get_width() // 2
    camera_offset.y = player.rect.centery - screen.get_height() // 2

    # Player chunk coordinates
    player_chunk_x = player.rect.centerx // (TILE_SIZE * CHUNK_SIZE)
    player_chunk_y = player.rect.centery // (TILE_SIZE * CHUNK_SIZE)

    # Generate chunks & spawn enemies inside them
    for cy in range(player_chunk_y - RENDER_DISTANCE, player_chunk_y + RENDER_DISTANCE + 1):
        for cx in range(player_chunk_x - RENDER_DISTANCE, player_chunk_x + RENDER_DISTANCE + 1):
            if (cx, cy) not in generated_chunks:
                generateChunk(cx, cy)

                # Spawn 2–5 enemies in NEW chunks
                for _ in range(random.randint(2, 5)):
                    spawn_enemy_in_chunk(cx, cy, player_chunk_x, player_chunk_y)

    # Unload far chunks
    unload_far_chunks(player_chunk_x, player_chunk_y)

    # Rendering
    screen.fill((0, 0, 0))

    # Draw tilemap
    for (cx, cy), tiles in generated_chunks.items():
        for tx, ty, color in tiles:
            world_x = (cx * CHUNK_SIZE + tx) * TILE_SIZE
            world_y = (cy * CHUNK_SIZE + ty) * TILE_SIZE

            pygame.draw.rect(
                screen, color,
                (world_x - camera_offset.x, world_y - camera_offset.y, TILE_SIZE, TILE_SIZE)
            )

    # Draw sprites
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.topleft - camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
