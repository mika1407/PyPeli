import pygame, random

# Yksinkertainen Pygame-kirjastolla tyhty peli

# äänitiedoston muuttujat
LASER_SOUND = None
EXPLOSION_SOUND = None

def init():
    pygame.init()
    pygame.mixer.init()
    scr = pygame.display.set_mode((640,480))
    scr.fill((0,0,0))

    # Ladataan äänet 
    global LASER_SOUND, EXPLOSION_SOUND
    try:
        # HUOM: Varmista, että 'laser.wav' ja 'explosion.wav' ovat samassa kansiossa!
        LASER_SOUND = pygame.mixer.Sound("laser.wav")
        EXPLOSION_SOUND = pygame.mixer.Sound("explosion.wav")
    except pygame.error as e:
        print(f"Varoitus: Äänitiedostoja ei voitu ladata: {e}")

    return scr


# Luokka mallintaa "avaruusalusta" ruudulla
class StarShip:
    def __init__(self, x, y, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.size = 1
        self.going_up = False
        self.going_down = False

    def draw(self, screen):
        # --- LIEKKITEHOSTE ---
        if self.size > 0.35:
            flame_offset = random.randint(0, 5) 
            fx_1 = self.x - 5 - flame_offset
            fy_1 = self.y + 30
            fy_2_top = self.y + 15
            fy_3_bottom = self.y + 45
            flame_color = random.choice([(255, 69, 0), (255, 140, 0), (255, 0, 0)])

            pygame.draw.polygon(screen, flame_color, 
                                ((self.x, fy_2_top), (fx_1, fy_1), (self.x, fy_3_bottom)))
        
        # --- ALUS ---
        color2 = tuple([x * 1.3 for x in self.color])
        size = self.size
        x1 = self.x
        y1 = self.y
        x2 = int(x1 + 20 * size)
        y2 = int(y1 + 10 * size)
        x3 = int(x2 + 40 * size)
        y3 = int(y2 + 20 * size)
        y4 = int(y3 + 20 * size)
        y5 = int(y4 + 10 * size)

        if self.going_up:
            y3 -= 5
        if self.going_down:
            y3 += 5

        pygame.draw.polygon(screen, color2, ((x1,y2), (x2, y1), (x3, y3), (x1, y3), (x1, y2)))
        pygame.draw.polygon(screen, self.color, ((x1,y3), (x3, y3), (x2, y5), (x1, y4), (x1, y3)))

    def up(self):
        self.y -= 1
    def down(self):
        self.y += 1
    def left(self) :
        self.x -= 1
    def right(self):
        self.x += 1

# Mallintaa yhtä avaruusaluksen ampumaa "luotia"
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_out = False

    def draw(self, screen):
        x,y = self.x, self.y
        pygame.draw.line(screen, (255,255,255), (x,y), (x+20, y))

    def update(self):
        self.x += 2
        if self.x > 640:
            self.is_out = True

# Mallintaa yhtä taustalla liikkuvan tähtikentän tähteä
class Star:
    def __init__(self, x, y, level: int):
        self.x = x
        self.y = y
        basecol = int((10 - level) / 10 * 255)
        self.rgb = (basecol, basecol, basecol)
        self.tick = 0
        self.level = level
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.rgb, (self.x, self.y), 1)

    def update(self):
        self.tick += 1
        if self.tick == self.level:
            self.tick = 0
            self.x -= 1
            if self.x == 0:
                self.x = 640
                self.y = random.randint(5,475)
    

# Mallintaa pyramidia, jotka toimivat vihollisina
class Pyramid:
    def __init__(self, y, rgb: tuple):
        self.x = 640
        self.y = y
        self.rgb = rgb
        
        self.phase = 0 # PALAUTETTU: Animaatiovaihe
        self.ticker_anim = 0 # UUSI: Animaation oma ajastin
        self.color1 = self.rgb
        self.color2 = tuple([x * 1.7 for x in self.color1])
        self.is_out = False
        self.exploding = False
        self.exp_radius = 1
        self.ticker = 0 # Räjähdyksen ajastin

    def draw(self, screen):
        if self.exploding:
            # Uusi, yksinkertaistettu räjähdys
            radius = self.exp_radius
            center = (self.x + 20, self.y + 17)
            exp_color = random.choice([(255, 165, 0), (255, 255, 0), (255, 69, 0)])
            pygame.draw.circle(screen, exp_color, center, radius, max(1, 10 - radius // 4))
            
        else:
            # --- PALAUTETTU PYÖRIVÄ ANIMAATIO ---
            top_x = self.x + 20
            top_y = self.y
            left_x = self.x
            right_x = self.x + 40
            bottom_y = self.y + 35
            
            # Animaation laskenta
            if self.phase < 20:
                mid_bottom = self.y + 35 + (self.phase // 4)
            else:
                mid_bottom = self.y + 35 + ((40 - self.phase) // 4)
            mid_x = self.x + self.phase
            
            # Piirrä kaksi osaa pyramidista
            pygame.draw.polygon(screen, self.color1, ((top_x, top_y), (right_x, bottom_y), (mid_x, mid_bottom), (top_x, top_y)))
            pygame.draw.polygon(screen, self.color2, ((top_x, top_y), (left_x, bottom_y), (mid_x, mid_bottom), (top_x, top_y)))
            
    def update(self):
        if self.exploding:
            self.ticker += 1
            if self.ticker >= 3:
                self.ticker = 0
                self.exp_radius += 1
                
                if self.exp_radius >= 40:
                    self.is_out = True
        else:
            # Pyramid liikutus
            self.x -= 1
            if self.x == -40: 
                self.is_out = True
            
            # Animaation päivitys
            self.ticker_anim += 1 
            if self.ticker_anim == 3: 
                self.ticker_anim = 0
                self.phase += 1
                if self.phase == 40:
                    self.color1, self.color2 = self.color2, self.color1
                    self.phase = 0

    def start_explode(self):
        self.exploding = True
        self.exp_radius = 1
        self.ticker = 0

class Tile:
    def __init__(self, color: int):
        self.color = color
        self.highlight = tuple([c * 1.3 for c in self.color])
        self.shadow = tuple([c * 0.7 for c in self.color])
        self.drop = tuple([c * 0.9 for c in self.color])
        self.size = 31

    def draw(self, x: int, y: int, screen, drop_top = False, drop_left = False):
        size = self.size
        pygame.draw.rect(screen, self.color, pygame.Rect(x, y, self.size, self.size))
        
        if drop_top:
            pygame.draw.rect(screen, self.drop, pygame.Rect(x, y, self.size, self.size // 2))

        if drop_left:
            pygame.draw.rect(screen, self.drop, pygame.Rect(x, y, self.size // 2, self.size))
        
        pygame.draw.line(screen, self.highlight, (x,y), (x+size, y))
        pygame.draw.line(screen, self.highlight, (x,y), (x, y+size))
        pygame.draw.line(screen, self.shadow, (x + size,y + 1), (x+size, y+size))
        pygame.draw.line(screen, self.shadow, (x,y + size), (x+size, y+size))

# Mallintaa ruudun alalaidassa rullaavaa "lattiaa"
class Floor:
    def __init__(self, color1: tuple, color2: tuple, y = 448):
        self.color1 = color1
        self.color2 = color2
        self.offset = 0
        self.t1 = Tile(color1)
        self.t2 = Tile(color2)
        self.y = y

    def draw(self, screen):
        for i in range(0,22):
            if i % 2 == 0:
                self.t1.draw(i * 32 - self.offset, self.y, screen)
            else:
                self.t2.draw(i * 32 - self.offset, self.y, screen)

    def update(self):
        self.offset += 1
        if self.offset == 64:
            self.offset = 0


class StarField:
    """ Mallintaa kokonaista skrollaavaa tähtikenttää """
    def __init__(self):
        self.stars = []
        ri = random.randint
        for i in range(1, 9):
            for j in range(20):
                self.stars.append(Star(ri(0,640), ri(5,475), i))

    def draw(self, screen):
        for star in self.stars:
            star.draw(screen)

    def update(self):
        for star in self.stars:
            star.update()
        
            

# Tarkistaa onko joku luodeista osunut viholliseen
def check_bullet_hits(bullets: list, enemies: list):
    global score
    for bullet in bullets:
        for enemy in enemies:
            # Käytä pygame.Rect() tähänkin, helpottaa, mutta tässä pysytään alkuperäisessä x/y logiikassa
            if bullet.x > enemy.x and bullet.x < enemy.x + 40 and bullet.y > enemy.y and bullet.y < enemy.y + 40 and not enemy.exploding:
                enemy.start_explode()
                if EXPLOSION_SOUND:
                    EXPLOSION_SOUND.play()
                bullet.is_out = True
                score += 100

# Tarkistaa onko joku vihollisista osunut alukseen
def check_enemy_hit(starship, enemies: list):
    # Luodaan Rect-oliot tarkempaa osumanetsintää varten
    ship_rect = pygame.Rect(starship.x, starship.y, 60, 80) # Arvioitu aluksen koko
    
    for enemy in enemies:
        enemy_rect = pygame.Rect(enemy.x, enemy.y, 40, 40) # Arvioitu Pyramidin koko
        
        # Tarkistetaan Rect-olioiden osuma (colliderect) JA ettei vihollinen ole räjähtämässä
        if ship_rect.colliderect(enemy_rect) and not enemy.exploding:
            return True
    return False


# Alustaa pelin
scr = init()
timer = pygame.time.Clock()

high = 0
lives = 3
score = 0

ri = random.randint
    

# Silmukka, jossa peli pyörii uudelleen ja uudelleen
while True:
    stars = StarField()
    bullets = []
    enemies = []

    font = pygame.font.SysFont("Arial", 24)

    ship = StarShip(250, 200, (128, 128, 0))

    left = False
    right = False
    up = False
    down = False

    floor = Floor((0,128,0), (0,64,0))


    # Varsinainen pelisilmukka, joka pyörii kunnes alus tuhoutuu
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    left = True
                elif event.key == pygame.K_RIGHT:
                    right = True
                elif event.key == pygame.K_UP:
                    up = True
                    ship.going_up = True
                elif event.key == pygame.K_DOWN:
                    down = True
                    ship.going_down = True
                elif event.key == pygame.K_SPACE:
                    bullets.append(Bullet(ship.x + 60, ship.y + 30))
                    if LASER_SOUND:
                        LASER_SOUND.play()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left = False
                elif event.key == pygame.K_RIGHT:
                    right = False
                elif event.key == pygame.K_UP:
                    up = False
                    ship.going_up = False
                elif event.key == pygame.K_DOWN:
                    down = False
                    ship.going_down = False

        # --- PÄIVITYSLOGIIKKA ---
        
        # Aluksen liike (tämä pysyy erillään näppäinsyötteen takia)
        if left:
            ship.left()
        if right:
            ship.right()
        if up:
            ship.up()
        if down:
            ship.down()

        # Uusien vihollisten luonti
        if random.randint(1,150) == 1:
            enemies.append(Pyramid(ri(5,420), (ri(0,128), ri(0,128), ri(0,128))))   

        # Muiden elementtien logiikan päivitys (update-kutsut)
        stars.update()
        floor.update()
        
        # Luotien päivitys ja poisto
        index = 0
        while index < len(bullets):
            bullets[index].update()
            if bullets[index].is_out:
                bullets.pop(index)
            else:
                index += 1

        # Vihollisten päivitys ja poisto
        index = 0
        while index < len(enemies):
            enemies[index].update()
            if enemies[index].is_out:
                enemies.pop(index)
            else:
                index += 1
        
        # Tarkastetaan osumat
        check_bullet_hits(bullets, enemies)

        # Jos vihollinen osui alukseen, silmukka päättyy
        if check_enemy_hit(ship, enemies):
            break
        
        # --- PIIRTO ---

        scr.fill((0,0,0))
        stars.draw(scr)
        floor.draw(scr)
        ship.draw(scr)

        for bullet in bullets:
            bullet.draw(scr)
        for enemy in enemies:
            enemy.draw(scr)

        # Piirretään pistetilanne yläreunaan
        text1 = font.render("Score: " + (str(score).zfill(7)), True, (255,255,255))
        text2 = font.render("Score: " + (str(score).zfill(7)), True, (128,128,128))

        scr.blit(text2, (5,5))    
        scr.blit(text1, (2,2))

        text1 = font.render("High: " + (str(high).zfill(7)), True, (255,255,255))
        text2 = font.render("High: " + (str(high).zfill(7)), True, (128,128,128))

        scr.blit(text2, (250,5))    
        scr.blit(text1, (247,2))

        # Piirretään elämien määrää kuvaavat pikkualukset
        for live in range(lives):
            sh = StarShip(450 + live*30, 10, (128,128,0))
            sh.size = 0.3
            sh.draw(scr)

        if score > high:
            high = score

        pygame.display.flip()
        
        timer.tick(200) 

    # Jos peli loppuu, väläytetään ruutu valkoisesta mustaksi...
    for i in range(222, 1, -1):
        scr.fill((i,i,i))
        pygame.display.flip()
        timer.tick(300)

    lives -= 1

    # Jos elämät loppuivat, peli loppuu kokonaan
    if lives == 0:

        # --- UUSI SUURI FONTIN MÄÄRITYS ---
        game_over_font = pygame.font.SysFont("Arial", 52)
        
        current_score = score
        current_high = high
        
        # Game Over -animaatio
        for i in range(0, 255):
            scr.fill((0,0,0)) # Täytä mustalla jokaisessa framessa
            
            # --- GAME OVER TEKSTI JA PISTEET ---
            text_go = game_over_font.render("GAME OVER", True, (i, 0, 0))
            text_go_rect = text_go.get_rect(center=(320, 180))
            scr.blit(text_go, (text_go_rect))

            text_score = font.render(f"SCORE: {str(current_score).zfill(7)}", True, (i // 2 + 128, i // 2 + 128, i // 2 + 128))
            text_score_rect = text_score.get_rect(center=(320, 240))
            scr.blit(text_score, (text_score_rect))
            
            text_high = font.render(f"HIGH SCORE: {str(current_high).zfill(7)}", True, (i // 2 + 128, i // 2 + 128, i // 2 + 128))
            text_high_rect = text_high.get_rect(center=(320, 280))
            scr.blit(text_high, (text_high_rect))
            
            # Ohjeteksti
            text_hint = font.render("PRESS ESC TO QUIT / ENTER TO RESTART", True, (i // 3 + 100, i // 3 + 100, i // 3 + 100))
            text_hint_rect = text_hint.get_rect(center=(320, 400))
            scr.blit(text_hint, (text_hint_rect))
            
            pygame.display.flip()
            timer.tick(200)

        # Odotetaan käyttäjän syötettä (ESC tai ENTER)
        while True:
            done = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit() # Sulkee pelin ESC:llä
                    else:
                        done = True # Uudelleenkäynnistys millä tahansa muulla napilla (esim. ENTER)

            if done:
                break
        
        lives = 3
        score = 0