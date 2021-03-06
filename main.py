import math
import pathlib
import random
import time
import configparser
import pygame as pg

# Pygame initialization

pg.init()

# Some service variables (don't change)


PREFIX = str(pathlib.Path(__file__).parent.absolute())

SERV_INFO = {
    "DISPLAY": pg.display.Info(),
    "NEW_ID": 0
}
UNIT = int(math.sqrt(SERV_INFO['DISPLAY'].current_w *
                     SERV_INFO['DISPLAY'].current_h) // 200)

SIZE = width, height = (
    int(SERV_INFO['DISPLAY'].current_w * 0.7),
    int(SERV_INFO['DISPLAY'].current_h * 0.6)
)

# Game constants

CONFIG = configparser.ConfigParser()
CONFIG.read(f'{PREFIX}/constants.cfg')

TANK_TURN_SPEED = float(CONFIG['Tank']['turn_speed'])
TANK_SPEED = float(CONFIG['Tank']['speed']) * UNIT
RECHARGE_TIME = float(CONFIG['Tank']['recharge_time'])
RECOVERY_TIME = float(CONFIG['Tank']['recovery_time'])
FIRING_RANGE = float(CONFIG['Tank']['firing_range']) * UNIT
TANK_HP = int(CONFIG['Tank']['hp'])

BULLET_SPEED = float(CONFIG['Bullet']['speed']) * UNIT

PORTALS_QUANTITY = int(CONFIG['Miscellaneous']['portals_quantity'])
TANKS_QUANTITY = max(1, min(int(CONFIG['Miscellaneous']['tanks_quantity']), 4))
IS_EDGES_CONNECTED = int(CONFIG['Miscellaneous']['is_edges_connected'])
SHOW_HP = int(CONFIG['Miscellaneous']['show_hp'])
FPS = int(CONFIG['Miscellaneous']['fps'])


# Game classes


class Tank(pg.sprite.Sprite):
    def __init__(self, center, start_angle,
                 control_keys, first_color, shoot_color):
        super().__init__()
        self.x, self.y = center
        self.hp = TANK_HP
        self.radius = 2.5 * UNIT
        self.original_image = pg.Surface((int(5 * UNIT), int(5.4 * UNIT)))
        self.original_image.set_colorkey((0, 0, 0))
        pg.draw.rect(self.original_image, first_color,
                     (1, int(1.4 * UNIT), int(1 * UNIT),
                      int(5.4 * UNIT - 1)))
        pg.draw.rect(self.original_image, first_color,
                     (int(4 * UNIT - 1), int(1.4 * UNIT),
                      int(4.8 * UNIT), int(5.4 * UNIT - 1)))
        pg.draw.rect(self.original_image, (0, 0, 1),
                     (int(1 * UNIT), 1, int(3 * UNIT),
                      int(4.4 * UNIT)))
        pg.draw.rect(self.original_image, (0, 0, 0),
                     (int(2 * UNIT - 1), 1, int(1.4 * UNIT),
                      int(2.7 * UNIT)))
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.center = center
        self.angle = start_angle
        self.original_center = 0
        self.control_keys = control_keys
        self.shoot_color = shoot_color
        self.first_color = first_color
        self.last_shoot = time.time() - RECHARGE_TIME
        if SHOW_HP:
            self.hp_pad = TextObject(str(self.hp) + 'hp left', {"file": open(fr'{PREFIX}/fonts/hp_font.ttf'),
                                                                "antialias": True, "size": int(4 * UNIT),
                                                                "color": self.first_color, "background": None},
                                     (self.rect.center[0], self.rect.top - int(2 * UNIT)))

        self.id = SERV_INFO['NEW_ID']
        SERV_INFO['NEW_ID'] += 1

        self.is_alive = True

    def move(self):
        pressed_keys = pg.key.get_pressed()
        rotation = 0
        movement = 0
        if pressed_keys[self.control_keys['RIGHT']]:
            rotation += 1
        if pressed_keys[self.control_keys['LEFT']]:
            rotation -= 1
        if pressed_keys[self.control_keys['FORWARD']]:
            movement -= 1
        if pressed_keys[self.control_keys['BACKWARD']]:
            movement += 1

        if movement:
            self.x += math.cos(math.radians(self.angle)) * \
                      movement * (TANK_SPEED / FPS)
            self.y += math.sin(math.radians(self.angle)) * \
                      movement * (TANK_SPEED / FPS)

        if rotation:
            self.angle += TANK_TURN_SPEED * rotation / FPS
            self.angle %= 360

    def try_to_shoot(self):
        if pg.key.get_pressed()[self.control_keys['SHOOT']] \
                and time.time() - self.last_shoot > RECHARGE_TIME:
            missiles.add(Missile(self.rect.center, self.angle -
                                 180, self.id, 1, self.shoot_color))
            self.last_shoot = time.time()

    def update(self):

        self.is_alive = True

        self.move()
        self.try_to_shoot()
        if SHOW_HP:
            self.hp_pad = TextObject(str(self.hp) + 'hp left', {"file": open(fr'{PREFIX}/fonts/hp_font.ttf'),
                                                                "antialias": True, "size": int(4 * UNIT),
                                                                "color": self.first_color, "background": None},
                                     (self.rect.center[0], self.rect.top - int(2 * UNIT)))
        if IS_EDGES_CONNECTED:
            if self.x > width + 2.5 * UNIT:
                self.x = -2.5 * UNIT

            if self.x < -2.5 * UNIT:
                self.x = width + 2.5 * UNIT

            if self.y > height + 2.5 * UNIT:
                self.y = -2.5 * UNIT

            if self.y < -2.5 * UNIT:
                self.y = height + 2.5 * UNIT
        else:
            if self.x > width - 2.5 * UNIT:
                self.x = width - 2.5 * UNIT

            if self.x < 2.5 * UNIT:
                self.x = 2.5 * UNIT

            if self.y > height - 2.5 * UNIT:
                self.y = height - 2.5 * UNIT

            if self.y < 2.5 * UNIT:
                self.y = 2.5 * UNIT

        original_center = (int(self.x), int(self.y))
        self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
        self.rect = self.image.get_rect()
        self.rect.center = original_center


class Missile(pg.sprite.Sprite):
    def __init__(self, coordinates, angle, master_id, damage, color=(255, 0, 255)):
        super().__init__()

        self.x, self.y = coordinates

        self.radius = UNIT

        self.shoot_time = time.time()
        self.master_id = master_id
        self.id = master_id
        self.angle = angle
        self.original_center = coordinates

        self.image = pg.Surface((UNIT, 2 * UNIT))
        self.image.set_colorkey((0, 0, 0))
        self.damage = damage

        self.original_image = self.image

        pg.draw.rect(self.image, color, (1, 1, UNIT - 1, 2 * UNIT - 1))

        self.rect = self.image.get_rect()
        self.rect.center = coordinates

    def update(self):
        for _ in range(10):
            self.original_center = self.rect.center
            self.image = pg.transform.rotate(
                self.original_image, -self.angle + 90)

            self.x += math.cos((math.radians(self.angle))) * \
                      (BULLET_SPEED / FPS / 10)
            self.y += math.sin(math.radians(self.angle)) * \
                      (BULLET_SPEED / FPS / 10)

            coordinates = int(self.x), int(self.y)
            # Replace old rect with new rect.
            self.rect = self.image.get_rect()
            self.rect.center = coordinates


class PortalEntrance(pg.sprite.Sprite):
    def __init__(self, _id, coordinates_dict, color):
        super().__init__()

        self.radius = 2 * UNIT

        self.image = pg.Surface((4 * UNIT, 4 * UNIT))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = coordinates_dict.get(_id)
        self._id = _id
        self.id = -1

        pg.draw.circle(self.image, color, (2 * UNIT, 2 * UNIT), 2 * UNIT)


class PortalExit(pg.sprite.Sprite):
    def __init__(self, _id, coordinates_dict, color):
        super().__init__()

        self.image = pg.Surface((4 * UNIT, 4 * UNIT))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = coordinates_dict.get(_id)
        self._id = _id
        self.id = -1

        pg.draw.circle(
            self.image, color,
            (2 * UNIT, 2 * UNIT), 2 * UNIT, UNIT // 2
        )


class TextObject(pg.sprite.Sprite):
    def __init__(self, text, font, coord):
        super().__init__()
        self.font = pg.font.Font(font['file'], font['size'])
        self.image = self.font.render(
            text, font['antialias'], font['color'], font['background'])
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = coord


def spritecollide(sprite, group, dokill):
    sprite_x, sprite_y = sprite.rect.center
    res = False
    for element in group:
        el_x, el_y = element.rect.center
        if (el_x - sprite_x) ** 2 + (el_y - sprite_y) ** 2 \
                <= (sprite.radius + element.radius) ** 2 \
                and element.id != sprite.id:
            if dokill:
                element.kill()
            res = True
    return res


def is_missile_in_battlefield(checked_missile):
    if checked_missile.rect.left < -10 * UNIT \
            or checked_missile.rect.right > SIZE[0] + 10 * UNIT \
            or checked_missile.rect.top < -10 * UNIT or \
            missile.rect.bottom > SIZE[1] + 10 * UNIT:
        return False
    return True


def generate_portals(quantity):
    for i in range(quantity):
        color = (random.randint(1, 255),
                 random.randint(1, 255),
                 random.randint(1, 255))

        while abs(
                portal_entrances_coordinates.get(i)[0] -
                portal_exits_coordinates.get(i)[0]
        ) <= 10 * UNIT and \
                abs(
                    portal_entrances_coordinates.get(i)[1] -
                    portal_exits_coordinates.get(i)[1]
                ) <= 10 * UNIT:
            portal_entrances_coordinates[i] = (
                random.randint(0, width),
                random.randint(0, height)
            )
            portal_exits_coordinates[i] = (
                random.randint(0, width),
                random.randint(0, height)
            )

        portal_entrances.add(PortalEntrance(
            i, portal_entrances_coordinates, color))
        portal_exits.add(PortalExit(i, portal_exits_coordinates, color))
    while pg.sprite.groupcollide(portal_entrances, tanks, False, False):
        for i in portal_entrances:
            if spritecollide(i, tanks, False):
                portal_entrances_coordinates[i.id] = random.randint(
                    0, width), random.randint(0, height)
                i.rect.center = portal_entrances_coordinates[i.id]


def create_tanks(quantity):
    templates = [(((0, height // 2), -180,
                   {
                       "FORWARD": pg.K_w,
                       "BACKWARD": pg.K_s,
                       "RIGHT": pg.K_d,
                       "LEFT": pg.K_a,
                       "SHOOT": pg.K_LSHIFT
                   },
                   (255, 0, 0), (255, 0, 0))),
                 ((width, height // 2), 0,
                  {
                      "FORWARD": pg.K_UP,
                      "BACKWARD": pg.K_DOWN,
                      "RIGHT": pg.K_RIGHT,
                      "LEFT": pg.K_LEFT,
                      "SHOOT": pg.K_RSHIFT
                  },
                  (0, 0, 255), (0, 0, 255)),
                 ((width // 2, height), 90,
                  {
                      "FORWARD": pg.K_y,
                      "BACKWARD": pg.K_h,
                      "RIGHT": pg.K_j,
                      "LEFT": pg.K_g,
                      "SHOOT": pg.K_SPACE
                  },
                  (0, 255, 0), (0, 128, 0)),
                 ((width // 2, 0), -90, {
                     "FORWARD": pg.K_o,
                     "BACKWARD": pg.K_COMMA,
                     "RIGHT": pg.K_l,
                     "LEFT": pg.K_k,
                     "SHOOT": pg.K_RALT
                 }, (255, 0, 255), (255, 255, 255))][:quantity]
    for template in templates:
        tanks.add(Tank(*template))


# Game groups


tanks = pg.sprite.Group()
missiles = pg.sprite.Group()
portal_entrances = pg.sprite.Group()
portal_exits = pg.sprite.Group()
portal_entrances_coordinates = {
    i: (
        random.randint(0, width),
        random.randint(0, height)
    ) for i in range(PORTALS_QUANTITY)
}
portal_exits_coordinates = {i: (random.randint(0, width), random.randint(
    0, height)) for i in range(PORTALS_QUANTITY)}
portal_entrances_colliders = []
score = [0 for i in range(TANKS_QUANTITY)]

# Game window
screen = pg.display.set_mode(SIZE)
pg.display.set_caption('PyTanchiks')
logo = pg.image.load(PREFIX + '/images/logo.png')
pg.display.set_icon(logo)
clock = pg.time.Clock()

# Game objects

create_tanks(TANKS_QUANTITY)

# making in-game constant objects
generate_portals(PORTALS_QUANTITY)

# generate tank revive list
last_death_time = [time.time() - RECOVERY_TIME] * len(list(tanks))


second_start_time = time.time()
frame_counter = 0

while True:
    # Check if it is time to quit
    for event in pg.event.get():
        if event.type == pg.QUIT or pg.key.get_pressed()[pg.K_HOME]:
            pg.quit()
            exit()

    # Background
    screen.fill((200, 200, 200))

    portal_entrances.draw(screen)
    portal_exits.draw(screen)

    buff_group = pg.sprite.Group()
    rendered_score = TextObject(' : '.join(list(map(str, score))),
                                {"file": open(fr'{PREFIX}/fonts/score_font.ttf'),
                                 "antialias": True, "size": 10 * UNIT,
                                 "color": (255, 0, 0), "background": None},
                                (width // 2, height - 5 * UNIT))
    screen.blit(rendered_score.image, rendered_score.rect)

    # Tanks update

    for tank in tanks:

        if time.time() - last_death_time[tank.id] > RECOVERY_TIME:
            if tank.is_alive is False:
                tank.rect.center = tank.x, tank.y = (
                    random.randint(0, width),
                    random.randint(0, height)
                )
                tank.hp = TANK_HP
            screen.blit(tank.image, tank.rect)
            if SHOW_HP:
                screen.blit(tank.hp_pad.image, tank.hp_pad.rect)
            tank.update()
        else:
            tank.is_alive = False
            continue

        for portal_entrance in portal_entrances:
            buff_group.add(portal_entrance)

            if spritecollide(tank, buff_group, False):
                tank.x, tank.y = (
                    portal_exits_coordinates.get(portal_entrance._id))

            buff_group.remove(portal_entrance)
        for missile in missiles:
            buff_group.add(missile)

            if spritecollide(tank, buff_group, True):
                tank.hp -= missile.damage
                if tank.hp <= 0:
                    last_death_time[tank.id] = time.time()
                    score[missile.master_id] += 1
                    tank.angle = random.randint(0, 360)

    # bullets updating
    for missile in missiles:

        if spritecollide(missile, missiles, True):
            missile.kill()
            continue
        if (time.time() - missile.shoot_time) * BULLET_SPEED < FIRING_RANGE \
                and is_missile_in_battlefield(missile):
            missile.update()
        else:
            missiles.remove(missile)
            continue

        for portal_entrance in portal_entrances:
            buff_group.add(portal_entrance)

            if spritecollide(missile, buff_group, False):
                missile.x, missile.y = (
                    portal_exits_coordinates.get(portal_entrance._id)
                )

            buff_group.remove(portal_entrance)

    missiles.draw(screen)

    # updating screen
    pg.display.flip()
    if time.time() - second_start_time >= 1:
        pg.display.set_caption(f"Pytanchiks| {frame_counter} FPS")
        frame_counter = 0
        second_start_time = time.time()
    else:
        frame_counter += 1

    clock.tick(FPS)
