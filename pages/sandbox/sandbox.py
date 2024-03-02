import pygame
from utils.colors import Colors
from pages.page import Page

class Sandbox(Page):
    rotate_title = 0.1
    rotate_bg = -0.1
    rotate = pygame.USEREVENT + 1
    
    def on_start(self:any)->None:
        pygame.time.set_timer(self.rotate, 500)

    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i] for i, val in enumerate(self.game.dim)])
        self.base_btn_dim = (150 * min_ratio, 75 * min_ratio)
        if not hasattr(self, 'btn_dim'):
            self.btn_dim = self.base_btn_dim
        title_fs = 50 * min_ratio
        title_padding = 20 * min_ratio
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] - title.get_width() - title_padding
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg * min_ratio * 2), (title_x, title_padding + 4 * min_ratio))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title * min_ratio * 2), (title_x, title_padding))
        self.btn = self.game.create_btn((title_padding - (self.btn_dim[0] - self.base_btn_dim[0])*0.5, title_padding - (self.btn_dim[1] - self.base_btn_dim[1])*0.5), self.btn_dim, Colors.purple, round(10 * min_ratio), 'Zurück', 'Arial', round(30 * min_ratio), Colors.salmon)
        

    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1

        self.btn_dim = self.base_btn_dim

        # Handle mouse clicks
        if self.btn.collidepoint(self.mouse_pos):
            self.btn_dim = tuple([val * 1.05 for val in self.base_btn_dim])
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.game.goto_page('Menu')
