import pygame
import random
import asyncio
from pathlib import Path

# Äänitiedoston muuttujat
LASER_SOUND = None
EXPLOSION_SOUND = None

def init():
    # Selaimelle optimoidut ääniasetukset (44.1kHz, 16-bit, mono/stereo)
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        pygame.mixer.init()
    except:
        print("Mixer alustus epäonnistui")
        
    scr = pygame.display.set_mode((640, 480))
    scr.fill((0, 0, 0))
    return scr

# --- LUOKAT ---

class StarShip:
    def __init__(self, x, y, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.size = 1
        self.going_up = False
        self.going_down = False

    def draw(self, screen):
        if self.size > 0.35:
            flame_offset = random.randint(0, 5) 
            fx_1 = self.x - 5 - flame_offset
            fy_1 = self.y + 30
            fy_2_top = self.y + 15
            fy_3_bottom = self.y + 45
            flame_color = random.choice([(255, 69, 0), (255, 140, 0), (255, 0, 0)])
            pygame.draw.polygon(screen, flame_color, ((self.x, fy_2_top), (fx_1, fy_1), (self.x, fy_3_bottom)))
        
        color2 = tuple([min(255, x * 1.3) for x in self.color])
        size = self.size
        x1, y1 = self.x, self.y
        x2, y2 = int(x1 + 20 * size), int(y1 + 10 * size)
        x3, y3 = int(x2 + 40 * size), int(y2 + 20 * size)
        y4, y5 = int(y3 + 20 * size), int(y3 + 30 * size)

        if self.going_up: y3 -= 5
        if self.going_down: y3 += 5

        pygame.draw.polygon(screen, color2, ((x1,y2), (x2, y1), (x3, y3), (x1, y3), (x1, y2)))
        pygame.draw.polygon(screen, self.color, ((x1,y3), (x3, y3), (x2, y5), (x1, y4), (x1, y3)))

    def up(self): self.y -= 3 
    def down(self): self.y += 3
    def left(self): self.x -= 3
    def right(self): self.x += 3

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_out = False
    def draw(self, screen):
        pygame.draw.line(screen, (255,255,255), (self.x, self.y), (self.x+20, self.y))
    def update(self):
        self.x += 8
        if self.x > 640: self.is_out = True

class Star:
    def __init__(self, x, y, level: int):
        self.x, self.y = x, y
        basecol = int((10 - level) / 10 * 255)
        self.rgb = (basecol, basecol, basecol)
        self.tick, self.level = 0, level
    def draw(self, screen):
        pygame.draw.circle(screen, self.rgb, (self.x, self.y), 1)
    def update(self):
        self.tick += 1
        if self.tick >= self.level:
            self.tick = 0
            self.x -= 1
            if self.x <= 0:
                self.x, self.y = 640, random.randint(5,475)

class Pyramid:
    def __init__(self, y, rgb: tuple):
        self.x, self.y, self.rgb = 640, y, rgb
        self.phase, self.ticker_anim = 0, 0
        self.color1 = self.rgb
        self.color2 = tuple([min(255, x * 1.7) for x in self.color1])
        self.is_out = False
        self.exploding = False
        self.exp_radius = 1
        self.ticker = 0

    def draw(self, screen):
        if self.exploding:
            radius = self.exp_radius
            center = (self.x + 20, self.y + 17)
            exp_color = random.choice([(255, 165, 0), (255, 255, 0), (255, 69, 0)])
            pygame.draw.circle(screen, exp_color, center, radius, max(1, 10 - radius // 4))
        else:
            top_x, top_y = self.x + 20, self.y
            left_x, right_x = self.x, self.x + 40
            bottom_y = self.y + 35
            if self.phase < 20: mid_bottom = self.y + 35 + (self.phase // 4)
            else: mid_bottom = self.y + 35 + ((40 - self.phase) // 4)
            mid_x = self.x + self.phase
            pygame.draw.polygon(screen, self.color1, ((top_x, top_y), (right_x, bottom_y), (mid_x, mid_bottom)))
            pygame.draw.polygon(screen, self.color2, ((top_x, top_y), (left_x, bottom_y), (mid_x, mid_bottom)))
            
    def update(self):
        if self.exploding:
            self.ticker += 1
            if self.ticker >= 3:
                self.ticker = 0
                self.exp_radius += 2
                if self.exp_radius >= 40: self.is_out = True
        else:
            self.x -= 2
            if self.x <= -40: self.is_out = True
            self.ticker_anim += 1 
            if self.ticker_anim >= 3: 
                self.ticker_anim = 0
                self.phase += 1
                if self.phase == 40:
                    self.color1, self.color2 = self.color2, self.color1
                    self.phase = 0

    def start_explode(self):
        self.exploding = True
        self.exp_radius = 1

class Tile:
    def __init__(self, color: tuple):
        self.color = color
        self.highlight = tuple([min(255, c * 1.3) for c in self.color])
        self.shadow = tuple([int(c * 0.7) for c in self.color])
        self.size = 31
    def draw(self, x, y, screen):
        pygame.draw.rect(screen, self.color, (x, y, self.size, self.size))
        pygame.draw.line(screen, self.highlight, (x,y), (x+self.size, y))
        pygame.draw.line(screen, self.highlight, (x,y), (x, y+self.size))
        pygame.draw.line(screen, self.shadow, (x+self.size, y), (x+self.size, y+self.size))
        pygame.draw.line(screen, self.shadow, (x, y+self.size), (x+self.size, y+self.size))

class Floor:
    def __init__(self, c1, c2, y=448):
        self.t1, self.t2, self.y, self.offset = Tile(c1), Tile(c2), y, 0
    def draw(self, screen):
        for i in range(0, 22):
            tile = self.t1 if i % 2 == 0 else self.t2
            tile.draw(i * 32 - self.offset, self.y, screen)
    def update(self):
        self.offset += 2
        if self.offset >= 64: self.offset = 0

class StarField:
    def __init__(self):
        self.stars = [Star(random.randint(0,640), random.randint(5,475), random.randint(1,8)) for _ in range(100)]
    def draw(self, screen):
        for s in self.stars: s.draw(screen)
    def update(self):
        for s in self.stars: s.update()

# --- APUFUNKTIOT ---

def check_bullet_hits(bullets, enemies, score):
    global EXPLOSION_SOUND
    for b in bullets:
        for e in enemies:
            if not e.exploding and e.x < b.x < e.x + 40 and e.y < b.y < e.y + 40:
                e.start_explode()
                if EXPLOSION_SOUND: EXPLOSION_SOUND.play()
                b.is_out = True
                score += 100
    return score

def check_enemy_hit(starship, enemies):
    ship_rect = pygame.Rect(starship.x, starship.y, 60, 60)
    for e in enemies:
        if not e.exploding and ship_rect.colliderect(pygame.Rect(e.x, e.y, 40, 40)):
            return True
    return False

# --- PÄÄOHJELMA (ASYNC) ---

async def main():
    global score, high, lives, LASER_SOUND, EXPLOSION_SOUND
    scr = init()
    timer = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 24)
    font_start = pygame.font.SysFont("Arial", 32)
    game_over_font = pygame.font.SysFont("Arial", 52)

    # --- ALOITUSRUUTU ---
    ready = False
    while not ready:
        scr.fill((30, 30, 30))
        ohje = font_start.render("CLICK TO START GAME", True, (255, 255, 255))
        scr.blit(ohje, (180, 220))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                ready = True
        
        await asyncio.sleep(0.1) 
    
    # LATAA ÄÄNET VASTA TÄSSÄ (Kun käyttäjä on klikannut)
    try:
        LASER_SOUND = pygame.mixer.Sound("./laser.ogg")
        EXPLOSION_SOUND = pygame.mixer.Sound("./explosion.ogg")
        print("Äänet ladattu onnistuneesti!")
    except Exception as e:
        print(f"Äänivirhe: {e}")

    high = 0
    score = 0
    lives = 3

    while True: # Uudelleenkäynnistys-silmukka
        stars = StarField()
        bullets = []
        enemies = []
        ship = StarShip(100, 200, (128, 128, 0))
        floor = Floor((0,128,0), (0,64,0))
        left, right, up, down = False, False, False, False

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: left = True
                    elif event.key == pygame.K_RIGHT: right = True
                    elif event.key == pygame.K_UP: up = True; ship.going_up = True
                    elif event.key == pygame.K_DOWN: down = True; ship.going_down = True
                    elif event.key == pygame.K_SPACE:
                        bullets.append(Bullet(ship.x + 60, ship.y + 30))
                        if LASER_SOUND: LASER_SOUND.play()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT: left = False
                    elif event.key == pygame.K_RIGHT: right = False
                    elif event.key == pygame.K_UP: up = False; ship.going_up = False
                    elif event.key == pygame.K_DOWN: down = False; ship.going_down = False

            if left: ship.left()
            if right: ship.right()
            if up: ship.up()
            if down: ship.down()

            if random.randint(1, 60) == 1:
                enemies.append(Pyramid(random.randint(5, 400), (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))))

            stars.update()
            floor.update()
            for b in bullets[:]:
                b.update()
                if b.is_out: bullets.remove(b)
            for e in enemies[:]:
                e.update()
                if e.is_out: enemies.remove(e)

            score = check_bullet_hits(bullets, enemies, score)
            if check_enemy_hit(ship, enemies):
                running = False 

            scr.fill((0, 0, 0))
            stars.draw(scr)
            floor.draw(scr)
            ship.draw(scr)
            for b in bullets: b.draw(scr)
            for e in enemies: e.draw(scr)

            scr.blit(font.render(f"Score: {str(score).zfill(7)}", True, (255,255,255)), (10, 10))
            scr.blit(font.render(f"High: {str(high).zfill(7)}", True, (200,200,200)), (250, 10))
            for i in range(lives):
                life_icon = StarShip(450 + i*30, 15, (128,128,0))
                life_icon.size = 0.3
                life_icon.draw(scr)

            if score > high: high = score
            pygame.display.flip()
            await asyncio.sleep(0) 
            timer.tick(60)

        # Kuoleman animaatio
        for i in range(30):
            scr.fill((100, 0, 0))
            pygame.display.flip()
            await asyncio.sleep(0)
            timer.tick(60)

        lives -= 1
        if lives <= 0:
            # GAME OVER RUUTU
            waiting = True
            while waiting:
                scr.fill((0, 0, 0))
                txt = game_over_font.render("GAME OVER", True, (255, 0, 0))
                scr.blit(txt, txt.get_rect(center=(320, 180)))
                scr.blit(font.render(f"FINAL SCORE: {score}", True, (200,200,200)), (240, 250))
                scr.blit(font.render("PRESS SPACE TO PLAY AGAIN", True, (150,150,150)), (180, 350))
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            waiting = False
                
                await asyncio.sleep(0.1)
            
            lives, score = 3, 0

if __name__ == "__main__":
    asyncio.run(main())