# app.py
import streamlit as st
from streamlit_pygame import st_pygame
import pygame, sys, random, math

# --- Configurações iniciais ---
WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255,255,255)
BLACK = (0,0,0)
SHIP_COLOR = (0,255,200)
ASTEROID_COLOR = (200,200,200)
BULLET_COLOR = (255,230,0)

SHIP_SIZE, ASTEROID_SIZE, BULLET_SIZE = 40, 50, 6
SHIP_SPEED, BULLET_SPEED = 5, 5
ASTEROID_SPEED_RANGE = (2,4)
ASTEROID_SPAWN_RATE = 45  # frames

# --- Auxiliares ---
def rot_center(img, ang, x, y):
    r = pygame.transform.rotate(img, ang)
    return r, r.get_rect(center=(x,y))

def get_angle(x1, y1, x2, y2):
    return -math.degrees(math.atan2(y2-y1, x2-x1))

# --- Classes ---
class Ship:
    def __init__(self):
        self.x, self.y = WIDTH//2, HEIGHT//2
        self.size, self.speed = SHIP_SIZE, SHIP_SPEED
        self.angle = 0
        self.img = self.make_img()
        self.inv = 0
    def make_img(self):
        surf = pygame.Surface((self.size,self.size), pygame.SRCALPHA)
        pygame.draw.polygon(surf, SHIP_COLOR, [(self.size//2,0),(0,self.size),(self.size,self.size)])
        return surf
    def move(self, keys):
        dx=dy=0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx-=self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx+=self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy-=self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy+=self.speed
        self.x = max(self.size//2, min(WIDTH-self.size//2, self.x+dx))
        self.y = max(self.size//2, min(HEIGHT-self.size//2, self.y+dy))
    def update_angle(self, mpos): self.angle = get_angle(self.x,self.y,*mpos)
    def update_inv(self): 
        if self.inv>0: self.inv-=1
    def is_inv(self): return self.inv>0
    def draw(self, win):
        if self.is_inv() and (self.inv//5)%2==0: return
        r, rect = rot_center(self.img, self.angle, self.x, self.y)
        win.blit(r, rect)
    def get_rect(self):
        return pygame.Rect(self.x-self.size//2,self.y-self.size//2,self.size,self.size)

class Bullet:
    def __init__(self, x, y, angle):
        self.x, self.y = x, y
        self.size, self.angle, self.speed = BULLET_SIZE, math.radians(angle), BULLET_SPEED
    def update(self):
        self.x += self.speed*math.cos(self.angle)
        self.y -= self.speed*math.sin(self.angle)
    def draw(self, win):
        pygame.draw.circle(win, BULLET_COLOR, (int(self.x),int(self.y)), self.size)
    def off(self):
        return not (0<=self.x<=WIDTH and 0<=self.y<=HEIGHT)
    def get_rect(self):
        return pygame.Rect(self.x-self.size,self.y-self.size,self.size*2,self.size*2)

class Asteroid:
    def __init__(self):
        m=50; side=random.choice(['top','bottom','left','right'])
        if side=='top': self.x=random.randint(0,WIDTH); self.y=-m
        elif side=='bottom': self.x=random.randint(0,WIDTH); self.y=HEIGHT+m
        elif side=='left': self.x=-m; self.y=random.randint(0,HEIGHT)
        else: self.x=WIDTH+m; self.y=random.randint(0,HEIGHT)
        ang=math.atan2(HEIGHT//2-self.y, WIDTH//2-self.x)+random.uniform(-.5,.5)
        sp=random.uniform(*ASTEROID_SPEED_RANGE)
        self.dx, self.dy = math.cos(ang)*sp, math.sin(ang)*sp
        self.size = random.randint(ASTEROID_SIZE//2, ASTEROID_SIZE)
        surf = pygame.Surface((self.size,self.size), pygame.SRCALPHA)
        pygame.draw.circle(surf, ASTEROID_COLOR, (self.size//2,self.size//2), self.size//2)
        self.img = surf
    def update(self): self.x+=self.dx; self.y+=self.dy
    def off(self):
        return self.x<-self.size or self.x>WIDTH+self.size or self.y<-self.size or self.y>HEIGHT+self.size
    def draw(self, win):
        win.blit(self.img,(self.x-self.size//2,self.y-self.size//2))
    def get_rect(self):
        return pygame.Rect(self.x-self.size//2,self.y-self.size//2,self.size,self.size)

# --- Loop do jogo ---
def game_loop(win):
    clock = pygame.time.Clock()
    ship = Ship()
    bullets, asteroids = [], []
    spawn, score, vidas = 0, 0, 3
    shoot_cd = 0
    font = pygame.font.SysFont(None, 36)
    running = True

    while running:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running=False

        keys = pygame.key.get_pressed()
        ship.move(keys)
        ship.update_angle((mx,my))
        ship.update_inv()

        if (pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]) and shoot_cd<=0:
            bullets.append(Bullet(ship.x, ship.y, ship.angle))
            shoot_cd = 10
        if shoot_cd>0: shoot_cd-=1

        spawn+=10
        if spawn>=ASTEROID_SPAWN_RATE:
            asteroids.append(Asteroid()); spawn=0

        for b in bullets[:]:
            b.update()
            if b.off(): bullets.remove(b)
        for a in asteroids[:]:
            a.update()
            if a.off(): asteroids.remove(a)

        for b in bullets[:]:
            for a in asteroids[:]:
                if b.get_rect().colliderect(a.get_rect()):
                    bullets.remove(b); asteroids.remove(a); score+=1; break

        for a in asteroids[:]:
            if ship.get_rect().colliderect(a.get_rect()) and not ship.is_inv():
                asteroids.remove(a)
                vidas-=1
                ship.inv = 60
                if vidas<=0: running=False

        win.fill(BLACK)
        ship.draw(win)
        for b in bullets: b.draw(win)
        for a in asteroids: a.draw(win)

        win.blit(font.render(f"Pontos: {score}", True, WHITE), (10,10))
        win.blit(font.render(f"Vidas: {vidas}", True, WHITE), (10,40))
        pygame.draw.rect(win, WHITE, (0,0,WIDTH,HEIGHT),2)
        pygame.display.flip()

    return score

# --- Streamlit ---
st.set_page_config(layout="wide")
st.title("💥 Asteroides no Streamlit")
st.write("Clique pra atirar, use WASD ou setas pra controlar a nave!")
score = st_pygame(game_loop, key="game", frame_rate=FPS, width=WIDTH, height=HEIGHT)
if score is not None:
    st.success(f"Game over! Sua pontuação: {score}")
    if st.button("Jogar de novo"):
        st.experimental_rerun()
