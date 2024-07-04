from typing import Optional
import pygame
from utils.colors import Colors
from pages.page import Page
from utils.eventbool import EventBool
from external.definitions import PlayerRole, decompress_grid
from utils.canvas import Canvas
from threading import Thread
from utils.colors import Colors
from time import sleep
import math

class Message:
    def __init__(self: any, game: any, text: str, sender: str, padding: tuple[int], color: Colors = Colors.salmon, text_color: Colors = Colors.purple, sender_color: Colors = Colors.beige, is_image: bool = False, canvas: Optional[Canvas] = None) -> None:
        self.text = text
        self.sender = sender
        self.padding = padding
        self.is_image = is_image
        self.game = game
        self.pos = [0, 0]
        self.color = color
        self.text_color = text_color
        self.sender_color = sender_color
        self.canvas = canvas
    
    def draw(self: any, pos: list[int], title_padding: float) -> None:
        sender = self.game.text_surface(self.sender, 'Arial', 15, self.sender_color)

        if self.is_image:
            dim = (self.game.dim[0] / 4, self.game.dim[0] / 4 + sender.get_height() + 2 * self.padding[1])
            self.message = pygame.Rect(pos[0], pos[1], dim[0], dim[1])
            bdrad = 10
            self.message.inflate(-2 * bdrad, -2 * bdrad)
            pygame.draw.rect(self.game.screen, self.color, self.message, border_radius=bdrad)
            self.canvas.draw((pos[0] + self.padding[0], pos[1] + sender.get_height() + 2 * self.padding[1]), (dim[0] - 2 * self.padding[0], dim[1] - 3 * self.padding[1] - sender.get_height()), Colors.white)
        else:
            text = self.game.text_surface(self.text, 'Arial', 20, self.text_color)
            dim = (max(text.get_width(), sender.get_width()) + 2 * self.padding[0], text.get_height() + sender.get_height() + 3 * self.padding[1])
            self.message = pygame.Rect(pos[0], pos[1], dim[0], dim[1])
            bdrad = 10
            self.message.inflate(-2 * bdrad, -2 * bdrad)
            pygame.draw.rect(self.game.screen, self.color, self.message, border_radius=bdrad)
            self.game.draw(text, (pos[0] + self.padding[0], pos[1] + sender.get_height() + 2 * self.padding[1]))
            
        self.game.draw(sender, (pos[0] + self.padding[0], pos[1] + self.padding[1]))
        pygame.draw.polygon(self.game.screen, self.color, [(self.message.x + title_padding * 0.5, self.message.y), (self.message.x, self.message.y + title_padding * 0.5), (self.message.x - title_padding * 0.5, self.message.y - title_padding * 0.5)])

class Chat(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self:any)->None:
        self.continue_btn_hover = EventBool(self.trigger_update)
        self.base_continue_btn_dim = (0, 0)
        self.continue_btn = None
        self.animation_done = False
        self.canvas = Canvas(self.game, self, grid_width=100, grid_height=100, readonly=True)
        self.chat_scroll = 0

    def on_start(self:any)->None:
        if self.game.client is None or self.game.client.info is None or 'lobby' not in self.game.client.info:
            if self.game.log is not None:
                self.game.log.error(f'Invalid state for chat page, client lobby info missing')
                    
            self.game.return_info = 'Ungültiger Zustand'
            self.game.goto_page('Menu')

        lobby = self.game.client.info['lobby']
        grid = lobby['grid'] if lobby['grid'] is not None else {'tiles': [[0]], 'dim': (1, 1)}
        self.canvas.grid_width = grid['dim'][0]
        self.canvas.grid_height = grid['dim'][1]
        self.canvas.grid = decompress_grid(grid['tiles'], self.canvas.grid_width) if 'compressed' in grid else grid['tiles']

        self.messages = []

        for player in sorted(lobby['players'], key=lambda x: x['role']):
            if player['role'] == PlayerRole.DRAWER.name:
                self.messages.append(Message(self.game, '', player['name'], (10, 10), is_image=True, canvas=self.canvas))
            else:
                self.messages.append(Message(self.game, player['guess'], player['name'], (10, 5)))

        self.messages.append(Message(self.game, lobby['word'], 'KI', (10, 5), color=Colors.pink))
        
        self.animation_thread = Thread(target=self.animation)
        self.animation_thread.start()

    def linear(self: any, x: float) -> float:
        return x
    
    def regression(self: any, x: float) -> float:
        slope = 8
        return 1 - 1 / (1 + slope * x)

    def logistic(self: any, x: float) -> float:
        slope = 8
        return 1 / (1 + math.e ** (-slope * (x - 0.5)))

    def animation(self: any) -> None:
        padding = self.game.dim[1] / 15

        for message in self.messages:
            message.pos = [-self.game.dim[0] / 3, self.game.dim[1] + 200]
        
        y = 0

        for message in self.messages:
            self.animate(message.pos, (0, y), 25, 50, self.regression, self.logistic, 1)
            message.draw((0, y), 0)
            y = message.message.y + message.message.height + padding
        
        sleep(2)

        self.animation_done = True
    
    def animate(self: any, pos: list[float], end: tuple[float], x_steps: int, y_steps: int, x_func: callable, y_func: callable, time: float) -> None:
        start = tuple(pos)
        steps = max(x_steps, y_steps)
        # TODO: dynamic animation speed, adapt chat scroll height

        for i in range(steps):
            x = start[0] + (end[0] - start[0]) * x_func(min(i, x_steps) / x_steps)
            y = start[1] + (end[1] - start[1]) * y_func(min(i, y_steps) / y_steps)
            pos[0] = x
            pos[1] = y
            self.trigger_update()
            sleep(time / steps)
        
    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i] for i, val in enumerate(self.game.dim)])
        title_fs = 50 * min_ratio
        
        title_padding = 20 * min_ratio
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] - title.get_width() - title_padding
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg * min_ratio * 2), (title_x, title_padding + 4 * min_ratio))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title * min_ratio * 2), (title_x, title_padding))
    
        for i, message in enumerate(self.messages):
            message.draw((title_padding + message.pos[0], title_padding + message.pos[1] + self.chat_scroll), title_padding)
        
        if self.animation_done:
            self.base_continue_btn_dim = (200 * min_ratio, 100 * min_ratio)

            if not hasattr(self, 'continue_btn_dim'):
                self.continue_btn_dim = self.base_continue_btn_dim

            self.continue_btn = self.game.create_btn((self.game.dim[0] - title_padding - self.continue_btn_dim[0], self.game.dim[1] - title_padding - self.continue_btn_dim[1]), self.continue_btn_dim, Colors.purple, int(20 * min_ratio), 'Weiter >', 'Arial', 30 * min_ratio, Colors.beige)

    def iteration(self:any)->None:     
        if self.continue_btn is not None and self.continue_btn.collidepoint(self.mouse_pos):
            if self.continue_btn_hover.switch_true():
                self.continue_btn_dim = tuple([val * 1.05 for val in self.base_continue_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.continue_btn_hover.switch_false():
            if self.continue_btn is not None:
                self.continue_btn_dim = self.base_continue_btn_dim
            
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        self.canvas.iteration()
                         
    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.continue_btn is not None and self.continue_btn_hover.state:
                if self.animation_thread.is_alive():
                    self.animation_thread.join()
                
                self.game.goto_page('Result')
        
        if self.animation_done:
            if event.type == pygame.MOUSEWHEEL:
                self.chat_scroll += event.y * 5
                self.chat_scroll = min(0, self.chat_scroll)
                self.trigger_update()
        
        if event.type == pygame.VIDEORESIZE and self.continue_btn is not None:
            self.continue_btn_hover.switch_true()
        
        self.canvas.event_check(event)
