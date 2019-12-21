# update 0.3: portal time!

import pygame as pg
import math
import random

# initing pygame
pg.init()

# making constants
info = pg.display.Info()
unit: int = int(math.sqrt(info.current_w * info.current_h) // 200)
size = width, height = int(info.current_w * 0.7), int(info.current_h * 0.6)
player_turn_speed = 2.5
bullet_speed = 3 * unit
shoot_rate = 1000
acceleration = 2 * unit
FPS = 30
revive_rate = FPS * 3
bullet_life_time = FPS * 3
quantity_of_teleports = 12

# making usables
players = pg.sprite.Group()
shoots = pg.sprite.Group()
teleports = pg.sprite.Group()
exits = pg.sprite.Group()
teleport_enters = {i: (random.randint(0, width), random.randint(0, height)) for i in range(quantity_of_teleports)}
teleport_exits = {i: (random.randint(0, width), random.randint(0, height)) for i in range(quantity_of_teleports)}


# making in-game objects classes
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
        # (self.angle)

    def update(self):
        self.original_center = self.rect.center
        self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)
        keys = pg.key.get_pressed()
        if keys[self.GUI[2]]:  # go forward
            self.rect.move_ip(math.cos(math.radians(self.angle)) * acceleration,
                              math.sin(math.radians(self.angle)) * acceleration)
        if keys[self.GUI[1]]:  # rotate right
            self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
            self.angle -= player_turn_speed  # Value will reapeat after 359. This prevents angle to overflow.
            self.angle %= 360
            x, y = self.rect.center  # Save its current center.
            self.rect = self.image.get_rect()  # Replace old rect with new rect.
            self.rect.center = (x, y)
            # (self.angle)
        if keys[self.GUI[0]]:  # move backward
            self.rect.move_ip(-math.cos(math.radians(self.angle)) * acceleration,
                              -math.sin(math.radians(self.angle)) * acceleration)
        if keys[self.GUI[3]]:  # rotate left
            self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
            self.angle += player_turn_speed
            self.angle %= 360
            x, y = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            # (self.angle)
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

    def teleport(self, position):
        self.rect.center = position


class Missle(pg.sprite.Sprite):
    def __init__(self, coordinates, angle, admin_id, life_time, first_color=(255, 0, 255), second_color=None):
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
        self.admin_id = admin_id
        self.life_time = life_time
        # ('shooted')/

    def update(self):
        self.original_center = self.rect.center
        self.image = pg.transform.rotate(self.original_image, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)
        self.rect.move_ip(math.cos((math.radians(self.angle))) * bullet_speed,
                          math.sin(math.radians(self.angle)) * bullet_speed)
        self.life_time -= 1

    def teleport(self, position):
        self.rect.center = position


class Teleport(pg.sprite.Sprite):
    def __init__(self, id, dict, color):
        super().__init__()
        self.original_image = pg.Surface((4 * unit, 4 * unit))
        self.original_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.original_image, color, (2 * unit, 2 * unit), 2 * unit)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = dict.get(id)
        self.id = id

    def update(self):
        pass


class Teleport_exit(pg.sprite.Sprite):
    def __init__(self, id, dict, color):
        super().__init__()
        self.original_image = pg.Surface((4 * unit, 4 * unit))
        self.original_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.original_image, color, (2 * unit, 2 * unit), 2 * unit, unit // 2)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = dict.get(id)
        self.id = id

    def update(self):
        pass


# making utilities
def shoot(angle, position, first_col, sec_col, admin_id):
    global shoots, bullet_life_time
    shoots.add(Missle(position, angle, admin_id, bullet_life_time, first_col, sec_col))


def shoot_del(group, size):
    for i in group:
        if i.rect.left < -40 or i.rect.right > size[0] + 40 or i.rect.top < -40 or i.rect.bottom > size[1] + 40:
            group.remove(i)


def teleport_generator(quantity):
    global teleports, exits
    for i in range(quantity):
        color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        while abs(teleport_enters.get(i)[0] - teleport_exits.get(i)[0]) <= 10 * unit \
                and abs(teleport_enters.get(i)[1] - teleport_exits.get(i)[1]) <= 10 * unit:
            teleport_enters[i] = (random.randint(0, width), random.randint(0, height))
            teleport_exits[i] = (random.randint(0, width), random.randint(0, height))
        teleports.add(Teleport(i, teleport_enters, color))
        exits.add(Teleport_exit(i, teleport_exits, color))


# making pygame needs
screen = pg.display.set_mode(size)
pg.display.set_caption('Pytanks')
logo = pg.image.load('images/logo.png')
pg.display.set_icon(logo)
time = pg.time.Clock()

# making players:
    # full player parameters
players.add(Player(0, time, shoot_rate, (255, 0, 0), (0, height // 2), -180,
                   (pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_SPACE), (0, 0, 1), (0, 0, 1), (0, 0, 255), (255, 255, 0)))
    # must-have player parameters
players.add(Player(1, time, shoot_rate, (0, 255, 0), (width, height // 2), 0,
                   (pg.K_UP, pg.K_LEFT, pg.K_DOWN, pg.K_RIGHT, pg.K_RSHIFT)))

# making in-game constant objects
teleport_generator(quantity_of_teleports)

# generate player revive list
time_to_players_reviving = [0] * len(list(players))

while True:
    # checking exit
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()

    # making bacground
    screen.fill((200, 200, 200))
    group = pg.sprite.Group()

    # updating players
    for i in players:
        for n in teleports:
            group.add(n)
            if pg.sprite.spritecollide(i, group, False):
                i.teleport(teleport_exits.get(n.id))
            group.remove(n)
        if not time_to_players_reviving[i.id]:
            screen.blit(i.image, i.rect)
            i.update()
        else:
            time_to_players_reviving[i.id] -= 1

    # bullets updating
    for i in shoots:
        if i.life_time >= 0:
            i.update()
        else:
            shoots.remove(i)
            continue
        for n in teleports:
            group.add(n)
            if pg.sprite.spritecollide(i, group, False):
                i.teleport(teleport_exits.get(n.id))
            group.remove(n)
    shoots.draw(screen)

    # drawing statical objects
    teleports.draw(screen)
    exits.draw(screen)
    group = pg.sprite.Group()

    # updating players (again)
    for i in players:
        for n in shoots:
            group.add(n)
            if time_to_players_reviving[i.id] == 0:
                if n.admin_id != i.id and pg.sprite.spritecollide(i, group, True):
                    time_to_players_reviving[i.id] = revive_rate
    # activate utilities
    shoot_del(shoots, size)

    # updating screen
    pg.display.flip()

    time.tick(FPS)
