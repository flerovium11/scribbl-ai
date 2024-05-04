import pygame
from utils.colors import Colors
from pages.page import Page

class Info(Page):  
    rotate = pygame.USEREVENT + 1
    
    def on_init(self:any)->None:
        pygame.event.set_allowed([self.rotate])

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

        h1_fs = 30 * min_ratio
        p_fs = 20 * min_ratio
        h1_py = (40 * min_ratio, 20 * min_ratio)
        p_py = (10 * min_ratio, 10 * min_ratio)
        element_flow = []
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Was passiert hier?', 'Ink Free', h1_fs, Colors.purple)})
        element_flow.append({'py': p_py, 'el': self.game.text_surface('Das ist ein Spiel', 'Arial', p_fs, Colors.black)})
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Was muss ich machen?', 'Ink Free', h1_fs, Colors.purple)})
        element_flow.append({'py': p_py, 'el': self.game.text_surface('Du kannst Mehrspieler oder Sandkiste (Einzelspieler) spielen', 'Arial', p_fs, Colors.black)})
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Wer hat das gemacht?', 'Ink Free', h1_fs, Colors.purple)})
        element_flow.append({'py': p_py, 'el': self.game.text_surface('Ich habe das für die coding_academy gemacht (Ennio Binder)', 'Arial', p_fs, Colors.black)})
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Wer hat das gemacht?', 'Ink Free', h1_fs, Colors.purple)})

        posy = ((self.game.dim[1] - title_padding - title.get_height()) - sum([el['el'].get_height() + el['py'][0] for el in element_flow])) / 2 + title.get_height() + title_padding
        posx = (self.game.dim[0] - max([el['el'].get_width() for el in element_flow])) / 2

        for element in element_flow:
            posy += element['py'][0]
            self.game.draw(element['el'], (posx, posy))
            posy += element['py'][1]

    def iteration(self:any)->None:
        if self.btn.collidepoint(self.mouse_pos):
            if self.back_button_hover.switch_true():
                self.btn_dim = tuple([val * 1.05 for val in self.base_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_button_hover.switch_false():
            self.btn_dim = self.base_btn_dim

    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
        
        if self.back_button_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.goto_page('Menu')
