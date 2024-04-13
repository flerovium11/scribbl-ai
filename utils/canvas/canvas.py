import math
from utils.colors import Colors
import pygame

class Canvas:
    def __init__(self:any, game:any, page:any)->None:
        self.game = game
        self.page = page
        self.mode = 'draw'
        self.pencil_img = pygame.image.load('./assets/pencil.png').convert_alpha()
        self.eraser_img = pygame.image.load('./assets/eraser.png').convert_alpha()
        self.trash_img = pygame.image.load('./assets/trash.png').convert_alpha()
        self.phover = self.ehover = self.thover = self.drawing = False
        self.grid_width = 200
        self.grid_height = 200
        self.grid = self.empty_grid(self.grid_width, self.grid_height)
        self.draw_radius = 4
        self.erase_radius = 8
    
    def empty_grid(self:any, w:int, h:int):
        return [[0.0 for _ in range(h)] for _ in range(w)]

    def draw_circle(self:any, center:tuple[float], radius:float, erase:bool=False, fade_factor:float=1)->None:
        center_x, center_y = center

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
        pencil_size = (icon_size * (1 + self.phover / 10), icon_size * (1 + self.phover / 10))
        eraser_size = (icon_size * (1 + self.ehover / 10), icon_size * (1 + self.ehover / 10))
        trash_size = (icon_size * (1 + self.thover / 10), icon_size * (1 + self.thover / 10))

        self.pencil_rect = pygame.Rect(pencil_pos, pencil_size)
        self.eraser_rect = pygame.Rect(eraser_pos, eraser_size)
        self.trash_rect = pygame.Rect(trash_pos, trash_size)

        self.game.draw(pygame.transform.smoothscale(self.pencil_img, pencil_size), pencil_pos)
        self.game.draw(pygame.transform.smoothscale(self.eraser_img, eraser_size), eraser_pos)
        self.game.draw(pygame.transform.smoothscale(self.trash_img, trash_size), trash_pos)
        
        self.draw_trace()

        if self.page.mouseswitch and hasattr(self.page, 'mouse_pos'):
            img = self.pencil_img if self.mode == 'draw' else self.eraser_img
            self.game.draw(pygame.transform.smoothscale(img, tuple([val / 1.5 for val in pencil_size])), (self.page.mouse_pos[0], self.page.mouse_pos[1] - pencil_size[1] / 2 - 5))

    def normalize_pos(self:any, pos:tuple[float])->tuple[float]:
        pos_x = math.floor((pos[0] - self.canvas.x) / self.canvas.width * self.grid_width)
        pos_y = math.floor((pos[1] - self.canvas.y) / self.canvas.height * self.grid_height)
        return (pos_x, pos_y)

    def coords(self:any, x:int, y:float)->tuple[int]:
        return (min(self.grid_width - 1, max(0, x)), min(self.grid_height - 1, max(0, y)))

    def event_check(self:any, event:pygame.event)->None: 
        self.phover = self.ehover = self.thover = False

        if self.canvas.collidepoint(self.page.mouse_pos):
            self.page.mouseswitch = True
            pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.drawing = True
                    normalized = self.normalize_pos(event.pos)
                    radius = self.draw_radius if self.mode == 'draw' else self.erase_radius
                    self.draw_circle((normalized[0], normalized[1]), radius, self.mode != 'draw', 0.1)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing = False
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    normalized = self.normalize_pos(event.pos)
                    radius = self.draw_radius if self.mode == 'draw' else self.erase_radius
                    self.draw_circle((normalized[0], normalized[1]), radius, self.mode != 'draw', 0.1)
            
        elif event.type == pygame.MOUSEMOTION:
            self.page.mouseswitch = False

        if self.pencil_rect.collidepoint(self.page.mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.phover = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mode = 'draw'

        if self.eraser_rect.collidepoint(self.page.mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.ehover = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mode = 'erase'

        if self.trash_rect.collidepoint(self.page.mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.thover = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.grid = self.empty_grid(self.grid_width, self.grid_height)
        
    def draw_trace(self:any)->None:
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.grid[x][y] > 0:
                    rect = pygame.Rect(self.canvas.x + x / self.grid_width * self.canvas.width, self.canvas.y + y / self.grid_height * self.canvas.height, math.ceil(self.canvas.width / self.grid_width), math.ceil(self.canvas.height / self.grid_height)) # * 1.2 weil sonst komische abstände entstehen
                    brightness = int(255 - self.grid[x][y] * 255)
                    pygame.draw.rect(self.game.screen, pygame.Color(brightness, brightness, brightness), rect)
