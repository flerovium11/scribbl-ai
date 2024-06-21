import pygame
from utils.colors import Colors
from pages.page import Page

class Lobby(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self:any)->None:
        pass
    
    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i] for i, val in enumerate(self.game.dim)])
        self.base_exit_btn_dim = (150 * min_ratio, 75 * min_ratio)

        if not hasattr(self, 'exit_btn_dim'):
            self.exit_btn_dim = self.base_exit_btn_dim
        
        title_fs = 50 * min_ratio
        title_padding = 20 * min_ratio
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] - title.get_width() - title_padding
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg * min_ratio * 2), (title_x, title_padding + 4 * min_ratio))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title * min_ratio * 2), (title_x, title_padding))

        if 'mode' in self.game.client.info and self.game.client.info['mode'] == 'lobby':
            self.exit_btn = None
            player_count = len(self.game.client.info["lobby"]["players"])
            count = self.game.client.info["lobby"]["countdown"]
            max_players = self.game.client.info["lobby"]["max_players"]
            min_players = self.game.client.info["lobby"]["min_players"]

            bottom_info = f'Warte auf weitere Spieler ({player_count}/{max_players})' if player_count < max_players else f'({player_count}/{max_players}) Spieler bereit'

            if player_count >= min_players:
                bottom_info += f' - Spiel startet in {count} Sekunden'
            
            info_text = self.game.text_surface(bottom_info, 'Arial', title_fs / 2, Colors.purple)
            self.game.draw(info_text, (self.game.dim[0] - info_text.get_width() - title_padding, self.game.dim[1] - info_text.get_height() - title_padding))
        else:
            info_text = self.game.text_surface('Suche Spiel...', 'Arial', title_fs / 1.5, Colors.purple)
            self.game.draw(info_text, (self.game.dim[0] / 2 - info_text.get_width() / 2, self.game.dim[1] / 2 - info_text.get_height() / 2))
        
        self.exit_btn = self.game.create_btn((title_padding - (self.exit_btn_dim[0] - self.base_exit_btn_dim[0])*0.5, title_padding - (self.exit_btn_dim[1] - self.base_exit_btn_dim[1])*0.5), self.exit_btn_dim, Colors.purple, round(10 * min_ratio), 'Abbrechen', 'Arial', round(30 * min_ratio), Colors.salmon)
    
    def iteration(self:any)->None:
        if self.exit_btn is not None and self.exit_btn.collidepoint(self.mouse_pos):
            if self.back_button_hover.switch_true():
                self.exit_btn_dim = tuple([val * 1.05 for val in self.base_exit_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_button_hover.switch_false():
            self.exit_btn_dim = self.base_exit_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
        
        if self.back_button_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.client.disconnect()
            self.game.goto_page('Menu')
