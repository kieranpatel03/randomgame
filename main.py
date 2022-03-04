import pygame
import sys
from datetime import datetime, timedelta
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 500
bullets = []
spaceship_wh = [60, 50]
monster_wh = [300, 210]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load('images/space.jpeg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
monster = pygame.image.load('images/monster.png')
monster = pygame.transform.rotate(monster, 180)
monster = pygame.transform.scale(monster, (monster_wh[0], monster_wh[1]))
monster_box = pygame.Rect(550, 145, monster_wh[0], monster_wh[1])
spaceship = pygame.image.load('images/spaceship.png')
spaceship = pygame.transform.rotate(spaceship, 270)
spaceship = pygame.transform.scale(spaceship, (spaceship_wh[0], spaceship_wh[1]))
spaceship_box = pygame.Rect(100, 225, spaceship_wh[0], spaceship_wh[1])
last_bullet = datetime.utcnow()
COLLISION = pygame.USEREVENT + 1
COLLISION2 = pygame.USEREVENT + 2
boss_health = 500
explosion = pygame.image.load('images/explosion.png')
explosion = pygame.transform.scale(explosion, (50, 50))
explosions = []
spaceship_health = 50
bullets_available = 20
last_recharge = datetime.utcnow()
monster_bullets = []
start_time = [datetime.utcnow(), False]
end_time = None

def spaceship_movement(keys, box, bullets, last_bullet, bullets_available):
    if keys[pygame.K_LEFT] and box.x > 0:
        box.x -= 5
    if keys[pygame.K_RIGHT] and box.x < (WIDTH - box.width)/2:
        box.x += 5
    if keys[pygame.K_UP] and box.y > 0:
        box.y -= 5
    if keys[pygame.K_DOWN] and box.y < (HEIGHT - box.height):
        box.y += 5
    if keys[pygame.K_SPACE]:
        if last_bullet < (datetime.utcnow() - timedelta(seconds=0.1)) and bullets_available > 0:
            x_val = box.x + box.width
            y_val = box.y + (box.height)/2
            bullets.append(pygame.Rect(x_val, y_val, 10, 10))
            last_bullet = datetime.utcnow()
            bullets_available -= 1
    return last_bullet, bullets_available


def bullet_movement(bullets, monster_box, spaceship_box):
    for x in bullets:
        if monster_box.colliderect(x):
            pygame.event.post(pygame.event.Event(COLLISION))
            bullets.remove(x)
            explosions.append([x, True])
        else:
            x.x += 5
            for i in monster_bullets:
                if x.colliderect(i[0]):
                    bullets.remove(x)
                    monster_bullets.remove(i)
                    explosions.append([x, False])
    for x in monster_bullets:
        monster_bullet = x[0]
        if spaceship_box.colliderect(monster_bullet):
            pygame.event.post(pygame.event.Event(COLLISION2))
            monster_bullets.remove(x)
            explosions.append([monster_bullet, False])
        monster_bullet.x -= x[1]
        monster_bullet.y -= x[2]




def screenfill(spaceship_box, monster_box, bullets, explosion, explosions, boss_health, bullets_avaliable, spaceship_health):
    screen.blit(background, (0, 0))
    global end_time
    if boss_health <= 0:
        if start_time[1] == False:
            end_time = datetime.utcnow()
            start_time[1] = True
        screen.blit(background, (0, 0))
        myfont = pygame.font.SysFont('Comic Sans MS', 100)
        text = myfont.render(f'You Won!', False, (0, 255, 0))    
        w = (WIDTH - text.get_width())/2
        h = (HEIGHT - text.get_height())/2
        screen.blit(text, (w, h))
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        time_taken = end_time - start_time[0]
        time_taken = str(timedelta(seconds=int(time_taken.total_seconds())))
        text2 = myfont.render(f'Time Taken: {time_taken}', False, (255, 255, 255))    
        screen.blit(text2, (w, h + text.get_height()))
        pygame.display.update()
    elif spaceship_health <= 0:
        screen.blit(background, (0, 0))
        myfont = pygame.font.SysFont('Comic Sans MS', 100)
        text = myfont.render(f'Game Over!', False, (255, 0, 0))    
        w = (WIDTH - text.get_width())/2
        h = (HEIGHT - text.get_height())/2
        screen.blit(text, (w, h))
        pygame.display.update()
    else:
        for x in bullets:
            pygame.draw.circle(screen, (0, 255, 0), (x.x, x.y), 5, 0)
        for x in monster_bullets:
            monster_bullet = x[0]
            pygame.draw.circle(screen, (255, 0, 0), (monster_bullet.x, monster_bullet.y), 5, 0)
        for x in explosions:
            if x[1]:
                explosion = pygame.transform.scale(explosion, (100, 100))
            else:
                pass
            screen.blit(explosion, (x[0].x, x[0].y))
            explosions.remove(x)
        screen.blit(monster, (monster_box.x, monster_box.y))
        screen.blit(spaceship, (spaceship_box.x, spaceship_box.y))
        if boss_health > 300:
            colour = (0, 255, 0)
        elif boss_health > 100:
            colour = (255, 255, 0)
        else:
            colour = (255, 0, 0)
        width = (boss_health/500)*monster_box.width
        healthbar = pygame.Rect(monster_box.x, monster_box.y - 15, width, 15)
        pygame.draw.rect(screen, colour, healthbar)
        myfont = pygame.font.SysFont('Comic Sans MS', 20)
        if bullets_avaliable > 15:
            colour = (0, 255, 0)
        elif bullets_avaliable > 5:
            colour = (255, 255, 0)
        else:
            colour = (255, 0, 0)
        text = myfont.render(f'Bullets Available: {bullets_avaliable}', False, colour)
        screen.blit(text, (10, 10))
        if spaceship_health > 30:
            colour = (0, 255, 0)
        elif spaceship_health > 10:
            colour = (255, 255, 0)
        else:
            colour = (255, 0, 0)
        myfont = pygame.font.SysFont('Comic Sans MS', 20)
        text = myfont.render(f'Health: ', False, colour)
        t = screen.blit(text, (10, 30))
        start = t.width + t.x
        width = ((spaceship_health/50)*spaceship_box.width)*2
        healthbar = pygame.Rect(start, t.y + 12, width, 10)
        pygame.draw.rect(screen, colour, healthbar)
        pygame.display.update()


clock = pygame.time.Clock()

while True:
    clock.tick(60)
    if bullets_available < 20 and datetime.utcnow() > (last_recharge + timedelta(seconds=0.5)):
        bullets_available += 1
        last_recharge = datetime.utcnow()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == COLLISION:
            boss_health -= 3
        if event.type == COLLISION2:
            spaceship_health -= 1
    keys = pygame.key.get_pressed()
    if random.randint(0, 10) == 0:
        x_val = monster_box.x
        y_val = monster_box.y + (monster_box.height)/2
        userx = monster_box.x - spaceship_box.x
        usery = monster_box.y - spaceship_box.y
        total_distance = math.sqrt((userx**2) + (usery**2))
        unit_vectors = [userx/total_distance, usery/total_distance]
        unit_vectors = [(round(5*i, 2) + (random.randint(-1, 1)/2)) for i in unit_vectors]
        monster_bullets.append([pygame.Rect(x_val, y_val, 10, 10), *unit_vectors])
    last_bullet, bullets_available = spaceship_movement(keys, spaceship_box, bullets, last_bullet, bullets_available)
    bullet_movement(bullets, monster_box, spaceship_box)
    screenfill(spaceship_box, monster_box, bullets, explosion, explosions, boss_health, bullets_available, spaceship_health)

