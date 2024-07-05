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

        h1_fs = 27 * min_ratio
        p_fs = 18 * min_ratio
        h1_py = (40 * min_ratio, 20 * min_ratio)
        p_py = (10 * min_ratio, 10 * min_ratio)
        element_flow = []
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Zweck', 'Ink Free', h1_fs, Colors.purple)})
        self.paragraph('ScribblAI ist ein Spiel, das die Anwendungsmöglichkeiten von Bilderkennung mit KI und Multiplayer-Netzwerktechnik erforscht. Es wurde 2024 im Rahmen der Coding_Academy am WIFI Gmunden erschaffen.', 'Arial', p_fs, Colors.black, p_py, self.game.dim[0] / (p_fs * 0.5), element_flow)
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Spielkonzept', 'Ink Free', h1_fs, Colors.purple)})
        self.paragraph('Eine Person muss ein Wort zeichnen und die anderen müssen es erraten. Das Bild wird zusätzlich durch ein CNN geschickt, und sollte die KI das Bild richtig klassifizieren, verlieren alle menschlichen Spieler*innen. Das Ziel ist es folglich, so zu zeichnen, dass Menschen das Wort erraten können, aber kein Computeralgorithmus.', 'Arial', p_fs, Colors.black, p_py, self.game.dim[0] / (p_fs * 0.5), element_flow)
        element_flow.append({'py': h1_py, 'el': self.game.text_surface('Danksagungen', 'Ink Free', h1_fs, Colors.purple)})
        self.paragraph("""Danke an unseren WIFI-Trainer Hannes Lettner. \n
Bilddatenset: quickdraw.withgoogle.com \n
Grundlegende Spielidee: skribbl.io""", 'Arial', p_fs, Colors.black, p_py, self.game.dim[0] / (p_fs * 0.5), element_flow)

        posy = 2 * title_padding + title.get_height()
        posx = (self.game.dim[0] - max([el['el'].get_width() for el in element_flow])) / 2

        for element in element_flow:
            posy += element['py'][0]
            self.game.draw(element['el'], (posx, posy))
            posy += element['py'][1]

    def paragraph(self: any, text: str, font: str, fs: int, color: Colors, pad: int, maxlen: int, element_flow: list) -> None:
        words = text.split(' ')
        line = ''

        for word in words:
            if len(line + word + ' ') > maxlen or (len(word) and '\n' in word):
                element_flow.append({'py': pad, 'el': self.game.text_surface(line[:-1], font, fs, color)})
                line = word.replace('\n', '') + ' '
            else:
                line += word + ' '
        
        if line:
            element_flow.append({'py': pad, 'el': self.game.text_surface(line[:-1], font, fs, color)})


    def iteration(self:any)->None:
        if self.btn.collidepoint(self.mouse_pos):
            if self.back_button_hover.switch_true():
                self.btn_dim = tuple([val * 1.05 for val in self.base_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_button_hover.switch_false():
            self.btn_dim = self.base_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
        
        if self.back_button_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.goto_page('Menu')
        
        if event.type == pygame.VIDEORESIZE:
            self.back_button_hover.switch_true()
