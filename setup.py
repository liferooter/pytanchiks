import configparser
import pathlib
import math
import pygame as pg
import random

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

BULLET_SPEED = float(CONFIG['Bullet']['speed']) * UNIT

PORTALS_QUANTITY = int(CONFIG['Miscellaneous']['portals_quantity'])
TANKS_QUANTITY = max(1, min(int(CONFIG['Miscellaneous']['tanks_quantity']), 3))
IS_EDGES_CONNECTED = int(CONFIG['Miscellaneous']['is_edges_connected'])
FPS = int(CONFIG['Miscellaneous']['fps'])


class CheckBox(pg.sprite.Sprite):
    def __init__(self, coordinates, text, font_size=12, checked=False,
                 font='Comic Sans MS'):
        super().__init__()
        self.font = pg.font.SysFont(font, font_size)
        self.font_size = font_size
        self.coordinates = coordinates
        self.checked = checked
        self.text = self.font.render(text, False, (0, 0, 1))
        self.text.set_colorkey((255, 255, 255))
        self.box = pg.Surface(
            (min(self.text.get_size()), min(self.text.get_size())))
        self.cross = pg.Surface(self.box.get_size())
        pg.draw.circle(self.cross, (1, 1, 1), (self.cross.get_size()[0]
                                               // 2, self.cross.get_size()[1]
                                               // 2), self.box.get_size()[1]
                       // 2 - int(0.75 * UNIT))
        self.cross.set_colorkey((0, 0, 0))
        pg.draw.rect(self.box, (255, 255, 255),
                     pg.Rect((0, 0), self.box.get_size()))
        pg.draw.rect(self.box, (1, 1, 1), pg.Rect(
            (0, 0), self.box.get_size()), 1 * UNIT)
        self.image = pg.Surface(
            (self.text.get_size()[0] + self.box.get_size()[0],
                self.text.get_size()[1]))
        self.image.blit(self.box, (0, 0))
        self.image.blit(self.text, (self.box.get_size()[0] + 1, 0))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.coordinates

    def update(self):
        self.image = pg.Surface(
            (self.text.get_size()[0] + self.box.get_size()[0],
                self.text.get_size()[1]))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.coordinates
        self.image.blit(self.box, (0, 0))
        self.image.blit(self.text, (self.box.get_size()[0] + 1, 0))
        bttns = pg.mouse.get_pressed()
        pos = pg.mouse.get_pos()
        if bttns[0] and self.coordinates[0] <= pos[0] <= self.coordinates[0] + self.image.get_size()[0]\
                and self.coordinates[1] <= pos[1]\
                <= self.coordinates[1] + self.image.get_size()[1]:
            self.checked = not self.checked
            pg.time.wait(random.randint(140, 160))
        if self.checked:
            self.image.blit(self.cross, (0, 1))


ch = CheckBox((0, 0), '''kalakamalaka Danya govno!''',
              25, False, 'Arial black')
screen = pg.display.set_mode(SIZE)
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
    screen.fill((200, 200, 200))
    screen.blit(ch.image, ch.rect)
    ch.update()
    pg.display.flip()
