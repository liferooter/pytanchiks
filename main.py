import pygame as pg
import math as m
import random as r

pg.init()

info = pg.display.Info()
unit = m.sqrt(info.current_w * info.current_h) // 200
size = width, height = int(info.current_w * 0.5), int(info.current_h * 0.5)
player_speed_turn = 3
bullet_speed = 5 * unit
shoot_rate = 250
acceleration = 1 * unit
count_of_walls = 10
wall_id = -1
FPS = 30
shoots = pg.sprite.Group()
walls = pg.sprite.Group()


class Player(pg.sprite.Sprite):
    def __init__(self, id, clock, shoot_rate, first_color, center, start_angle, gui, second_color=(0, 0, 1),
                 third_color=(0, 0, 1), shoot_color=(0, 0, 255), shoot_sec_color=(255, 255, 0)):
        super().__init__()
        self.original_image = pg.Surface((5 * unit, 5.4 * unit))
        self.original_image.set_colorkey((0, 0, 0))
        pg.draw.rect(self.original_image, first_color, (1, 1.4 * unit, 1 * unit, 5.4 * unit - 1))
        pg.draw.rect(self.original_image, first_color, (4 * unit - 1, 1.4 * unit, 4.8 * unit, 5.4 * unit - 1))
        pg.draw.rect(self.original_image, second_color, (1 * unit, 1, 3 * unit, 4.4 * unit))
        pg.draw.rect(self.original_image, (0, 0, 0), (2 * unit - 1, 1, 1.4 * unit, 2.7 * unit))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.angle = start_angle
        self.original_center = 0
        self.GUI = gui
        self.shoot_color = shoot_color
        self.shoot_sec_color = shoot_sec_color
        self.shoot_b = shoot
        self.clock = clock
        self.current_cooldown = 0
        self.shoot_rate = shoot_rate
        self.id = id
        #(self.angle)

    def update(self):
        self.original_center = self.rect.center
        self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)
        keys = pg.key.get_pressed()
        if keys[self.GUI[2]]:  # go forward
            self.rect.move_ip(m.cos(m.radians(self.angle)) * acceleration,
                              m.sin(m.radians(self.angle)) * acceleration)
        if keys[self.GUI[1]]:  # rotate right
            self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
            self.angle -= player_speed_turn  # Value will reapeat after 359. This prevents angle to overflow.
            self.angle %= 360
            x, y = self.rect.center  # Save its current center.
            self.rect = self.image.get_rect()  # Replace old rect with new rect.
            self.rect.center = (x, y)
            #(self.angle)
        if keys[self.GUI[0]]:  # move backward
            self.rect.move_ip(-m.cos(m.radians(self.angle)) * acceleration,
                              -m.sin(m.radians(self.angle)) * acceleration)
        if keys[self.GUI[3]]: # rotate left
            self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
            self.angle += player_speed_turn
            self.angle %= 360
            x, y = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            #(self.angle)
        if keys[self.GUI[4]] and self.current_cooldown <= 0:  # shooting
            shoot(self.angle - 180, self.rect.center, self.shoot_color, self.shoot_sec_color, self.id)
            self.current_cooldown = self.shoot_rate
        else:
            self.current_cooldown -= self.clock.get_time()
        if self.rect.center[0] > width + 30:
            self.rect.center = (-30, self.rect.center[1])
        if self.rect.center[0] < -30:
            self.rect.center = (width + 30, self.rect.center[1])
        if self.rect.center[1] < -30:
            self.rect.center = (self.rect.center[0], height + 30)
        if self.rect.center[1] > height + 30:
            self.rect.center = (self.rect.center[0], -30)


class Missle(pg.sprite.Sprite):
    def __init__(self, coordinates, angle,  admin, first_color=(255, 0, 255), second_color=None):
        super().__init__()
        self.original_image = pg.Surface((6, 10))
        self.original_image.set_colorkey((0, 0, 0))
        pg.draw.rect(self.original_image, first_color, (1, 1, 5, 9))
        if second_color is not None:
            self.sec_col = second_color
        else:
            self.sec_col = first_color
        pg.draw.rect(self.original_image, self.sec_col, (2, 2, 3, 7))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = coordinates
        self.angle = angle
        self.original_center = coordinates
        self.image = pg.transform.rotate(self.original_image, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)
        self.admin = admin
        #('shooted')/

    def update(self):
        self.original_center = self.rect.center
        self.image = pg.transform.rotate(self.original_image, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)
        self.rect.move_ip(m.cos((m.radians(self.angle))) * bullet_speed, m.sin(m.radians(self.angle)) * bullet_speed)


class Simple_wall(pg.sprite.Sprite):
    def __init__(self, position, color=(50, 50, 50), circles=2, sec_col=[200, 200, 100]):
        super().__init__()
        self.sec_col = sec_col
        self.image = pg.Surface(20, 20)
        self.image.set_colorkey(0, 0, 0)
        pg.draw.circle(self.image, color, (10, 10), 4)
        for i in range(circles):
            pg.draw.circle(self.image, tuple(self.sec_col), (10, 10), r.randint(0, 3))
            self.sec_col[r.randint(0, 2)] -= r.randint(0, 50)
            for n in range(len(sec_col)):
                if self.sec_col[n] < 40:
                    self.sec_col[n] = 200
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self):
        pass


def shoot(angle, position, first_col, sec_col, admin):
    global shoots
    shoots.add(Missle(position, angle, admin, first_col, sec_col))


def shoot_del(group, size):
    buff = pg.sprite.Group()
    for i in group:
        if i.rect.left < -40 or i.rect.right > size[0] + 40 or i.rect.top < -40 or i.rect.bottom > size[1] + 40:
            group.remove(i)

screen = pg.display.set_mode(size)
time = pg.time.Clock()
players = pg.sprite.Group()
# Full player parameters
players.add(Player(0, time, shoot_rate, (255, 0, 0), (0, height // 2), -180,
                   (pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_TAB), (0, 0, 1), (0, 0, 1), (0, 0, 255), (255, 255, 0)))
# Must-have player parameters
players.add(Player(1, time, shoot_rate, (0, 255, 0), (width, height // 2), 0,
                   (pg.K_UP, pg.K_LEFT, pg.K_DOWN, pg.K_RIGHT, pg.K_RSHIFT)))
players.add(Player(2, time, shoot_rate, (0, 0, 255), (width // 2, 0), -90,
                   (pg.K_u, pg.K_h, pg.K_n, pg.K_k, pg.K_m)))
respawn = [0] * len(list(players))

while True:
    # checking exit
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()

    # making bacground
    screen.fill((200, 200, 200))
    for i in players:
        if not respawn[i.id]:
            screen.blit(i.image, i.rect)
            i.update()
        else:
            respawn[i.id] -= 1
    shoots.update()
    shoots.draw(screen)
    group = pg.sprite.Group()
    for i in players:
        for n in shoots:
            group.add(n)
            if respawn[i.id] == 0:
                if n.admin != i.id and pg.sprite.spritecollide(i, group, True):
                    respawn[i.id] = FPS
    shoot_del(shoots, size)
    pg.display.flip()
    time.tick(FPS)
