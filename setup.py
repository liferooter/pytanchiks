import configparser
import pathlib
import math
import pygame as pg

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
    def __init__(self, coordinates, text, font_size=12, checked=False, font='Comic Sans MS'):
        super().__init__()
        self.font = pg.font.SysFont(font, font_size)
        self.font_size = font_size
        self.checked = checked
        self.text = self.font.render(text, False, (0, 0, 1))
        self.text.set_colorkey((255, 255, 255))
        self.box = pg.Surface((min(self.text.get_size()), min(self.text.get_size())))
        pg.draw.rect(self.box, (255, 255, 255), pg.Rect((0, 0), self.box.get_size()))
        pg.draw.rect(self.box, (1, 1, 1), pg.Rect((0, 0), self.box.get_size()), 8)
        self.image = pg.Surface((self.text.get_size()[0] + self.box.get_size()[0], self.text.get_size()[1]))
        self.image.blit(self.box, (0, 0))
        self.image.blit(self.text, (self.box.get_size()[0] + 1, 0))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = coordinates


ch = CheckBox((0, 0), 'kalaka', 25)
screen = pg.display.set_mode(SIZE)
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
    screen.fill((200, 200, 200))
    screen.blit(ch.image, ch.rect)
    pg.display.flip()
