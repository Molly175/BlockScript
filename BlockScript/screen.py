import pygame as pg
import os
pg.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Screen:
    def __init__(self, W, H):
        self.screen = pg.display.set_mode((W, H))
        pg.display.set_caption("BlockScript")
        pg.display.set_icon(pg.image.load(os.path.join(BASE_DIR, "icon.png")))
        self.WIDTH = W
        self.HEIGHT = H
        self.BG = (25,25,25)
        self.FPS = 200
        self.SCALE = 1
        self.SCENE = "main_editor"
        self.MAX_SCALE = 0.5

        self.X, self.Y = -(W//2), -(H//2)
        self.old_tick = {"scale": None, "fps": self.FPS}
        self.old_scale = 1
        self.CLOCK = pg.time.Clock()
        self.base_font = pg.font.SysFont("Arial", 32)
        self._EDITOR_BUFFER = []
        self._UI_BUFFER = []

        pg.mouse.set_visible(False)
    def add_to_editor_buffer(self, element):
        self._EDITOR_BUFFER.append(element)
    def remove_from_editor_buffer(self, element):
        if element in self._EDITOR_BUFFER:
            self._EDITOR_BUFFER.remove(element)
    def add_to_ui_buffer(self, element):
        self._UI_BUFFER.append(element)
    def remove_from_ui_buffer(self, element):
        self._UI_BUFFER.remove(element)
    def get_events(self):
        return pg.event.get()
    def get_keys(self):
        return pg.key.get_pressed()
    def get_mouse_pos(self, world=True):
        mx, my = pg.mouse.get_pos()
        if world:
            return (mx / self.SCALE + self.X,my / self.SCALE + self.Y)
        else:
            return mx, my
    def get_mouse_press(self):
        return pg.mouse.get_pressed()
    def draw_editor(self):
        for element in self._EDITOR_BUFFER:
            for value in element.values():
                if not value or type(value) != list:
                    continue
                if value[0] == "rect":
                    x = (value[2][0] - self.X) * self.SCALE
                    y = (value[2][1] - self.Y) * self.SCALE
                    w = value[2][2] * self.SCALE
                    h = value[2][3] * self.SCALE
                    pg.draw.rect(self.screen, value[1], (x, y, w, h), value[3]*max(1,int(self.SCALE)), value[4]*max(1,int(self.SCALE)))
                elif value[0] == "circle":
                    x = (value[2][0] - self.X) * self.SCALE
                    y = (value[2][1] - self.Y) * self.SCALE
                    r = value[2][2] * self.SCALE
                    pg.draw.circle(self.screen, value[1], (x, y), r)
                elif value[0] == "line":
                    x1 = (value[2][0] - self.X) * self.SCALE
                    y1 = (value[2][1] - self.Y) * self.SCALE
                    x2 = (value[3][0] - self.X) * self.SCALE
                    y2 = (value[3][1] - self.Y) * self.SCALE
                    pg.draw.line(
                        self.screen,
                        value[1],
                        (x1, y1),
                        (x2, y2),
                        max(1, int(value[4] * self.SCALE))
                    )
                elif value[0] == "point":
                    x = (value[1][0] - self.X) * self.SCALE
                    y = (value[1][1] - self.Y) * self.SCALE
                    r = value[3] * self.SCALE
                    pg.draw.circle(self.screen, value[2], (x, y), r)
                elif value[0] == "image":
                    img = value[1]["image"]
                    pos = value[1]["pos"]
                    x = (pos[0] - self.X) * self.SCALE
                    y = (pos[1] - self.Y) * self.SCALE
                    scaled_img = pg.transform.scale(img,(int(img.get_width() * self.SCALE),int(img.get_height() * self.SCALE)))
                    self.screen.blit(scaled_img, (x, y))
            for key, value in element.items():
                if key == "menu_btn":
                    for element_2 in value.values():
                        for value_2 in element_2.values():
                            if value_2[0] == "rect":
                                x = (value_2[2][0] - self.X) * self.SCALE
                                y = (value_2[2][1] - self.Y) * self.SCALE
                                w = value_2[2][2] * self.SCALE
                                h = value_2[2][3] * self.SCALE
                                pg.draw.rect(self.screen, value_2[1], (x, y, w, h))
                            elif value_2[0] == "image":
                                img = value_2[1]["image"]
                                pos = value_2[1]["pos"]
                                x = (pos[0] - self.X) * self.SCALE
                                y = (pos[1] - self.Y) * self.SCALE
                                scaled_img = pg.transform.scale(img,(int(img.get_width() * self.SCALE),int(img.get_height() * self.SCALE)))
                                self.screen.blit(scaled_img, (x,y))
                        continue
        self._EDITOR_BUFFER.clear()
    def draw_grid(self):
        offset_x = (self.X % 100 - 50) * self.SCALE
        offset_y = (self.Y % 100 - 50) * self.SCALE
        scale = self.SCALE
        width = self.WIDTH
        height = self.HEIGHT
        screen = self.screen
        draw_line = pg.draw.line
        for x in range(0, int(width/self.MAX_SCALE)+2, 100):
            sx = x * scale - offset_x
            draw_line(screen, (0, 0, 0), (sx, 0), (sx, height), 5)
        for y in range(0, int(height/self.MAX_SCALE)+2, 100):
            sy = y * scale - offset_y
            draw_line(screen, (0, 0, 0), (0, sy), (width, sy), 5)
    def draw_ui(self, dt, tick):
        if tick%(self.FPS/10) == 0 and round(1/dt) != self.old_tick["fps"]:
            self.old_tick["fps"] = round(1/dt)
        self.screen.blit(self.base_font.render(str(self.old_tick["fps"]), True, (200,200,200)), (50,50))
        if self.SCALE != self.old_scale:
            self.old_tick["scale"] = tick+self.FPS*2
            self.screen.blit(self.base_font.render(f"{self.SCALE}x", True, (200,200,200)), (50, 85))
            self.old_scale = self.SCALE
        if self.old_tick["scale"] is not None:
            if tick >= self.old_tick["scale"]:
                self.old_tick["scale"] = None
            else:
                self.screen.blit(self.base_font.render(f"{self.SCALE}x", True, (200,200,200)), (50, 85))
        for element in self._UI_BUFFER:
            for value in element.values():
                if value[0] == "rect":
                    pg.draw.rect(self.screen, value[1], value[2])
                if value[0] == "circle":
                    pg.draw.circle(self.screen, value[1], (value[2][0], value[2][1]), value[2][2])
                if value[0] == "image":
                    self.screen.blit(value[1]["image"], value[1]["pos"])
    def update(self):
        pg.display.flip()