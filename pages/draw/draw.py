import pygame
from utils.colors import Colors
from pages.page import Page
from external.definitions import LobbyState, PlayerRole

class Draw(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self:any)->None:
        pass

    def on_start(self:any)->None:
        pass

    def draw(self:any)->None:
        self.check_network_connection([LobbyState.CHOOSE_WORD.name, LobbyState.GAME.name], [PlayerRole.DRAWER.name])
        
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
        playerlist_pos = (title_padding, title_padding)
        playerlist_dim = (self.game.dim[0] - 2 * title_padding, self.game.dim[1] - playerlist_pos[1] - title_padding * 4)
        self.game.playerlist.draw(playerlist_pos, playerlist_dim, 10, self.clt.players, self.clt.info['id'], 5, title_padding * 2, (title_padding, title_padding), 3, Colors.white, Colors.salmon, Colors.gray, Colors.black)

        status_info_text = self.game.text_surface(self.clt.status, 'Arial', title_fs / 3, Colors.salmon)
        info_dim = (status_info_text.get_width() + title_padding, status_info_text.get_height() * 1.5)
        info_pos = (title_fs / 3, self.game.dim[1] - info_dim[1] - title_fs / 3)
        self.game.create_btn(info_pos, info_dim, status_color, 10, self.clt.status, 'Arial', title_fs / 3, Colors.black)

        if self.clt.game_state == LobbyState.CHOOSE_WORD.name:
            cover = pygame.Surface(self.game.dim, pygame.SRCALPHA)
            cover.fill((0, 0, 0, 0.7 * 255))
            self.choosing_name = True
            self.game.screen.blit(cover, (0, 0))
            popup_dim = (self.game.dim[0] / 1.5, self.game.dim[1] / 2)
            popup_pos = (self.game.dim[0] / 2 - popup_dim[0] / 2, self.game.dim[1] / 2 - popup_dim[1] / 2)
            popup_rect = pygame.Rect(popup_pos, popup_dim)
            popup_bdrad = 10
            popup_rect.inflate(-2 * popup_bdrad, -2 * popup_bdrad)
            pygame.draw.rect(self.game.screen, Colors.white, popup_rect, border_radius=popup_bdrad)
            text = self.game.text_surface('Wähle ein Wort, das du zeichnen willst!', 'Ink Free', title_fs / 2, Colors.purple)
            self.game.draw(text, (popup_pos[0] + popup_dim[0] / 2 - text.get_width() / 2, popup_pos[1] + title_padding))
    
    def iteration(self:any)->None:
        pass
        
    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
