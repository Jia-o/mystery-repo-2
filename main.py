import pygame
import sys
import math
import random

# --- 1. Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 50
BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)

STARTING_GOLD = 100
STARTING_LIVES = 10
TOWER_COST = 25
ENEMY_REWARD = 5

BASE_HEALTH = 30
HEALTH_STEP = 10

SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
SPAWN_DELAY = 1500 

PATH = [(0, 0),  
        (SCREEN_WIDTH/3, SCREEN_HEIGHT*3/4), 
        (SCREEN_WIDTH*2/3, SCREEN_HEIGHT/2),
        (SCREEN_WIDTH, SCREEN_HEIGHT)]

# --- 2. Sprite Loading & Handling ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cats vs Spoons")

CAT_VARIATIONS = []
try:
    full_sheet = pygame.image.load("cats.png").convert_alpha()
    sheet_w, sheet_h = full_sheet.get_size() 
    CAT_W = sheet_w // 3
    CAT_H = sheet_h // 2
    
    print(f"Image loaded: {sheet_w}x{sheet_h}. Individual cat size: {CAT_W}x{CAT_H}")

    for row in range(2):
        for col in range(3):
            rect = pygame.Rect(col * CAT_W, row * CAT_H, CAT_W, CAT_H)
            cat_surf = full_sheet.subsurface(rect)
            CAT_VARIATIONS.append(pygame.transform.scale(cat_surf, (50, 50)))
    
    SPOON_IMG = pygame.image.load("spoon.png").convert_alpha()
    SPOON_IMG = pygame.transform.scale(SPOON_IMG, (40, 40))

except Exception as e:
    print(f"Error: {e}")
    backup = pygame.Surface((50, 50))
    backup.fill((0, 255, 0))
    CAT_VARIATIONS = [backup]
    SPOON_IMG = pygame.Surface((40, 40))
    SPOON_IMG.fill((200, 200, 200))

# --- 3. Classes ---
class Enemy:
    def __init__(self, path, spawn_number):
        self.path = path
        self.target_index = 0
        self.x, self.y = path[0]
        self.speed = 2
        self.angle = 0
        self.max_health = BASE_HEALTH + (spawn_number * HEALTH_STEP)
        self.health = self.max_health
        self.reached_end = False 

    def update(self):
        if self.target_index < len(self.path):
            target_x, target_y = self.path[self.target_index]
            dx, dy = target_x - self.x, target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > self.speed:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                # Calculate angle for rotation
                self.angle = math.degrees(math.atan2(-dy, dx)) - 45 # -45 to align sprite
            else:
                self.target_index += 1
        else:
            self.reached_end = True
        
    def draw(self, surface):
        # Rotate spoon towards movement direction
        rotated_spoon = pygame.transform.rotate(SPOON_IMG, self.angle)
        rect = rotated_spoon.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_spoon, rect.topleft)
        
        # Health bar
        bar_w = 30
        health_pct = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, (255, 0, 0), (self.x - 15, self.y - 25, bar_w, 4))
        pygame.draw.rect(surface, (0, 255, 0), (self.x - 15, self.y - 25, int(bar_w * health_pct), 4))

class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.range = 150
        self.damage = 10
        self.cooldown = 800  
        self.last_shot = pygame.time.get_ticks()
        self.target = None
        self.image = random.choice(CAT_VARIATIONS)

    def update(self, enemies):
        self.target = None
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                self.target = enemy
                break 

        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot > self.cooldown:
            self.target.health -= self.damage
            self.last_shot = now

    def draw(self, surface):
        pygame.draw.circle(surface, (80, 80, 80), (self.x, self.y), self.range, 1)
        
        rect = self.image.get_rect(center=(self.x, self.y))
        surface.blit(self.image, rect.topleft)
        
        if self.target:
            pygame.draw.line(surface, (255, 255, 0), (self.x, self.y), (self.target.x, self.target.y), 2)

# --- 4. Main Game Loop ---
pygame.display.set_caption("Cats vs Spoons TD")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, bold=True)
pygame.time.set_timer(SPAWN_ENEMY_EVENT, SPAWN_DELAY)

enemies, towers = [], []
gold, lives, spawn_count = STARTING_GOLD, STARTING_LIVES, 0

while True:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        if event.type == SPAWN_ENEMY_EVENT and lives > 0:
            spawn_count += 1
            enemies.append(Enemy(PATH, spawn_count))

        if event.type == pygame.MOUSEBUTTONDOWN and lives > 0:
            if gold >= TOWER_COST:
                towers.append(Tower(mx, my))
                gold -= TOWER_COST

    # Logic
    if lives > 0:
        for e in enemies[:]: 
            e.update()
            if e.reached_end:
                lives -= 1; enemies.remove(e)
            elif e.health <= 0:
                gold += ENEMY_REWARD; enemies.remove(e)
        for t in towers: t.update(enemies)
    
    # Draw
    screen.fill(BG_COLOR)
    pygame.draw.lines(screen, PATH_COLOR, False, PATH, 8)
    for t in towers: t.draw(screen)
    for e in enemies: e.draw(screen)

    # Ghost Cat
    if lives > 0:
        ghost_cat = CAT_VARIATIONS[0].copy() 
        ghost_cat.set_alpha(150)
        
        if gold < TOWER_COST:
            ghost_cat.fill((255, 0, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)
            
        screen.blit(ghost_cat, (mx-25, my-25))

    # UI
    screen.blit(font.render(f"GOLD: ${gold}", True, (255, 215, 0)), (20, 20))
    screen.blit(font.render(f"LIVES: {lives}", True, (255, 50, 50)), (20, 45))
    screen.blit(font.render(f"WAVE STRENGTH: {spawn_count}", True, (200, 200, 200)), (20, 70))

    if lives <= 0:
        over_text = font.render("GAME OVER - YOU SURVIVED " + str(spawn_count) + " ENEMIES", True, (255, 255, 255))
        screen.blit(over_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2))

    pygame.display.flip()
    clock.tick(FPS)