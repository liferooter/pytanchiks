import pygame as pg


pg.init()
SERV_INFO = {
    "DISPLAY": pg.display.Info(),
    "NEW_ID": 0
}

SIZE = width, height = (
    int(SERV_INFO['DISPLAY'].current_w * 0.7),
    int(SERV_INFO['DISPLAY'].current_h * 0.6)
)

containment = {'player1': (((0, height // 2), -180,
                            {
                                "FORWARD": pg.K_w,
                                "BACKWARD": pg.K_s,
                                "RIGHT": pg.K_d,
                                "LEFT": pg.K_a,
                                "SHOOT": pg.K_TAB
                            },
                            (255, 0, 0), (255, 0, 0))),
               'player3': ((width // 2, height), 90,
                           {
                               "FORWARD": pg.K_y,
                               "BACKWARD": pg.K_h,
                               "RIGHT": pg.K_j,
                               "LEFT": pg.K_g,
                               "SHOOT": pg.K_SPACE
                           },
                           (0, 255, 0), (0, 128, 0)),
               'player2': ((width, height // 2), 0,
                           {
                               "FORWARD": pg.K_UP,
                               "BACKWARD": pg.K_DOWN,
                               "RIGHT": pg.K_RIGHT,
                               "LEFT": pg.K_LEFT,
                               "SHOOT": pg.K_RSHIFT
                           },
                           (0, 0, 255), (0, 0, 255))}
