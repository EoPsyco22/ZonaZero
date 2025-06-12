import asyncio
import pygame
import random
import math

# Inicialização
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHIP_COLOR = (0, 255, 200)
ASTEROID_COLOR = (200, 200, 200)
BULLET_COLOR = (255, 230, 0)

SHIP_SIZE = 40
ASTEROID_SIZE = 50
BULLET_SIZE = 6
SHIP_SPEED = 5
BULLET_SPEED = 5
ASTEROID_SPEED_RANGE = (2, 4)
ASTEROID_SPAWN_RATE = 45

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroides Simples - Pygbag")

font = pygame.font.SysFont(None, 36)


def rot_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=(x, y))
    return rotated_image, new_rect


def get_angle(x1, y1, x2, y2):
    return -math.degrees(math.atan2(y2 - y1, x2 - x1))


class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = SHIP_SIZE
        self.speed = SHIP_SPEED
        self.angle = 0
        self.image = self.make_image()
        self.invulneravel_timer = 0

    def make_image(self):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.polygon(surf, SHIP_COLOR, [
            (self.size // 2, 0), (0, self.size), (self.size, self.size)
        ])
        return surf

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += self.speed
        self.x = max(self.size // 2, min(WIDTH - self.size // 2, self.x + dx))
        self.y = max(self.size // 2, min(HEIGHT - self.size // 2, self.y + dy))

    def update_angle(self, mouse_pos):
        self.angle = get_angle(self.x, self.y, *mouse_pos)

    def update_invulnerabilidade(self):
        if self.invulneravel_timer > 0:
            self.invulneravel_timer -= 1

    def is_invulneravel(self):
        return self.invulneravel_timer > 0

    def draw(self, win):
        if self.is_invulneravel() and (self.invulneravel_timer // 5) % 2 == 0:
            return
        rotated, rect = rot_center(self.image, self.angle, self.x, self.y)
        win.blit(rotated, rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.size = BULLET_SIZE
        self.angle = math.radians(angle)
        self.speed = BULLET_SPEED

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)

    def draw(self, win):
        pygame.draw.circle(win, BULLET_COLOR, (int(self.x), int(self.y)), self.size)

    def off_screen(self):
        return not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class Asteroid:
    def __init__(self):
        margin = 50
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = -margin
        elif side == 'bottom':
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + margin
        elif side == 'left':
            self.x = -margin
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH + margin
            self.y = random.randint(0, HEIGHT)
        angle = math.atan2(HEIGHT//2 - self.y, WIDTH//2 - self.x) + random.uniform(-0.5, 0.5)
        self.dx = math.cos(angle) * random.uniform(*ASTEROID_SPEED_RANGE)
        self.dy = math.sin(angle) * random.uniform(*ASTEROID_SPEED_RANGE)
        self.size = random.randint(ASTEROID_SIZE//2, ASTEROID_SIZE)
        self.image = self.make_image()

    def make_image(self):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surf, ASTEROID_COLOR, (self.size//2, self.size//2), self.size//2)
        return surf

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, win):
        win.blit(self.image, (self.x - self.size // 2, self.y - self.size // 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def off_screen(self):
        return (
            self.x < -self.size or self.x > WIDTH + self.size or
            self.y < -self.size or self.y > HEIGHT + self.size
        )


async def main():
    clock = pygame.time.Clock()
    ship = Ship()
    bullets = []
    asteroids = []
    spawn_timer = 0
    score = 0
    vidas = 3
    shoot_cooldown = 0

    try:
        background = pygame.image.load("background.png")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = None

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        ship.move(keys)
        ship.update_angle(mouse_pos)
        ship.update_invulnerabilidade()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        mouse_buttons = pygame.mouse.get_pressed()
        if (mouse_buttons[0] or mouse_buttons[2]) and shoot_cooldown <= 0:
            bullets.append(Bullet(ship.x, ship.y, ship.angle))
            shoot_cooldown = 10

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        spawn_timer += 10
        if spawn_timer >= ASTEROID_SPAWN_RATE:
            asteroids.append(Asteroid())
            spawn_timer = 0

        for bullet in bullets[:]:
            bullet.update()
            if bullet.off_screen(): bullets.remove(bullet)

        for asteroid in asteroids[:]:
            asteroid.update()
            if asteroid.off_screen(): asteroids.remove(asteroid)

        bullets_to_remove = []
        asteroids_to_remove = []

        for bullet in bullets:
            for asteroid in asteroids:
                if bullet.get_rect().colliderect(asteroid.get_rect()):
                    bullets_to_remove.append(bullet)
                    asteroids_to_remove.append(asteroid)
                    score += 1

        for b in bullets_to_remove:
            if b in bullets: bullets.remove(b)
        for a in asteroids_to_remove:
            if a in asteroids: asteroids.remove(a)

        for asteroid in asteroids[:]:
            if ship.get_rect().colliderect(asteroid.get_rect()) and not ship.is_invulneravel():
                asteroids.remove(asteroid)
                vidas -= 1
                ship.invulneravel_timer = 60
                if vidas <= 0:
                    return  # Encerra o jogo

        if background:
            WIN.blit(background, (0, 0))
        else:
            WIN.fill(BLACK)

        ship.draw(WIN)
        for bullet in bullets:
            bullet.draw(WIN)
        for asteroid in asteroids:
            asteroid.draw(WIN)

        score_surf = font.render(f"Pontos: {score}", True, WHITE)
        vidas_surf = font.render(f"Vidas: {vidas}", True, WHITE)
        WIN.blit(score_surf, (10, 10))
        WIN.blit(vidas_surf, (10, 40))

        pygame.draw.rect(WIN, WHITE, (0, 0, WIDTH, HEIGHT), 2)
        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
