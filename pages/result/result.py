import pygame
from utils.colors import Colors
import os
from pages.page import Page
from utils.eventbool import EventBool
from external.definitions import decompress_grid
from definitions import ROOT_DIR
from scipy.ndimage import gaussian_filter
import numpy as np
from utils.canvas import Canvas

class Result(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self:any)->None:
        self.canvas = Canvas(self.game, self, True)
        self.win_img = pygame.image.load(os.path.join(ROOT_DIR, 'assets/wrecked_robot.png')).convert_alpha()
        self.lose_img = pygame.image.load(os.path.join(ROOT_DIR, 'assets/logo.png')).convert_alpha()
        self.again_btn_hover = EventBool(self.trigger_update)
        self.back_btn_hover = EventBool(self.trigger_update)

    def on_start(self:any)->None:
        if self.game.client is None or self.game.client.info is None or 'lobby' not in self.game.client.info:
            if self.game.log is not None:
                self.game.log.error(f'Invalid state for result page, client lobby info missing')
                    
            self.game.return_info = 'Ungültiger Zustand'
            self.game.goto_page('Menu')

        self.lobby = self.game.client.info['lobby']
        grid = self.lobby['grid'] if self.lobby['grid'] is not None else {'tiles': [[0]], 'dim': (1, 1)}
        self.canvas.grid_width = grid['dim'][0]
        self.canvas.grid_height = grid['dim'][1]
        self.canvas.grid = decompress_grid(grid['tiles'], self.canvas.grid_width) if 'compressed' in grid else grid['tiles']
        self.canvas.grid = gaussian_filter(np.array(self.canvas.grid), sigma=2)
        self.img = self.lose_img if self.lobby['winner'] == 'ai' else self.win_img
        self.text = 'KI gewinnt!' if self.lobby['winner'] == 'ai' else 'Menschen gewinnen!' if self.lobby['winner'] == 'humans' else 'Niemand gewinnt!'

    def draw(self:any)->None:
        min_ratio = min([val / self.game.start_dim[i] for i, val in enumerate(self.game.dim)])
        title_fs = 50 * min_ratio
        title_padding = 20 * min_ratio
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] - title.get_width() - title_padding
        self.canvas.draw((0, 0), self.game.dim, Colors.white)

        cover = pygame.Surface(self.game.dim, pygame.SRCALPHA)
        cover.fill((0, 0, 0, 0.3 * 255))
        self.choosing_name = True
        self.game.screen.blit(cover, (0, 0))
        popup_dim = (self.game.dim[0] / 2, self.game.dim[1] / 1.5)
        popup_pos = (self.game.dim[0] / 2 - popup_dim[0] / 2, self.game.dim[1] / 2 - popup_dim[1] / 2)
        popup_rect = pygame.Rect(popup_pos, popup_dim)
        popup_bdrad = 10
        popup_rect.inflate(-2 * popup_bdrad, -2 * popup_bdrad)
        pygame.draw.rect(self.game.screen, Colors.white, popup_rect, border_radius=popup_bdrad)
        img_size = 100 * min_ratio
        img_pos = (popup_pos[0] + popup_dim[0] / 2 - img_size / 2, popup_pos[1] + title_padding)
        self.game.draw(pygame.transform.smoothscale(self.img, (img_size, self.img.get_height() / self.img.get_width() * img_size)), img_pos)
        text = self.game.text_surface(self.text, 'Arial', title_fs / 2, Colors.purple)
        self.game.draw(text, (popup_pos[0] + popup_dim[0] / 2 - text.get_width() / 2, img_pos[1] + img_size + title_padding))
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg * min_ratio * 2), (title_x, title_padding + 4 * min_ratio))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title * min_ratio * 2), (title_x, title_padding))
        self.base_btn_dim = (popup_dim[0] / 2, popup_dim[1] / 6)

        if not hasattr(self, 'again_btn_dim'):
            self.again_btn_dim = self.base_btn_dim
            self.back_btn_dim = self.base_btn_dim
        
        again_btn_pos = (popup_pos[0] + popup_dim[0] / 2 - self.again_btn_dim[0] / 2, img_pos[1] + img_size + text.get_height() + 2 * title_padding)
        self.again_btn = self.game.create_btn(again_btn_pos, self.again_btn_dim, Colors.purple, round(10 * min_ratio), 'Erneut spielen', 'Arial', round(20 * min_ratio), Colors.salmon)
        self.back_btn = self.game.create_btn((popup_pos[0] + popup_dim[0] / 2 - self.back_btn_dim[0] / 2, again_btn_pos[1] + self.again_btn_dim[1] + title_padding), self.back_btn_dim, Colors.salmon, round(10 * min_ratio), 'Zurück', 'Arial', round(20 * min_ratio), Colors.white)
    
    def iteration(self:any)->None:
        if self.again_btn.collidepoint(pygame.mouse.get_pos()):
            if self.again_btn_hover.switch_true():
                self.again_btn_dim = (self.base_btn_dim[0] * 1.1, self.base_btn_dim[1] * 1.1)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.again_btn_hover.switch_false():
            self.again_btn_dim = self.base_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        if self.back_btn.collidepoint(pygame.mouse.get_pos()):
            if self.back_btn_hover.switch_true():
                self.back_btn_dim = (self.base_btn_dim[0] * 1.1, self.base_btn_dim[1] * 1.1)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_btn_hover.switch_false():
            self.back_btn_dim = self.base_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        self.canvas.iteration()
                         
    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.again_btn_hover.state:
                self.game.return_info = 'play_again'
                self.game.goto_page('Menu')
                return

            if self.back_btn_hover.state:
                self.game.goto_page('Menu')
                return
        
        if event.type == pygame.VIDEORESIZE:
            self.back_btn_hover.switch_true()
            self.again_btn_hover.switch_true()
            
        self.canvas.event_check(event)

