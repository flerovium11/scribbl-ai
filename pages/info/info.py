import pygame
from utils.colors import Colors
from pages.page import Page

class Info(Page):  
    rotate_title = 0.1
    rotate_bg = -0.1
    rotate = pygame.USEREVENT + 1
    base_btn_dim = btn_dim = (200, 100)
    
    def on_start(self:any)->None:
        pygame.time.set_timer(self.rotate, 500)

    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i] for i, val in enumerate(self.game.dim)])
        print(min_ratio)
        title_fs = round(min(180, self.game.dim[0] / 5.147, self.game.dim[1] / 4.583))
        title_padding_top = 30
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] // 2 - title.get_width() // 2
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg / 120 * title_fs), (title_x, title_padding_top + title_fs/12))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title / 120 * title_fs), (title_x, title_padding_top))

        self.btn = self.game.create_btn((20, 20), self.btn_dim, Colors.salmon, 10, 'Zurück', 'Arial', 30, Colors.purple)     

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
