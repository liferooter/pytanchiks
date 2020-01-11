import pygame as pg
import math
import random
import time


# Game classes


class Tank(pg.sprite.Sprite):
    def __init__(self, _id, first_color, center, start_angle, control_keys, second_color,
                 shoot_color):
        super().__init__()
        self.x, self.y = center
        self.original_image = pg.Surface((int(5 * UNIT), int(5.4 * UNIT)))
        self.original_image.set_colorkey((0, 0, 0))
        pg.draw.rect(self.original_image, first_color,
                     (1, int(1.4 * UNIT), int(1 * UNIT),
                      int(5.4 * UNIT - 1)))
        pg.draw.rect(self.original_image, first_color,
                     (int(4 * UNIT - 1), int(1.4 * UNIT),
                      int(4.8 * UNIT), int(5.4 * UNIT - 1)))
        pg.draw.rect(self.original_image, second_color,
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
        self.last_shoot = time.time() - RECHARGE_TIME
        self.id = _id
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
            self.x += math.cos(math.radians(self.angle)) * movement * (TANK_SPEED / FPS)
            self.y += math.sin(math.radians(self.angle)) * movement * (TANK_SPEED / FPS)

        if rotation:
            self.angle += TANK_TURN_SPEED * rotation
            self.angle %= 360

    def try_to_shoot(self):
        if pg.key.get_pressed()[self.control_keys['SHOOT']] and time.time() - self.last_shoot > RECHARGE_TIME:
            missiles.add(Missile(self.rect.center, self.angle - 180, self.id, self.shoot_color))
            self.last_shoot = time.time()

    def update(self):

        self.is_alive = True

        self.move()
        self.try_to_shoot()

        if self.x > width - 2.5 * UNIT:
            self.x, self.y = width - 2.5 * UNIT, self.y

        if self.x < 2.5 * UNIT:
            self.x, self.y = 2.5 * UNIT, self.y

        if self.y < 2.5 * UNIT:
            self.x, self.y = self.x, 2.5 * UNIT

        if self.y > height - 2.5 * UNIT:
            self.x, self.y = self.x, height - 2.5 * UNIT

        original_center = (int(self.x), int(self.y))
        self.image = pg.transform.rotate(self.original_image, -self.angle + 90)
        self.rect = self.image.get_rect()
        self.rect.center = original_center


class Missile(pg.sprite.Sprite):
    def __init__(self, coordinates, angle, master_id, color=(255, 0, 255)):
        super().__init__()

        self.x, self.y = coordinates

        self.shoot_time = time.time()
        self.master_id = master_id
        self.angle = angle
        self.original_center = coordinates

        self.image = pg.Surface((UNIT, 2 * UNIT))
        self.image.set_colorkey((0, 0, 0))

        self.original_image = self.image

        pg.draw.rect(self.image, color, (1, 1, UNIT - 1, 2 * UNIT - 1))

        self.rect = self.image.get_rect()
        self.rect.center = coordinates

    def update(self):
        for i in range(10):
            self.original_center = self.rect.center
            self.image = pg.transform.rotate(self.original_image, -self.angle + 90)

            self.x += math.cos((math.radians(self.angle))) * (BULLET_SPEED / FPS / 10)
            self.y += math.sin(math.radians(self.angle)) * (BULLET_SPEED / FPS / 10)

            coordinates = int(self.x), int(self.y)
            self.rect = self.image.get_rect()  # Replace old rect with new rect.
            self.rect.center = coordinates


class PortalEntrance(pg.sprite.Sprite):
    def __init__(self, _id, coordinates_dict, color):
        super().__init__()

        self.image = pg.Surface((4 * UNIT, 4 * UNIT))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = coordinates_dict.get(_id)
        self.id = _id
        self.radius = 2 * UNIT

        pg.draw.circle(self.image, color, (2 * UNIT, 2 * UNIT), self.radius)


class PortalExit(pg.sprite.Sprite):
    def __init__(self, _id, coordinates_dict, color):
        super().__init__()

        self.image = pg.Surface((4 * UNIT, 4 * UNIT))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = coordinates_dict.get(_id)
        self.id = _id

        pg.draw.circle(self.image, color, (2 * UNIT, 2 * UNIT), 2 * UNIT, UNIT // 2)


def is_missile_in_battlefield(checked_missile):
    if checked_missile.rect.left < -10 * UNIT \
            or checked_missile.rect.right > SIZE[0] + 10 * UNIT \
            or checked_missile.rect.top < -10 * UNIT or \
            missile.rect.bottom > SIZE[1] + 10 * UNIT:
        return False
    return True


def generate_portals(quantity):
    for i in range(quantity):
        color = (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        while abs(portal_entrances_coordinates.get(i)[0] - portal_exits_coordinates.get(i)[0]) <= 10 * UNIT \
                and abs(portal_entrances_coordinates.get(i)[1] - portal_exits_coordinates.get(i)[1]) <= 10 * UNIT:
            portal_entrances_coordinates[i] = (random.randint(0, width), random.randint(0, height))
            portal_exits_coordinates[i] = (random.randint(0, width), random.randint(0, height))
        portal_entrances.add(PortalEntrance(i, portal_entrances_coordinates, color))
        portal_exits.add(PortalExit(i, portal_exits_coordinates, color))
    for i in portal_entrances:
        portal_entrances_colliders.append(pg.mask.from_surface(i.image))


def circle_collide_for_bullet(object: pg.sprite.Sprite, circle: pg.sprite.Sprite):
    vector = abs(object.rect.center[0] - circle.rect.center[0]), abs(object.rect.center[1] - circle.rect.center[1])
    collide_distance = circle.radius + math.sqrt((object.rect.top - object.rect.bottom) ** 2 +
                                                 (object.rect.right - object.rect.left) ** 2) / 2
    distance = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return distance <= collide_distance


def circle_collide_for_tank(object: pg.sprite.Sprite, circle: pg.sprite.Sprite):
    vector = abs(object.rect.center[0] - circle.rect.center[0]), abs(object.rect.center[1] - circle.rect.center[1])

    collide_distance = max(abs(object.rect.center[0] - circle.rect.center[0]), abs(object.rect.center[1] -
                                                                                   circle.rect.center[1])) / 2 + \
                       circle.radius
    distance = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return distance <= collide_distance

# Initializing PyGame
pg.init()

# Constants
info = pg.display.Info()
UNIT = int(math.sqrt(info.current_w * info.current_h) // 200)
SIZE = width, height = int(info.current_w * 0.7), int(info.current_h * 0.6)
TANK_TURN_SPEED = 2.5
BULLET_SPEED = 100 * UNIT
RECHARGE_TIME = 1
TANK_SPEED = 15 * UNIT
FPS = 30
RECOVERY_TIME = 3
FIRING_RANGE = 150 * UNIT
PORTALS_QUANTITY = 12

# Game groups
tanks = pg.sprite.Group()
missiles = pg.sprite.Group()
portal_entrances = pg.sprite.Group()
portal_exits = pg.sprite.Group()
portal_entrances_coordinates = {
    i: (random.randint(0, width), random.randint(0, height)) for i in range(PORTALS_QUANTITY)
}
portal_exits_coordinates = {i: (random.randint(0, width), random.randint(0, height)) for i in range(PORTALS_QUANTITY)}
portal_entrances_colliders = []

# Game window
screen = pg.display.set_mode(SIZE)
pg.display.set_caption('PyTanchiks')
logo = pg.image.load('images/logo.png')
pg.display.set_icon(logo)
clock = pg.time.Clock()

# Game objects

tanks.add(Tank(0, (255, 0, 0), (0, height // 2), -180,
               {
                   "FORWARD": pg.K_w,
                   "BACKWARD": pg.K_s,
                   "RIGHT": pg.K_d,
                   "LEFT": pg.K_a,
                   "SHOOT": pg.K_SPACE
               },
               (0, 0, 1), (255, 0, 0)))

tanks.add(Tank(1, (0, 0, 255), (width, height // 2), 0,
               {
                   "FORWARD": pg.K_UP,
                   "BACKWARD": pg.K_DOWN,
                   "RIGHT": pg.K_RIGHT,
                   "LEFT": pg.K_LEFT,
                   "SHOOT": pg.K_RSHIFT
               },
               (0, 0, 1), (0, 0, 255)))

# making in-game constant objects
generate_portals(PORTALS_QUANTITY)

# generate tank revive list
last_death_time = [time.time() - RECOVERY_TIME] * len(list(tanks))

while True:
    # Check if it is time to quit
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()

    # Background
    screen.fill((200, 200, 200))

    portal_entrances.draw(screen)
    portal_exits.draw(screen)

    current_portal = pg.sprite.Group()

    # Tanks update

    for tank in tanks:

        if time.time() - last_death_time[tank.id] > RECOVERY_TIME:
            screen.blit(tank.image, tank.rect)
            tank.update()
        else:
            tank.is_alive = False
            continue

        for portal_entrance in portal_entrances:
            current_portal.add(portal_entrance)

            if circle_collide_for_tank(tank, portal_entrance):
                tank.x, tank.y = (portal_exits_coordinates.get(portal_entrance.id))

            current_portal.remove(portal_entrance)

    current_missile = pg.sprite.Group()

    # bullets updating
    for missile in missiles:

        if (time.time() - missile.shoot_time) * BULLET_SPEED < FIRING_RANGE and is_missile_in_battlefield(missile):
            missile.update()
        else:
            missiles.remove(missile)
            continue

        current_missile.add(missile)

        for tank in tanks:
            if tank.is_alive and missile.master_id != tank.id and pg.sprite.spritecollide(tank, current_missile, True):
                last_death_time[tank.id] = time.time()
                tank.rect.center = tank.x, tank.y = (random.randint(0, SIZE[0]), random.randint(0, SIZE[1]))
                tank.angle = random.randint(0, 11) * 30

        for portal_entrance in portal_entrances:
            current_portal.add(portal_entrance)

            if circle_collide_for_bullet(missile, portal_entrance):
                missile.x, missile.y = (portal_exits_coordinates.get(portal_entrance.id))

            current_portal.remove(portal_entrance)

        current_missile.remove(missile)

    missiles.draw(screen)

    # updating screen
    pg.display.flip()

    clock.tick(FPS)
