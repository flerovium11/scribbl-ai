import pygame
from utils.colors import Colors
from utils.timer import Timer
from pages.page import Page
from utils.eventbool import EventBool
from utils.canvas import Canvas
from external.definitions import LobbyState, PlayerRole, compress_grid

class Draw(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self:any)->None:
        self.base_word_btn_dim = (0, 0)
        self.word_btns = None
        self.canvas = Canvas(self.game, self, grid_width=200, grid_height=200)

    def on_start(self:any)->None:
        pass

    def draw(self:any)->None:
        self.check_network_connection([LobbyState.CHOOSE_WORD.name, LobbyState.GAME.name], [PlayerRole.DRAWER.name])

        if self.game.pagename != self.name or not self.game.running:
            return
        
        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i] for i, val in enumerate(self.game.dim)])
        title_fs = 50 * min_ratio
        title_padding = 20 * min_ratio
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] - title.get_width() - title_padding
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg * min_ratio * 2), (title_x, title_padding + 4 * min_ratio))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title * min_ratio * 2), (title_x, title_padding))

        status_color = Colors.pink if self.clt.player['online'] else Colors.gray
        playerlist_dim = (self.game.dim[0] / 3, self.game.dim[1] - title_padding * 3 - title.get_height())
        playerlist_pos = (self.game.dim[0] - playerlist_dim[0] - title_padding, title_padding * 2 + title.get_height())

        self.game.playerlist.draw(playerlist_pos, playerlist_dim, 10, self.clt.players, self.clt.info['id'], 5, title_padding * 2, (title_padding, title_padding), 3, Colors.white, Colors.salmon, Colors.gray, Colors.black)

        status_info_text = self.game.text_surface(self.clt.status, 'Arial', title_fs / 3, Colors.salmon)
        info_dim = (status_info_text.get_width() + title_padding, status_info_text.get_height() * 1.5)
        info_pos = (title_fs / 3, self.game.dim[1] - info_dim[1] - title_fs / 3)
        self.game.create_btn(info_pos, info_dim, status_color, 10, self.clt.status, 'Arial', title_fs / 3, Colors.black)

        canvas_dim = (self.game.dim[0] - playerlist_dim[0] - 3 * title_padding, self.game.dim[1] - playerlist_pos[1] - title_padding * 3)
        self.canvas.draw((title_padding, playerlist_pos[1]), canvas_dim, Colors.white)
        self.clt.grid = {'tiles': compress_grid(self.canvas.grid), 'dim': (self.canvas.grid_width, self.canvas.grid_height), 'compressed': True}

        self.choosing = self.clt.game_state == LobbyState.CHOOSE_WORD.name and self.clt.word_index is None

        if self.choosing:
            cover = pygame.Surface(self.game.dim, pygame.SRCALPHA)
            cover.fill((0, 0, 0, 0.7 * 255))
            self.choosing_name = True
            self.game.screen.blit(cover, (0, 0))
            popup_dim = (self.game.dim[0] / 1.2, self.game.dim[1] / 2)
            popup_pos = (self.game.dim[0] / 2 - popup_dim[0] / 2, self.game.dim[1] / 2 - popup_dim[1] / 2)
            popup_rect = pygame.Rect(popup_pos, popup_dim)
            popup_bdrad = 10
            popup_rect.inflate(-2 * popup_bdrad, -2 * popup_bdrad)
            pygame.draw.rect(self.game.screen, Colors.beige, popup_rect, border_radius=popup_bdrad)
            text = self.game.text_surface('Wähle ein Wort, das du zeichnen willst!', 'Ink Free', title_fs / 2, Colors.purple)
            self.game.draw(text, (popup_pos[0] + title_padding, popup_pos[1] + title_padding))
            words = self.clt.info['lobby']['words']
            word_count = len(words)
            self.base_word_btn_dim = ((popup_dim[0] - title_padding * 2) / word_count - title_padding * 0.5, popup_dim[1] / 2 - title_padding * 2)

            if not hasattr(self, 'word_btn_dims'):
                self.word_btn_dims = [self.base_word_btn_dim] * word_count
            
            if not hasattr(self, 'word_btns_hover'):
                self.word_btns_hover = []
                for i in range(word_count):
                    self.word_btns_hover.append(EventBool(self.trigger_update))

            self.word_btns = []
            btn_y = (popup_pos[1] + title_padding + text.get_height() + popup_dim[1]) / 2

            for i, word in enumerate(words):
                button = self.game.create_btn((popup_pos[0] + title_padding + i * (self.base_word_btn_dim[0] + title_padding * 0.5), btn_y), self.word_btn_dims[i], Colors.purple, round(10 * min_ratio), word, 'Arial', round(20 * min_ratio), Colors.salmon, auto_fontsize=True, padding_x=int(10 * min_ratio))
                self.word_btns.append(button)
            
            Timer.draw(self.game, (popup_pos[0] + popup_dim[0] - title_padding * 3, popup_pos[1] + title_padding), title_padding, Colors.pink, Colors.black, self.clt.lobby['countdown'], self.clt.lobby['choose_word_time'])
        else:
            self.word_btns = None
            info = f'Schnell, zeichne "{self.clt.lobby["word"]}"!' if self.clt.lobby['word'] is not None else "Schnell, zeichneeeeee..."
            info_text = self.game.text_surface(info, 'Arial', title_fs / 2.5, Colors.purple)
            self.game.draw(info_text, (title_padding, title_padding + title.get_height() // 2 - info_text.get_height() // 2))
            Timer.draw(self.game, (canvas_dim[0] - title_padding, title.get_height() // 2), title_padding, Colors.pink, Colors.black, self.clt.lobby['countdown'], self.clt.lobby['draw_time'])

    
    def iteration(self:any)->None:
        if self.word_btns is not None:
            for i, btn in enumerate(self.word_btns):
                if btn.collidepoint(self.mouse_pos):
                    if self.word_btns_hover[i].switch_true():
                        self.word_btn_dims[i] = tuple([val * 1.05 for val in self.base_word_btn_dim])
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                elif self.word_btns_hover[i].switch_false():
                    self.word_btn_dims[i] = self.base_word_btn_dim
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        if not self.choosing:
            self.canvas.iteration()
                         
    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, hovering in enumerate(self.word_btns_hover):
                if hovering.state:
                    self.clt.word_index = i
        
        if event.type == pygame.VIDEORESIZE:
            for hovering in self.word_btns_hover:
                hovering.switch_true()
        
        if not self.choosing:
            self.canvas.event_check(event)
