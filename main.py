import pygame as pg
import os, sys, random, string
roaming_path = os.path.join(os.environ["APPDATA"], "BlockScript")
sys.path.append(roaming_path)
# from entities import Block, Line, Point, Menu, Cursor, DATA
# from screen import Screen
from BlockScript.screen import Screen
from BlockScript.entities import Block, Line, Point, Menu, Cursor, DATA

screen = Screen(1600, 800)
cursor = Cursor()

class ExecutionEngine:
    def __init__(self):
        self.queue = []          # поточні сигнали
        self.next_queue = []     # сигнали наступного тіку
        self.running = False
        self.speed = 1           # скільки тіків за кадр
        self.paused = False
        self.REGISTER = []
        self.command_buffer = {
            "End": False,
            "Print": (False, "")
        }
        self.priority_command_buffer = [[],[]]
        self.visited_this_tick = set()
    def start(self, start_uid):
        self.queue.clear()
        self.next_queue.clear()
        self.REGISTER.clear()
        self.visited_this_tick = set()
        self.queue.append((start_uid, None))
        self.running = True
        self.paused = False
        print("Code was start")
    def stop(self, exit_code=0):
        global editor_mode, old_editor_mode
        self.running = False
        self.queue.clear()
        self.next_queue.clear()
        self.REGISTER.clear()
        print(f"Code was stop | exit code: {exit_code}\n\n\n\n\n")
        if type(MODES[old_editor_mode]) == list:
            editor_mode = f"{MODES[old_editor_mode][0]}{MODES[old_editor_mode][1]}"
        else:
            editor_mode = MODES[old_editor_mode]
        MODES["curr"] = old_editor_mode
        old_editor_mode = None
    def add_signal(self, uid, input_index):
        self.next_queue.append((uid, input_index))
    def step(self, tick):
        if not self.running or self.paused:
            return
        for _ in range(self.speed):
            self.visited_this_tick = set()
            if not self.queue:
                self.queue, self.next_queue = self.next_queue, []
                if not self.queue:
                    self.stop()
                    return
            current_batch = self.queue.copy()
            self.queue.clear()
            for uid, input_index in current_batch:
                self.process(uid, input_index, tick)
            for block_name, value in self.command_buffer.items():
                if not engine.running: break
                if block_name == "End" and value:
                    self.priority_command_buffer[1].append(value)
                if block_name == "Print" and value[0]:
                    self.priority_command_buffer[0].append(value)
            for idx, block_value in enumerate(self.priority_command_buffer):
                for value in block_value:
                    if not engine.running: break
                    if idx == 1 and value:
                        engine.stop(1)
                    elif idx == 0 and value[0]:
                        print(value[1])
            self.command_buffer = {
                "End": False,
                "Print": (False, "")
            }
            self.priority_command_buffer = [[],[]]
    def process(self, source_uid, input_index, tick):
        state = (source_uid, input_index)
        if state in self.visited_this_tick:
            return
        self.visited_this_tick.add(state)
        next_targets = get_next_targets(source_uid)
        for target_uid, line in next_targets:
            if target_uid in POINT_LIST:
                self.add_signal(target_uid, None)
            elif target_uid in BLOCK_LIST:
                block = BLOCK_LIST[target_uid]
                new_input = None
                if line["line"].end_object == block:
                    new_input = int(line["line"].end_point[-1:])
                block.activate_block(new_input, tick, self)
                self.add_signal(target_uid, new_input)

def generate_UID(length=8):
    chars = string.ascii_letters + string.digits
    while True:
        new_uid = ''.join(random.choice(chars) for _ in range(length))
        if not (new_uid in LINE_LIST or new_uid in BLOCK_LIST or new_uid in POINT_LIST):
            return new_uid
def clamp(val, min_val, max_val):
    return min(max_val, max(val, min_val))
def get_next_targets(source_uid):
    targets = []
    for line in LINE_LIST.values():
        if line["sources"][0] == source_uid:
            targets.append((line["sources"][1], line))
    return targets
def remove_matches_for(a):
    global LINE_LIST
    sa = a.get("sources", [])
    if len(sa) != 2:
        return False
    new_LINE_LIST = {}
    for key, b in LINE_LIST.items():
        if b is a or not (
            sa[0] in b.get("sources", []) and
            sa[1] in b.get("sources", [])
        ):
            new_LINE_LIST[key] = b
    if new_LINE_LIST != LINE_LIST:
        LINE_LIST = new_LINE_LIST
        return True
    return False
def line_wiring(mx, my):
    global curr_line, is_line_wiring, old_source, block_point_pos
    keys = screen.get_keys()
    line_mode = "active" if is_line_wiring else "unactive"
    for block in BLOCK_LIST.values():
        point_result = block.get_collision_with_points((mx, my))
        if point_result[0]:
            if not is_line_wiring and DATA[block.type]["attributes"].get("Outputs") is not None and point_result[2] == "output":
                block_point_pos = point_result[1]
                is_line_wiring = True
                curr_line = None
                old_source = block
                line_mode = "active"
                curr_line = Line(generate_UID(), block_point_pos[0], block_point_pos[1], mx, my, line_mode, old_source, point_result[3][15:])
                return
            else:
                if curr_line is not None and DATA[block.type]["attributes"].get("Inputs") is not None and point_result[2] == "input":
                    if block == old_source: continue
                    block_point_pos = point_result[1]
                    curr_line.end_x, curr_line.end_y = block_point_pos
                    line_mode = "unactive"
                    curr_line.end_object = block
                    curr_line.end_point = point_result[3][15:]
                    curr_line.update(line_mode)
                    new_line = {"type": "block", "sources": [old_source.UID, block.UID], "line": curr_line}
                    LINE_LIST[curr_line.UID] = new_line
                    if remove_matches_for(new_line):
                        curr_line = None
                        old_source = None
                        is_line_wiring = False
                        return
                if curr_line is not None and curr_line.end_object is not None:
                    curr_line = None
                    old_source = None
                    is_line_wiring = False
                return
    for point in POINT_LIST.values():
        if point.is_collide_in_point((mx, my)):
            print("Point was click")
            if not is_line_wiring:
                for line in LINE_LIST.values():
                    if point.UID in line["sources"]:
                        is_line_wiring = True
                        curr_line = None
                        old_source = point
                        line_mode = "active"
                        curr_line = Line(generate_UID(), point.x, point.y, mx, my, line_mode, old_source)
            else:
                if curr_line is not None:
                    curr_line.end_x, curr_line.end_y = point.x, point.y
                    line_mode = "unactive"
                    curr_line.end_object = point
                    curr_line.update(line_mode)
                    new_line = {"type": "point", "sources": [old_source.UID, point.UID], "line": curr_line}
                    LINE_LIST[curr_line.UID] = new_line
                    if remove_matches_for(new_line):
                        curr_line = None
                        old_source = None
                        is_line_wiring = False
                        return
                if curr_line is not None and curr_line.end_object is not None:
                    if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
                        old_source = point
                        curr_line = Line(generate_UID(), point.x, point.y, mx, my, line_mode, old_source)
                        is_line_wiring = True
                    else:
                        old_source = None
                        curr_line = None
                        is_line_wiring = False
def add_block_to_world(type, x, y, grid_rel=False, return_UID=False):
    new_UID = generate_UID()
    BLOCK_LIST[new_UID] = Block(new_UID, type, x*(100 if grid_rel else 1), y*(100 if grid_rel else 1))
    if return_UID: return new_UID
def mode_process():
    global is_line_wiring, curr_line, editor_mode, rel_x, rel_y, target, block_menu, menu_open, block_menu_type, submenu_open, block_submenu
    mx, my = screen.get_mouse_pos()
    press = screen.get_mouse_press()
    grid = 100



    if editor_mode == "Drag":
        if rel_x is None or rel_y is None or target is None:
            for block in BLOCK_LIST.values():
                if block.is_collide_in_point((mx, my)):
                        block.update((91,69,60),(255,127,39))
                        if press[0]:
                            rel_x, rel_y = block.x-mx, block.y-my
                            target = block
                else:
                    block.update((75,75,75),(125,125,125))
            for point in POINT_LIST.values():
                if point.is_collide_in_point((mx, my)):
                    point.color = (255,127,39)
                    if press[0]:
                        rel_x, rel_y = point.x-mx, point.y-my
                        target = point
                else:
                    point.color = (150,150,150)
        else:
            target.x, target.y = rel_x+mx, rel_y+my
            world_x, world_y = target.x, target.y
            target.update()
            if not press[0]:
                if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
                    world_x, world_y = target.x, target.y
                    target.x = round(world_x/grid)*grid
                    target.y = round(world_y/grid)*grid
                    target.update()
                    target = None
                    rel_x, rel_y = None, None
                else:
                    target = None
                    rel_x, rel_y = None, None
        if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
            cursor.set_cursor_addiction("drag_snap")
        else:
            cursor.set_cursor_addiction()
    else:
        target = None
        rel_x, rel_y = None, None
        for block in BLOCK_LIST.values():
            if block.secondary_color == (255,127,39):
                block.update((75,75,75),(125,125,125))
        for point in POINT_LIST.values():
            if point.color == (255,127,39):
                point.color = (150,150,150)



    if editor_mode == "LineBuild":
        if curr_line is not None:
            curr_line.end_x, curr_line.end_y = mx,my
            curr_line.update("active")
            screen.add_to_editor_buffer(curr_line.get_elements())
    else:
        curr_line = None
        is_line_wiring = False



    if editor_mode == "LineDelete":
        line_buffer = []
        for point in POINT_LIST.copy().values():
            if point.is_collide_in_point((mx, my)):
                for line_dict in LINE_LIST.copy().values():
                    if point.UID in line_dict["sources"] and line_dict not in line_buffer:
                        line_buffer.append(line_dict)
                point.color = (200,0,0)
                for line in line_buffer:
                    line["line"].update("delete")
                if press[0]:
                    for line in line_buffer:
                        del LINE_LIST[line["line"].UID]
                    line_buffer.clear()
                    del POINT_LIST[point.UID]
                return
            else:
                point.color = (150,150,150)
        for key, line_dict in LINE_LIST.copy().items():
            line = line_dict["line"]
            if line.is_point_on_line(mx, my):
                line.update("delete")
                if press[0]:
                    del LINE_LIST[key]
                    continue
            else:
                line.update("unactive")
    else:
        for line in LINE_LIST.values():
            if line["line"].mode == "delete":
                line["line"].update("unactive")
        for point in POINT_LIST.values():
            if point.color == (200,0,0):
                point.color = (150,150,150)



    if editor_mode == "BlockBuild":
        for block in BLOCK_LIST.values():
            if block.is_collide_in_point((mx, my)):
                block.update((60,91,62),(0,151,12))
                if press[2] and not menu_open:
                    menu_open = True
                    block_menu = Menu("block", mx, my)
                    block_menu_type = "block"
        if press[0] and menu_open:
            if not block_menu.is_collide_in_point((mx, my)):
                if submenu_open:
                    if not block_submenu.is_collide_in_point((mx, my)):
                        submenu_open = False
                        block_submenu = None
                        menu_open = False
                        block_menu = None
                        block_menu_type = None
                else:
                    menu_open = False
                    block_menu = None
                    block_menu_type = None
        if menu_open: return
        for block in BLOCK_LIST.values():
            if not block.is_collide_in_point((mx,my)):
                block.update((75,75,75),(125,125,125))
                if press[2] and not menu_open:
                    menu_open = True
                    block_menu = Menu("regular", mx, my)
                    block_menu_type = "regular"
    else:
        menu_open = False
        block_menu = None
        submenu_open = False
        block_submenu = None
        for block in BLOCK_LIST.values():
            if block.secondary_color == (0,151,12):
                block.update((75,75,75),(125,125,125))



    if editor_mode == "BlockDelete":
        for UID, block in BLOCK_LIST.copy().items():
            if block.is_collide_in_point((mx, my)):
                block.update((107,44,44),(200,0,0))
                if press[0] and block.type != "Start":
                    del BLOCK_LIST[UID]
            else:
                block.update((75,75,75),(125,125,125))
    else:
        for block in BLOCK_LIST.values():
            if block.secondary_color == (200,0,0):
                block.update((75,75,75),(125,125,125))
def process_menu_buttons():
    global block_menu, menu_open, block_submenu, submenu_open
    if block_menu and menu_open:
        block_menu.update_buttons_hover((mx,my), cursor)
        if press[0]:
            if block_menu_type == "regular":
                clicked_btn = block_menu.check_buttons_click((mx, my))
                if clicked_btn is not None:
                    if clicked_btn[0] == "create_btn" and not submenu_open:
                        submenu_open = True
                        block_submenu = Menu("sub_create", block_menu.x+100, block_menu.y+5)
            if block_menu_type == "block":
                clicked_btn = block_menu.check_buttons_click((mx, my))
                if clicked_btn is not None:
                    if clicked_btn[0] == "open_parameters_btn":
                        print("Sorry, I don't have time for another window")
        for diction in LINE_LIST.values():
            for key, value in diction.items():
                if key == "line" and value is not None:
                    value.update(None)
                    screen.add_to_editor_buffer(value.get_elements())
    if block_submenu and submenu_open:
        block_submenu.update_buttons_hover((mx,my), cursor)
        if press[0]:
            clicked_btn = block_submenu.check_buttons_click((mx,my))
            if clicked_btn is not None:
                add_block_to_world(clicked_btn[1], block_menu.x, block_menu.y)
                cursor.cursor_mode = "arrow"
                block_menu = None
                menu_open = False
                block_submenu = None
                submenu_open = False

LINE_LIST = {}
BLOCK_LIST = {}
POINT_LIST = {}

MODES = {
    "curr": pg.K_1,
    pg.K_1: "View",
    pg.K_2: "Drag",
    pg.K_3: ["Line", "Build"],
    pg.K_4: ["Block", "Build"]
}
CAMERA_SPEED = 25

block_point_pos = None
block_submenu = None
block_menu = None
block_menu_type = None
submenu_open = False
menu_open = False
rel_x, rel_y = None, None
target = None
curr_line = None
old_source = None
is_line_wiring = False
running_index = 0
old_editor_mode = "View"
editor_mode = "View"

# MODES: | ALL DONE
# | View - You cannot build or delete, just watch | DONE
# | Drag - You can drag blocks and points | DONE
# | LineBuild - You can create lines and points | DONE
# | BlockBuild - You can build blocks and set up | DONE
# | LineDelete - You can delete lines and points | DONE
# | BlockDelete - You can delete blocks | DONE
#
# Run - Put you to View mode; | DONE
# Stop - Put you to old mode; | DONE

engine = ExecutionEngine()
start_UID = add_block_to_world("Start", 0, 0, False, True)

running = True
tick = 0
while running:
    dt = screen.CLOCK.tick(screen.FPS)/1000
    tick += 1
    press = screen.get_mouse_press()
    mx, my = screen.get_mouse_pos()
    events = screen.get_events()
    for event in events:
        if event.type == pg.QUIT: running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not engine.running:
                if editor_mode == "LineBuild": line_wiring(mx, my)
            if event.button == 3 and is_line_wiring and not engine.running:
                old_source = None
                curr_line = None
                is_line_wiring = False
        if event.type == pg.KEYDOWN:
            if engine.running:
                if event.key in [pg.K_SPACE, pg.K_F8]:
                    engine.paused = not engine.paused
                # if event.key == pg.K_UP:
                    # engine.speed += min(50, engine.speed + 1)
                # if event.key == pg.K_DOWN:
                    # engine.speed = max(1, engine.speed - 1)
                # if event.key == pg.K_RIGHT and engine.paused:
                    # engine.step(tick)
            if event.key == pg.K_p and editor_mode == "LineBuild" and not engine.running:
                new_UID = generate_UID()
                POINT_LIST[new_UID] = Point(new_UID, (mx, my))
                if is_line_wiring:
                    line_wiring(mx,my)
            if event.key == pg.K_h and editor_mode == "View":
                screen.X, screen.Y = 0-(screen.WIDTH/2), 0-(screen.HEIGHT/2)
                screen.SCALE = 1.0
            if event.key == pg.K_F9:
                if not engine.running:
                    running_index += 1
                    print(f"\n\n\n\n\n#{running_index}")
                    old_editor_mode = MODES["curr"]
                    editor_mode = MODES[pg.K_1]
                    MODES["curr"] = pg.K_1
                    engine.running = True
                    engine.start(start_UID)
                else:
                    engine.stop()
            if event.key in [pg.K_q, pg.K_e] and not engine.running:
                if type(MODES[MODES["curr"]]) == list:
                    if event.key == pg.K_q:
                        MODES[MODES["curr"]][1] = "Build"
                    else:
                        MODES[MODES["curr"]][1] = "Delete"
                    editor_mode = f"{MODES[MODES["curr"]][0]}{MODES[MODES["curr"]][1]}"
        if event.type == pg.MOUSEWHEEL:
            mx, my = screen.get_mouse_pos(False)
            world_x_before = mx / screen.SCALE + screen.X
            world_y_before = my / screen.SCALE + screen.Y
            zoom = 1.1 if event.y > 0 else 1 / 1.1
            screen.SCALE *= zoom
            screen.SCALE = clamp(round(screen.SCALE, 1), 0.5, 5)
            world_x_after = mx / screen.SCALE + screen.X
            world_y_after = my / screen.SCALE + screen.Y
            screen.X += (world_x_before - world_x_after)
            screen.Y += (world_y_before - world_y_after)
    keys = screen.get_keys()
    screen.Y+=(int(keys[pg.K_s])-int(keys[pg.K_w]))*CAMERA_SPEED*(0.25 if keys[pg.K_LSHIFT]and editor_mode=="View"else 1)*(4 if keys[pg.K_LCTRL]and editor_mode=="View"else 1)*50*dt
    screen.X+=(int(keys[pg.K_d])-int(keys[pg.K_a]))*CAMERA_SPEED*(0.25 if keys[pg.K_LSHIFT]and editor_mode=="View"else 1)*(4 if keys[pg.K_LCTRL]and editor_mode=="View"else 1)*50*dt
    if engine.running:
        engine.step(tick)
    keys = screen.get_keys()
    for key in [pg.K_1, pg.K_2, pg.K_3, pg.K_4]:
        if keys[key] and not engine.running:
            if type(MODES[key]) == list:
                editor_mode = f"{MODES[key][0]}{MODES[key][1]}"
            else:
                editor_mode = MODES[key]
            MODES["curr"] = key
    mode_process()
    process_menu_buttons()
    for diction in LINE_LIST.values():
        for key, value in diction.items():
            if key == "line" and value is not None:
                value.update(None)
                screen.add_to_editor_buffer(value.get_elements())
    for point in POINT_LIST.values():
        point.update_hitbox()
        screen.add_to_editor_buffer(point.get_point())
    for block in BLOCK_LIST.values():
        block.update(None, None, tick)
        screen.add_to_editor_buffer(block.get_elements())
    if block_menu is not None and menu_open: screen.add_to_editor_buffer(block_menu.get_elements())
    if block_submenu is not None and submenu_open: screen.add_to_editor_buffer(block_submenu.get_elements())
    screen.screen.fill(screen.BG)
    if not keys[pg.K_RIGHTBRACKET]: screen.draw_grid()
    screen.draw_editor()
    screen.draw_ui(dt, tick)
    cursor.cursor_name = editor_mode
    cursor.cursor_name_mode = None
    if cursor.cursor_name[:4] == "Line": cursor.cursor_name = "Line"
    if cursor.cursor_name[:5] == "Block": cursor.cursor_name = "Block"
    if editor_mode.endswith("Build"): cursor.cursor_name_mode = "Build"
    if editor_mode.endswith("Delete"): cursor.cursor_name_mode = "Delete"
    cursor.draw(screen)
    screen.update()