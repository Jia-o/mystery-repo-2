import pygame
import sys
import math

# --- 1. Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (30, 30, 30)
PATH_COLOR = (100, 100, 100)

# Custom event for spawning
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
SPAWN_DELAY = 1500 

#path is a list of 4 points, when an enemy reaches each point they change their direction
PATH = [(0, 0),  
        (SCREEN_WIDTH/3, SCREEN_HEIGHT*3/4), 
        (SCREEN_WIDTH*2/3, SCREEN_HEIGHT/2),
        (SCREEN_WIDTH, SCREEN_HEIGHT)]

# --- 2. Classes ---
class Enemy:
    def __init__(self, path):
        self.path = path
        self.target_index = 0
        self.x, self.y = path[0]
        self.speed = 2
        self.radius = 15
        self.color = (255, 50, 50)
        self.health = 30
        self.reached_end = False 

    def update(self):
        # Move toward waypoint
        if self.target_index < len(self.path):
            target_x, target_y = self.path[self.target_index]
            dx, dy = target_x - self.x, target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > self.speed:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                self.target_index += 1
        else:
            self.reached_end = True
        
        # Check for death
        if self.health <= 0:
            self.reached_end = True

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.damage = 10
        self.color = (0, 150, 255) 
        self.cooldown = 500  
        self.last_shot = pygame.time.get_ticks()
        self.target = None

    def find_target(self, enemies):
        self.target = None
        for enemy in enemies:
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range:
                self.target = enemy
                break 

    def update(self, enemies):
        self.find_target(enemies)
        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot > self.cooldown:
            self.target.health -= self.damage
            self.last_shot = now

    def draw(self, surface):
        # Range circle
        pygame.draw.circle(surface, (50, 50, 50), (self.x, self.y), self.range, 1)
        # Tower base
        pygame.draw.rect(surface, self.color, (self.x - 20, self.y - 20, 40, 40))
        # Visual laser
        if self.target:
            pygame.draw.line(surface, (255, 255, 0), (self.x, self.y), (self.target.x, self.target.y), 2)    

# --- 3. Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

pygame.time.set_timer(SPAWN_ENEMY_EVENT, SPAWN_DELAY)

enemies = []
towers = []

# --- 4. Main Game Loop ---
running = True
while running:
    # --- A. Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == SPAWN_ENEMY_EVENT:
            enemies.append(Enemy(PATH))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            towers.append(Tower(mx, my))

    # --- B. Game Logic (Update) ---
    # Update Enemies and remove dead ones
    for enemy in enemies[:]: 
        enemy.update()
        if enemy.reached_end:
            enemies.remove(enemy)
            
    # Update Towers
    for tower in towers:
        tower.update(enemies)
    
    # --- C. Rendering (Draw) ---
    screen.fill(BG_COLOR)
    
    # Draw Background Path
    pygame.draw.lines(screen, PATH_COLOR, False, PATH, 5)
    
    # Draw Game Objects
    for tower in towers:
        tower.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()