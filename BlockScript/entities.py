import pygame as pg
import math, os, time
pg.init()
pg.mixer.init()
DATA = {
    # "":{"width":,"height":,"attribute":{"keywords":[],"Inputs":,"Outputs":}}
    "Start":{"width":100,"height":100,"attributes":{"keywords":["Immortal","NoCreate"],"Outputs":1}},
    "End":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":1}},

    "Print":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":1}},
    "Set Value":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":1}},
    "Delete Value":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":1}},

    "If":{"width":150,"height":100,"attributes":{"keywords":[],"Inputs":1,"Outputs":2}},
    "Else":{"width":150,"height":100,"attributes":{"keywords":[],"Inputs":1,"Outputs":1}},

    "Repeat":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":2,"Outputs":1}},
    "For":{"width":150,"height":100,"attributes":{"keywords":[],"Inputs":2,"Outputs":1}},
    "While":{"width":150,"height":100,"attributes":{"keywords":[],"Inputs":2,"Outputs":1}},

    "Math":{"width":150,"height":150,"attributes":{"keywords":[],"Inputs":1}},
    "Random":{"width":150,"height":150,"attributes":{"keywords":[],"Inputs":1,"Outputs":2}}
}
DATA = {
    "Start":{"width":100,"height":100,"attributes":{"keywords":["Immortal","NoCreate"],"Outputs":1}},
    "End":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":1}},
    "Print":{"width":100,"height":100,"attributes":{"keywords":[],"Inputs":1}}
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def lerp(a, b, t):
    return a + (b - a) * t
class Cursor:
    def __init__(self):
        self.cursor_image_path = os.path.join(BASE_DIR, "cursors")
        self.image = None
        self.cursor_name = "View"
        self.cursor_name_mode = None
        self.cursor_addiction = None
        self.cursor_mode = "arrow"
        self.cursor_size_mul = 1
        self.color_const = {
            "View": [[(255,0,0),(0,162,232)],[(0,0,255),(255,255,255)]],
            "Drag": [[(255,0,0),(255,127,39)],[(0,0,255),(255,255,255)]],
            "Line": {"Build": [[(255,0,0),(195,195,195)],[(0,0,255),(34,177,76)]], "Delete": [[(255,0,0),(195,195,195)],[(0,0,255),(237,28,36)]]},
            "Block": {"Build": [[(255,0,0),(100,100,100)],[(0,0,255),(34,177,76)]], "Delete": [[(255,0,0),(100,100,100)],[(0,0,255),(237,28,36)]]}
        }
    def replace_color(self, surface, old_color, new_color):
        width, height = surface.get_size()
        for x in range(width):
            for y in range(height):
                if surface.get_at((x, y)) == old_color:
                    surface.set_at((x, y), new_color)
    def set_cursor_addiction(self, new_addiction=None):
        if new_addiction is not None and self.cursor_addiction is None:
            self.cursor_addiction = new_addiction
        elif new_addiction is None and self.cursor_addiction is not None:
            self.cursor_addiction = None
    def draw(self, surface):
        mx, my = surface.get_mouse_pos(False)
        with open(f"{os.path.join(self.cursor_image_path, self.cursor_mode)}.png") as image:
            image = pg.image.load(image)
            if self.cursor_name not in ["Line","Block"]:
                for index in self.color_const[self.cursor_name]:
                    self.replace_color(image, index[0], index[1])
            else:
                for index in self.color_const[self.cursor_name][self.cursor_name_mode]:
                    self.replace_color(image, index[0], index[1])
            image.set_colorkey((150,150,150))
            image_rect = image.get_rect()
            surface.screen.blit(pg.transform.scale(image, (image_rect.width/(2.5*self.cursor_size_mul), image_rect.height/(2.5*self.cursor_size_mul))), (mx-(5 if self.cursor_mode=="hand"else 0),my))
        if self.cursor_addiction is not None:
            with open(f"{os.path.join(self.cursor_image_path, self.cursor_addiction)}.png") as image_add:
                image_add = pg.image.load(image_add).convert()
                self.replace_color(image_add, (255,0,0),(255,127,39))
                image_add.set_colorkey((150,150,150))
                image_add_rect = image_add.get_rect()
                surface.screen.blit(pg.transform.scale(image_add, (image_add_rect.width/(2.5*self.cursor_size_mul)+10, image_add_rect.height/(2.5*self.cursor_size_mul)+10)), (mx+14,my-3))
class Menu:
    def __init__(self, type, x, y):
        self._elements = {}
        self._buttons = {}
        self.type = type
        if type == "regular": self.width, self.height = 100, 50
        if type == "block": self.width, self.height = 150, 50
        if type == "sub_create": self.width, self.height = 100, (50*(len(DATA.keys())-1))
        self.x = x
        self.y = y
        self.base_color = (75,75,75)
        self.secondary_color = (125,125,125)
        self.font = pg.font.SysFont("Arial", 16)
        self._hitbox = pg.Rect(self.x, self.y, self.width, self.height)
        self._create_block()
    def _add_block_base(self, x=0, y=0, width=10, height=10):
        self._add_rect("base", x, y, "both", width, height, self.base_color, border_radius=10)
        self._add_rect("outline", x, y, "both", width, height, self.secondary_color, 5, 10)
    def _add_rect(self, name, x=0, y=0, center="none", width=10, height=10, color=(0,0,0), rect_width=0, border_radius=0):
        if not center in ["none", "x", "y", "both"]: return
        new_width, new_height = width+rect_width, height+rect_width
        self._elements[name] = ["rect", color, pg.Rect(x-(new_width/2 if center in ["x", "both"] else 0), y-(new_height/2 if center in ["y", "both"] else 0), new_width, new_height), rect_width, border_radius]
    def _create_button(self, name, button):
        self._buttons[name] = button
    def _create_block(self):
        self._add_block_base(self.x+(self.width/2), self.y+(self.height/2), self.width, self.height)
        if self.type == "regular":
            self._create_button("create_btn", [self.Button(self, "create", "Create     >", self.x+10, self.y-(self.height/2 if self.type=="sub_create"else 0)+10, self.width-20, 30), ""])
        if self.type == "block":
            self._create_button("open_parameters_btn", self.Button(self, "open_param", "Open parameters", self.x+10, self.y+10, self.width-20, 30))
        if self.type == "sub_create":
            idx = 0
            for block_name, block_data in DATA.items():
                if "NoCreate" in block_data["attributes"]["keywords"]: continue
                idx += 1
                self._create_button(f"create_{block_name.lower()}", [self.Button(self, f"block_{block_name.lower()}", block_name, self.x+10, self.y+idx*35-25, self.width-20, 30), block_name])
    def is_collide_in_point(self, pos):
        return self._hitbox.collidepoint(pos)
    def get_elements(self):
        elements = self._elements.copy()
        elements["menu_btn"] = {name: btn[0].get_elements() if type(btn) == list else btn.get_elements() for name, btn in self._buttons.items()}
        return elements
    def update_buttons_hover(self, mouse_pos, cursor_class):
        button_all_hover = []
        for btn in self._buttons.values():
            if type(btn) == list:
                btn[0].update_hitbox()
                button_all_hover.append(btn[0].update_hover(mouse_pos))
            if type(btn) == self.Button:
                btn.update_hitbox()
                button_all_hover.append(btn.update_hover(mouse_pos))
        if any(button_all_hover):
            cursor_class.cursor_mode = "hand"
        else:
            cursor_class.cursor_mode = "arrow"
    def check_buttons_click(self, mouse_pos):
        for name, btn in self._buttons.items():
            if type(btn) == list:
                if btn[0].is_collide(mouse_pos):
                    return name, btn[1]
            if type(btn) == self.Button:
                if btn.is_collide(mouse_pos):
                    return name
        return None
    class Button:
        def __init__(self, master, type, name, x, y, width, height):
            self.master = master
            self.type = type
            self.name = name
            self.x, self.y = x, y
            self.width, self.height = width, height
            self.color = (55,55,55)
            self._elements = {}
            self._hitbox = pg.Rect(x, y, width, height)
            self._create_button()
        def _create_button(self):
            self._elements.clear()
            self._elements["rect"] = ["rect", self.color, pg.Rect(self.x, self.y, self.width, self.height), 0, 0]
            self._elements["text"] = ["image", {"image": self.master.font.render(self.name, True, (255,255,255)), "pos": (self.x+5, self.y+5)}]
        def update_hitbox(self):
            self._hitbox = pg.Rect(self.x, self.y, self.width, self.height)
        def update_hover(self, mouse_pos):
            if self._hitbox.collidepoint(mouse_pos):
                self.color = (35,35,35)
            else:
                self.color = (55,55,55)
            self._create_button()
            return self._hitbox.collidepoint(mouse_pos)
        def is_collide(self, mouse_pos):
            return self._hitbox.collidepoint(mouse_pos)
        def get_elements(self):
            return self._elements.copy()
class Block:
    def __init__(self, UID, type, x, y):
        self.UID = UID
        self.type = type
        self._elements = {}
        self.x = x
        self.y = y
        self.scale = 1
        self.width = DATA[type]["width"]
        self.height = DATA[type]["height"]
        self.base_color = (75,75,75)
        self.secondary_color = (125,125,125)
        self.font = pg.font.SysFont("Arial", 16)
        self._points_rect = {}
        self.old_ticks = -1
        self._create_block()
    def _add_rect(self,name,x=0,y=0,center="none",width=10,height=10,color=(0,0,0),rect_width=0,border_radius=0):
        if not center in ["none", "x", "y", "both"]: return
        new_width, new_height = width+rect_width, height+rect_width
        self._elements[name] = ["rect", color, pg.Rect(x-(new_width/2 if center in ["x", "both"] else 0), y-(new_height/2 if center in ["y", "both"] else 0), new_width, new_height), rect_width, border_radius]
    def _add_image(self, name, x=0, y=0, center="none", text="", text_color=(0,0,0)):
        image = self.font.render(text, True, text_color)
        if not center in ["none", "x", "y", "both"]: return
        width = image.get_rect().width
        height = image.get_rect().height
        center_x = x-(width/2 if center in ["x", "both"] else 0)
        center_y = y-(height/2 if center in ["y", "both"] else 0)
        self._elements[name] = ["image", {"image": image, "pos": (center_x, center_y)}]
    def _add_connection_points(self):
        self._points_rect = {}
        if DATA[self.type]["attributes"].get("Inputs") is not None and DATA[self.type]["attributes"].get("Inputs") != "inf":
            count = DATA[self.type]["attributes"]["Inputs"]
            offset_y = self.height/(count+1)
            for idx in range(DATA[self.type]["attributes"].get("Inputs")):
                y = self.y - self.height/2 + offset_y*(idx+1)
                self._elements[f"outline_circle_input_{idx}"] = ["circle",self.secondary_color,(self.x-(self.width/2),y,10)]
                self._elements[f"circle_input_{idx}"] = ["circle",self.base_color,(self.x-(self.width/2),y,5)]
                self._points_rect[f"hitbox_input_{idx}"] = pg.Rect(self.x-(self.width/2)-10,y-10,20,20)
                self._add_rect(f"input_hitbox_input_{idx}",self.x-(self.width/2)-10,y-10,20,20)
        if DATA[self.type]["attributes"].get("Outputs") is not None and DATA[self.type]["attributes"].get("Outputs") != "inf":
            count = DATA[self.type]["attributes"]["Outputs"]
            offset_y = self.height/(count+1)
            for idx in range(DATA[self.type]["attributes"].get("Outputs")):
                y = self.y - self.height/2 + offset_y*(idx+1)
                self._elements[f"outline_circle_output_{idx}"] = ["circle",self.secondary_color,(self.x+(self.width/2),y,10)]
                self._elements[f"circle_output_{idx}"] = ["circle",self.base_color,(self.x+(self.width/2),y,5)]
                self._points_rect[f"hitbox_output_{idx}"] = pg.Rect(self.x+(self.width/2)-10,y-10,20,20)
                self._add_rect(f"output_hitbox_input_{idx}",self.x+(self.width/2)-10,y-10,20,20)
    def _add_block_base(self, x=0, y=0, width=10, height=10):
        self._add_rect("base", x, y, "both", width, height, self.base_color, border_radius=10)
        self._add_rect("outline", x, y, "both", width, height, self.secondary_color, 5, 10)
    def _create_block(self):
        self._hitbox = pg.Rect(pg.Rect(self.x-self.width/2, self.y-self.height/2, self.width, self.height))
        self._add_block_base(self.x, self.y, self.width, self.height)
        self._add_connection_points()
        self._add_image("block_name", self.x, self.y-self.height/2+10, "x", self.type, (255,255,255))
    def update(self, new_base_color=None, new_secondary_color=None, tick=0):
        self._elements.clear()
        if new_base_color is not None:
            self.base_color = new_base_color
        if new_secondary_color is not None:
            self.secondary_color = new_secondary_color
        if self.old_ticks-10 < tick < self.old_ticks:
            self.base_color = (60, 180, 75)
            self.secondary_color = (120, 255, 120)
        else:
            if self.base_color == (60,180,75):
                self.base_color = (75,75,75)
                self.secondary_color = (125,125,125)
        self._create_block()
    def activate_block(self, input_index, tick, engine):
        # print(f"{self.type} | input: {input_index} | tick: {tick}")
        if self.type == "Print":
            engine.command_buffer["Print"] = (True, "Print!")
        if self.type == "End":
            engine.command_buffer["End"] = True
        self.old_ticks = tick + 10
    def is_collide_in_point(self, pos):
        return self._hitbox.collidepoint(pos)
    def get_pos(self):
        return self.x, self.y
    def get_collision_with_points(self, pos):
        for name in self._elements.keys():
            if (name.startswith("outline_circle_input_") or name.startswith("outline_circle_output_")) and self._points_rect[f"hitbox_{name[15:]}"].collidepoint(pos):
                return True, (self._points_rect[f"hitbox_{name[15:]}"].centerx,self._points_rect[f"hitbox_{name[15:]}"].centery), "input" if name.startswith("outline_circle_input_") else "output", name
        return False, (None, None)
    def _delete_element(self, name):
        del self._elements[name]
    def get_elements(self):
        return self._elements.copy()
class Line:
    def __init__(self, UID, start_x, start_y, end_x, end_y, mode, start_object=None, start_point=None, end_object=None, end_point=None):
        self.UID = UID
        self.mode = mode
        self.activated = False
        self.start_object = start_object
        self.start_point = start_point
        self.end_object = end_object
        self.end_point = end_point
        self.start_x, self.start_y = start_x, start_y
        self.end_x, self.end_y = end_x, end_y
        self.center_x, self.center_y = self._get_center_of_line()
        self.arrow_size = 20
        self._elements = {}
        self._create_objects()
    def _add_line(self, name, start_point, end_point, color, width):
        self._elements[name] = ["line", color, start_point, end_point, width]
    def _add_point(self, name, pos, color, width):
        self._elements[name] = ["point", pos, color, width]
    def _remove_line(self, name):
        del self._elements[name]
    def _create_objects(self):
        angle = math.atan2(self.center_y - self.start_y, self.center_x - self.end_x)
        color = (255,255,255)
        if self.mode == "active": color = (200,200,200)
        if self.mode == "delete": color = (255,0,0)
        self._add_line("main_line", (self.start_x, self.start_y), (self.end_x, self.end_y), color, 7 if self.mode == "active" else 5)
        self._add_line("direction_line_1", (self.center_x, self.center_y), (self.center_x+(math.cos(angle+math.radians(-45)))*self.arrow_size, self.center_y-(math.sin(angle+math.radians(-45)))*self.arrow_size), color, 9 if self.mode == "active" else 7)
        self._add_line("direction_line_2", (self.center_x, self.center_y), (self.center_x+(math.cos(angle+math.radians(45)))*self.arrow_size, self.center_y-(math.sin(angle+math.radians(45)))*self.arrow_size), color, 9 if self.mode == "active" else 7)
    def update(self, mode):
        if mode is not None: self.mode = mode
        if self.start_point is not None: self.start_x, self.start_y = self.start_object._points_rect[f"hitbox_{self.start_point}"].centerx, self.start_object._points_rect[f"hitbox_{self.start_point}"].centery
        if self.end_point is not None:self.end_x, self.end_y = self.end_object._points_rect[f"hitbox_{self.end_point}"].centerx, self.end_object._points_rect[f"hitbox_{self.end_point}"].centery
        if self.start_point is None and self.start_object is not None: self.start_x, self.start_y = self.start_object.x, self.start_object.y
        if self.end_point is None and self.end_object is not None: self.end_x, self.end_y = self.end_object.x, self.end_object.y
        self.center_x, self.center_y = self._get_center_of_line()
        self._elements.clear()
        self._create_objects()
    def is_point_on_line(self, x, y, max_dist=10):
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        length_sq = dx*dx + dy*dy
        if length_sq == 0:
            return math.hypot(x - self.start_x, y - self.start_y) <= max_dist
        t = ((x - self.start_x) * dx + (y - self.start_y) * dy) / length_sq
        t = max(0, min(1, t))
        nearest_x = self.start_x + t * dx
        nearest_y = self.start_y + t * dy
        dist = math.hypot(x - nearest_x, y - nearest_y)
        return dist <= max_dist
    def _get_center_of_line(self):
        return (lerp(self.start_x, self.end_x, 0.5), lerp(self.start_y, self.end_y, 0.5))
    def get_elements(self):
        return self._elements.copy()
class Point:
    def __init__(self, UID, pos):
        self.UID = UID
        self.x, self.y = pos
        self.color = (150,150,150)
        self.activated = False
        self.update_hitbox()
    def update_hitbox(self):
        self._hitbox = pg.Rect(self.x-15, self.y-15, 30, 30)
    def is_collide_in_point(self, pos):
        return self._hitbox.collidepoint(pos)
    def update(self):
        pass
    def get_pos(self):
        return self.x, self.y
    def get_point(self):
        return {
            "point": ["point", (self.x, self.y), self.color, 10]
        }