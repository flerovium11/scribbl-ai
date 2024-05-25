import math
from utils.colors import Colors
from utils.eventbool import EventBool
import pygame

class Canvas:
    def __init__(self:any, game:any, page:any)->None:
        self.game = game
        self.page = page
        self.mode = 'draw'
        self.pencil_img = pygame.image.load('./assets/pencil.png').convert_alpha()
        self.eraser_img = pygame.image.load('./assets/eraser.png').convert_alpha()
        self.trash_img = pygame.image.load('./assets/trash.png').convert_alpha()
        self.drawing = self.ai_predict = False
        self.grid_width = 200
        self.grid_height = 200
        self.grid = self.empty_grid(self.grid_width, self.grid_height)
        self.draw_radius_proportion = 0.03
        self.draw_radius = round(self.grid_width * self.draw_radius_proportion)
        self.max_draw_radius = self.draw_radius * 10
        self.min_draw_radius = 0
        self.erase_radius = self.draw_radius * 3
        self.max_erase_radius = self.erase_radius * 5
        self.min_erase_radius = 1
        self.scrolled_time = 0
        self.hover = EventBool(self.page.trigger_update)
        self.thover = EventBool(self.page.trigger_update)
        self.phover = EventBool(self.page.trigger_update)
        self.ehover = EventBool(self.page.trigger_update)
    
    def empty_grid(self:any, w:int, h:int):
        return [[0.0 for _ in range(h)] for _ in range(w)]

    def draw_circle(self:any, center:tuple[float], radius:float, erase:bool=False, fade_factor:float=1)->None:
        center_x, center_y = self.coords(*center)

        if radius < 1:
            self.grid[center_x][center_y] = 1
            return None
        
        min_x = max(center_x - radius, 0)
        max_x = min(center_x + radius, len(self.grid) - 1)
        min_y = max(center_y - radius, 0)
        max_y = min(center_y + radius, len(self.grid[0]) - 1)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance <= radius:
                    if erase:
                        self.grid[x][y] = 0
                    else:
                        darkness = 1 - (distance / radius) * fade_factor  # Calculate darkness based on distance
                        self.grid[x][y] = max(self.grid[x][y], darkness)
    
    def draw(self:any, pos:tuple[float], dim:tuple[float], color:Colors)->None:
        self.canvas = pygame.Rect(pos[0], pos[1], dim[0], dim[1] * 0.875)
        bdrad = 10
        self.canvas.inflate(-2 * bdrad, -2 * bdrad)
        pygame.draw.rect(self.game.screen, color, self.canvas, border_radius=bdrad)
        icon_size = dim[1] * 0.075

        pencil_pos = (pos[0], pos[1] + dim[1] * 0.9)
        eraser_pos = (pos[0] + 2 * icon_size, pos[1] + dim[1] * 0.9)
        trash_pos = (pos[0] + 4 * icon_size, pos[1] + dim[1] * 0.9)
        self.pencil_size = (icon_size * (1 + self.phover.state / 10), icon_size * (1 + self.phover.state / 10))
        eraser_size = (icon_size * (1 + self.ehover.state / 10), icon_size * (1 + self.ehover.state / 10))
        trash_size = (icon_size * (1 + self.thover.state / 10), icon_size * (1 + self.thover.state / 10))

        self.pencil_rect = pygame.Rect(pencil_pos, self.pencil_size)
        self.eraser_rect = pygame.Rect(eraser_pos, eraser_size)
        self.trash_rect = pygame.Rect(trash_pos, trash_size)

        self.game.draw(pygame.transform.smoothscale(self.pencil_img, self.pencil_size), pencil_pos)
        self.game.draw(pygame.transform.smoothscale(self.eraser_img, eraser_size), eraser_pos)
        self.game.draw(pygame.transform.smoothscale(self.trash_img, trash_size), trash_pos)
        
        self.draw_trace()

        if self.hover.state and hasattr(self.page, 'mouse_pos'):
            img = self.pencil_img if self.mode == 'draw' else self.eraser_img
            self.game.draw(pygame.transform.smoothscale(img, tuple([val / 1.5 for val in self.pencil_size])), (self.page.mouse_pos[0], self.page.mouse_pos[1] - self.pencil_size[1] / 2 - 5))
        
        if pygame.time.get_ticks() - self.scrolled_time <= 1000 and hasattr(self.page, 'mouse_pos'):
            pygame.draw.circle(self.game.screen, Colors.pink, self.page.mouse_pos, (self.draw_radius if self.mode == 'draw' else self.erase_radius) * self.canvas.width / self.grid_width + 2, width=1)

    def normalize_pos(self:any, pos:tuple[float])->tuple[float]:
        pos_x = math.floor((pos[0] - self.canvas.x) / self.canvas.width * self.grid_width)
        pos_y = math.floor((pos[1] - self.canvas.y) / self.canvas.height * self.grid_height)
        return (pos_x, pos_y)

    def coords(self:any, x:int, y:float)->tuple[int]:
        return (min(self.grid_width - 1, max(0, x)), min(self.grid_height - 1, max(0, y)))
    
    def iteration(self:any)->None:
        if self.canvas.collidepoint(self.page.mouse_pos):
            if self.hover.switch_true():
                pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

                if pygame.mouse.get_pressed()[0]:
                    self.start_drawing()
        elif self.hover.switch_false():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        if self.pencil_rect.collidepoint(self.page.mouse_pos):
            if self.phover.switch_true():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.phover.switch_false():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.eraser_rect.collidepoint(self.page.mouse_pos):
            if self.ehover.switch_true():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.ehover.switch_false():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.trash_rect.collidepoint(self.page.mouse_pos):
            if self.thover.switch_true():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.thover.switch_false():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def event_check(self:any, event:pygame.event)->None: 
        if self.phover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.mode = 'draw'
            self.scrolled_time = pygame.time.get_ticks()
        
        if self.ehover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.mode = 'erase'
            self.scrolled_time = pygame.time.get_ticks()
        
        if self.thover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.grid = self.empty_grid(self.grid_width, self.grid_height)
            self.ai_predict = True
            self.page.trigger_update()
        
        if event.type == pygame.MOUSEWHEEL:
            if self.mode == 'draw':
                self.draw_radius = min(self.max_draw_radius, max(self.min_draw_radius, self.draw_radius + event.y))
            
            if self.mode == 'erase':
                self.erase_radius = min(self.max_erase_radius, max(self.min_erase_radius, self.erase_radius + event.y))
            
            self.scrolled_time = pygame.time.get_ticks()
            self.page.trigger_update()

        if self.hover.state:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.start_drawing()
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.drawing:
                    self.stop_drawing()
            
            elif event.type == pygame.MOUSEMOTION:
                self.page.trigger_update()

                if self.drawing:
                    normalized = self.normalize_pos(event.pos)
                    radius = self.draw_radius if self.mode == 'draw' else self.erase_radius
                    dist_x, dist_y = normalized[0] - self.last_pos[0], normalized[1] - self.last_pos[1]
                    distance = math.sqrt(dist_x**2 + dist_y**2)
                    max_interpolating_distance = max(1, round(radius / 2))
                    cuts = math.floor(distance / max_interpolating_distance)

                    for d in range(1, cuts):
                        perc = d / cuts
                        pos = self.coords(self.last_pos[0] + round(dist_x * perc), self.last_pos[1] + round(dist_y * perc))
                        self.draw_circle(pos, radius, self.mode != 'draw', 0.1)

                    self.draw_circle((normalized[0], normalized[1]), radius, self.mode != 'draw', 0.1)
                    self.last_pos = normalized
        elif self.drawing:
            self.stop_drawing()
        
    def draw_trace(self:any)->None:
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.grid[x][y] > 0:
                    rect = pygame.Rect(self.canvas.x + x / self.grid_width * self.canvas.width, self.canvas.y + y / self.grid_height * self.canvas.height, math.ceil(self.canvas.width / self.grid_width), math.ceil(self.canvas.height / self.grid_height)) # * 1.2 weil sonst komische abstände entstehen
                    brightness = int(255 - self.grid[x][y] * 255)
                    pygame.draw.rect(self.game.screen, pygame.Color(brightness, brightness, brightness), rect)

    def start_drawing(self:any)->None:
        self.drawing = True
        normalized = self.normalize_pos(self.page.mouse_pos)
        radius = self.draw_radius if self.mode == 'draw' else self.erase_radius
        self.draw_circle((normalized[0], normalized[1]), radius, self.mode != 'draw', 0.1)
        self.last_pos = normalized

    def stop_drawing(self:any)->None:
        self.drawing = False
        self.ai_predict = True
