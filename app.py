import pygame, os, random
pygame.init()

#Window settings
WIDTH, HEIGHT = 900, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("POLDNIKS WAR")
font = pygame.font.SysFont("arial", 50)
BG_MAIN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "amongus.jpg")), (WIDTH, HEIGHT))
BG_MENU = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alpa.png")), (WIDTH, HEIGHT))

#Medicine image
ORANGE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "orange.png")), (50,50))

#Load enemy settings
ENEMY_SIZE = 80

ENEMY_ALPA = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alpa.png")), (ENEMY_SIZE, ENEMY_SIZE))
ENEMY_MURA = pygame.transform.scale(pygame.image.load(os.path.join("assets", "mura.png")), (ENEMY_SIZE, ENEMY_SIZE))
ENEMY_CHINA = pygame.transform.scale(pygame.image.load(os.path.join("assets", "china.png")), (ENEMY_SIZE, ENEMY_SIZE))

RED_LASER_ALPA = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER_MURA = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER_CHINA = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

#Load player settings
PLAYER_SIZE = 100

PLAYER_ALIHAN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alihan.png")), (PLAYER_SIZE, PLAYER_SIZE))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#load sound effects and music
HIT_SOUND = pygame.mixer.Sound('assets/hit.mp3')
LOSE_LIFE_SOUND = pygame.mixer.Sound('assets/loselife.mp3')
EAT_SOUND = pygame.mixer.Sound('assets/eat.mp3')
MENU_MUSIC = pygame.mixer.Sound('assets/menu.mp3')
MAIN_MUSIC = pygame.mixer.Sound('assets/main.mp3')

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

class Zombie:
    COOLDOWN = 30 #makes restriction of 2 bullets/second, prevents spamming

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.zombie_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0 
    
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1
    
    def move_lasers(self, vel, obj):
        self.cooldown()
        
        for laser in self.lasers:
            laser.move(vel)
            
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)

            elif laser.collision(obj):
                HIT_SOUND.play(0)
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def draw(self, win):
        win.blit(self.zombie_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(win)

class Player(Zombie):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.zombie_img = PLAYER_ALIHAN
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.zombie_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + ENEMY_SIZE + 10, self.zombie_img.get_width(), 10))#red(damage) is placed under the green(health) bar
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + ENEMY_SIZE + 10, self.zombie_img.get_width() * (self.health/self.max_health), 10))#fills the green bar with the percentage of health: 78hp -> 78% green, 22% red bar

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

class Enemy(Zombie):
    ENEMIES_MAP = {
                "ALPA": (ENEMY_ALPA, RED_LASER_ALPA),
                "MURA": (ENEMY_MURA, GREEN_LASER_MURA),
                "CHINA": (ENEMY_CHINA, BLUE_LASER_CHINA)}

    def __init__(self, x, y, enemy, health=100):
        super().__init__(x, y, health)
        self.zombie_img, self.laser_img = self.ENEMIES_MAP[enemy]
        self.mask = pygame.mask.from_surface(self.zombie_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x-10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

class Fruit(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.zombie_img = ORANGE
        self.mask = pygame.mask.from_surface(self.zombie_img)
        self.fruit = None
    
    def move(self, vel):
        self.y += vel
    
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x #distance between 2 objs
    offset_y = obj2.y - obj1.y  
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    
def pause():
    MAIN_MUSIC.stop()
    WIN.blit(BG_MENU, (0,0))
    title_label = font.render("PRESS RIGHT MOUSE BUTTON TO RESUME", 1, (255,255,255))
    WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 375))#centre of the window
    
    pygame.display.update()

def main():
    MAIN_MUSIC.play(-1)
    RUN = True
    FPS = 60
    level = 0
    lives = 5

    enemies = [] #store enemies location
    fruits = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(410, 650) #create player in the center of the bottom window
    fruit = Fruit(random.randrange(0, 800), random.randrange(-1200, -100)) #create healer(orange)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0 #seconds between changing menus

    def redraw_window():
        WIN.blit(BG_MAIN, (0,0))

        lives_label = font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))#top left
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))#top right

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        fruit.draw(WIN)
     
        if lost:
            lost_label = font.render("YOU LOST POLDNIKS :(", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 375)) #place text in the centre of the screen
            MAIN_MUSIC.stop()

        pygame.display.update()

    while RUN:
        clock.tick(FPS)
        redraw_window()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            if random.randrange(0, 100) == 1: #probabilityy of shooting 50% in 100f/s
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                HIT_SOUND.play(0)
                enemies.remove(enemy)

            if enemy.y + ENEMY_SIZE > HEIGHT:
                lives -= 1
                LOSE_LIFE_SOUND.play(0)
                enemies.remove(enemy)

            if collide(fruit, player):
                player.health = 100
                EAT_SOUND.play(0)

        player.move_lasers(-laser_vel, enemies) #-laser_vel because player shoots in opposite direction 
        fruit.move(5)

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(0, 800), random.randrange(-1200, -100), random.choice(["ALPA", "MURA", "CHINA"])) #spawn enemies out of window's height for a random time delay between them
                enemies.append(enemy)
            fruit = Fruit(random.randrange(0, 800), random.randrange(-1200, -100))
            fruits.append(fruit)

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1 

        if lost: #makes the 4s pause between lost menu and main menu
            if lost_count > 240: 
                RUN = False
            else:
                continue
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        #player movement
        if keys[pygame.K_a] and player.x - player_vel > 0: 
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + PLAYER_SIZE < WIDTH: 
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: 
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + PLAYER_SIZE + 20 < HEIGHT: #+20px due to the healthbar's height 
            player.y += player_vel
        if keys[pygame.K_SPACE] or mouse_buttons[0]:
            player.shoot()
            
        if mouse_buttons[2]:
            pause()
    
def menu():
    RUN = True
    MENU_MUSIC.play(-1)
    
    while RUN:
        WIN.blit(BG_MENU, (0,0))
        title_label = font.render("PRESS MOUSE TO BEGIN", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 375))#centre of the window
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                MENU_MUSIC.stop()
                main()
    pygame.quit()

menu()