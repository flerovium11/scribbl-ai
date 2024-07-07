import pygame
from utils.colors import Colors
from external.definitions import LobbyState, PlayerRole
from pages.page import Page
from pages.menu import Menu
from utils.playerlist import PlayerList
from utils.input import Input
from utils.eventbool import EventBool


class Lobby(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self: any) -> None:
        self.was_connected = False
        self.game.playerlist = PlayerList(self.game)
        self.choosing_name = False
        self.name_input = Input(self.game, self, Colors.beige, 40,
                                placeholder_color=Colors.salmon, placeholder='Dein Name...')
        self.base_name_btn_dim = (0, 0)
        self.cancel_btn_hover = EventBool(self.trigger_update)
        self.enter_btn_hover = EventBool(self.trigger_update)
        self.cancel_btn = None
        self.enter_btn = None
        self.is_connected = False

    def draw(self: any) -> None:
        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i]
                        for i, val in enumerate(self.game.dim)])
        self.base_exit_btn_dim = (150 * min_ratio, 75 * min_ratio)

        if not hasattr(self, 'exit_btn_dim'):
            self.exit_btn_dim = self.base_exit_btn_dim

        title_fs = 50 * min_ratio
        title_padding = 20 * min_ratio
        title = self.game.text_surface(
            'ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface(
            'ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] - title.get_width() - title_padding
        self.game.draw(pygame.transform.rotate(
            title_bg, self.rotate_bg * min_ratio * 2), (title_x, title_padding + 4 * min_ratio))
        self.game.draw(pygame.transform.rotate(
            title, self.rotate_title * min_ratio * 2), (title_x, title_padding))
        center_info = None
        player = None
        remove_exit_btn = False

        if 'mode' in self.game.client.info and self.game.client.info['mode'] == 'lobby':
            self.was_connected = True
            self.is_connected = True
            player = self.game.client.info['lobby']['players'][self.game.client.info['id']]

            if self.game.client.info['lobby']['state'] == LobbyState.WAITING.name:
                self.exit_btn = None
                player_count = len(self.game.client.info['lobby']['players'])
                count = self.game.client.info['lobby']['countdown']
                max_players = self.game.client.info['lobby']['max_players']
                min_players = self.game.client.info['lobby']['min_players']
                status = 'online' if player['online'] else 'offline'
                status_color = Colors.pink if player['online'] else Colors.gray

                bottom_info = f'Warte auf weitere Spieler ({player_count}/{max_players})' if player_count < max_players else f'({player_count}/{max_players}) Spieler bereit'

                if player_count >= min_players:
                    bottom_info += f' - Spiel startet in {round(count)} Sekunden'

                info_text = self.game.text_surface(
                    bottom_info, 'Arial', title_fs / 2.5, Colors.purple)
                self.game.draw(info_text, (self.game.dim[0] - info_text.get_width(
                ) - title_padding, self.game.dim[1] - info_text.get_height() - title_padding))
                players = self.game.client.info['lobby']['players']
                playerlist_pos = (
                    title_padding, title_padding * 2 + self.exit_btn_dim[1])
                playerlist_dim = (self.game.dim[0] - 2 * title_padding,
                                  self.game.dim[1] - playerlist_pos[1] - title_padding * 4)
                self.game.playerlist.draw(playerlist_pos, playerlist_dim, 10, players, self.game.client.info['id'], 5, title_padding * 2, (
                    title_padding, title_padding), 3, Colors.white, Colors.salmon, Colors.gray, Colors.black)

                status_info_text = self.game.text_surface(
                    status, 'Arial', title_fs / 3, Colors.salmon)
                info_dim = (status_info_text.get_width() +
                            title_padding, status_info_text.get_height() * 1.5)
                info_pos = (
                    title_fs / 3, self.game.dim[1] - info_dim[1] - title_fs / 3)
                self.game.create_btn(
                    info_pos, info_dim, status_color, 10, status, 'Arial', title_fs / 3, Colors.black)
            elif self.game.client.info['lobby']['state'] == LobbyState.READY.name:
                center_info = 'Spiel startet...'
                remove_exit_btn = True
            elif self.game.client.info['lobby']['state'] in [LobbyState.CHOOSE_WORD.name, LobbyState.GAME.name]:
                if player['role'] == PlayerRole.DRAWER.name:
                    self.game.goto_page('Draw')
                elif player['role'] == PlayerRole.GUESSER.name:
                    self.game.goto_page('Guess')
            elif self.game.client.info['lobby']['state'] in [LobbyState.STOPPED.name, LobbyState.DISCONNECTED.name]:
                center_info = 'Verbindung verloren'
                self.is_connected = False
        elif self.was_connected:
            self.game.client.disconnect()
            self.game.return_info = 'Verbindung verloren'
            self.game.goto_page('Menu')
        else:
            center_info = 'Suche Spiel...'
            self.is_connected = False

        if center_info is not None:
            info_text = self.game.text_surface(
                center_info, 'Arial', title_fs / 1.5, Colors.purple)
            self.game.draw(info_text, (self.game.dim[0] / 2 - info_text.get_width(
            ) / 2, self.game.dim[1] / 2 - info_text.get_height() / 2))

        if not remove_exit_btn:
            self.exit_btn = self.game.create_btn((title_padding - (self.exit_btn_dim[0] - self.base_exit_btn_dim[0])*0.5, title_padding - (
                self.exit_btn_dim[1] - self.base_exit_btn_dim[1])*0.5), self.exit_btn_dim, Colors.purple, round(10 * min_ratio), 'Abbrechen', 'Arial', round(30 * min_ratio), Colors.salmon)

        if self.game.client is not None and self.game.client.name is None:
            cover = pygame.Surface(self.game.dim, pygame.SRCALPHA)
            cover.fill((0, 0, 0, 0.7 * 255))
            self.choosing_name = True
            self.game.screen.blit(cover, (0, 0))
            popup_dim = (self.game.dim[0] / 1.5, self.game.dim[1] / 2)
            popup_pos = (self.game.dim[0] / 2 - popup_dim[0] / 2,
                         self.game.dim[1] / 2 - popup_dim[1] / 2)
            popup_rect = pygame.Rect(popup_pos, popup_dim)
            popup_bdrad = 10
            popup_rect.inflate(-2 * popup_bdrad, -2 * popup_bdrad)
            pygame.draw.rect(self.game.screen, Colors.white,
                             popup_rect, border_radius=popup_bdrad)
            text = self.game.text_surface(
                'Wie möchtest du genannt werden?', 'Ink Free', title_fs / 2, Colors.purple)
            self.game.draw(
                text, (popup_pos[0] + popup_dim[0] / 2 - text.get_width() / 2, popup_pos[1] + title_padding))
            input_y = popup_pos[1] + text.get_height() + 2 * title_padding
            self.name_input.draw((popup_pos[0] + title_padding, input_y), popup_dim[0] -
                                 4 * title_padding, (title_padding, title_padding / 2), 10)
            self.base_name_btn_dim = (popup_dim[0] / 3 - 1.5 * title_padding, popup_dim[1] -
                                      input_y + popup_pos[1] - self.name_input.rect.height - 4 * title_padding)

            if not hasattr(self, 'cancel_btn_dim'):
                self.cancel_btn_dim = self.base_name_btn_dim
                self.enter_btn_dim = self.base_name_btn_dim

            show_enter = self.name_input.manager.value.strip() != ''
            cancel_btn_pos = (popup_pos[0] + popup_dim[0] - (1 + show_enter) * title_padding - 2 * self.base_name_btn_dim[0] + (
                self.base_name_btn_dim[0] if not show_enter else 0), popup_pos[1] + popup_dim[1] - self.base_name_btn_dim[1] - title_padding)
            self.cancel_btn = self.game.create_btn(cancel_btn_pos, self.cancel_btn_dim, Colors.red, round(
                10 * min_ratio), 'Abbrechen', 'Arial', round(20 * min_ratio), Colors.black)

            if show_enter:
                self.enter_btn = self.game.create_btn((cancel_btn_pos[0] + self.base_name_btn_dim[0] + title_padding, cancel_btn_pos[1]),
                                                      self.enter_btn_dim, Colors.purple, round(10 * min_ratio), 'Bestätigen', 'Arial', round(20 * min_ratio), Colors.salmon)
        else:
            self.choosing_name = False
            self.cancel_btn = None
            self.enter_btn = None

    def iteration(self: any) -> None:
        if self.exit_btn is not None and self.exit_btn.collidepoint(self.mouse_pos) and not self.choosing_name:
            if self.back_button_hover.switch_true():
                self.exit_btn_dim = tuple(
                    [val * 1.05 for val in self.base_exit_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_button_hover.switch_false():
            self.exit_btn_dim = self.base_exit_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.cancel_btn is not None and self.cancel_btn.collidepoint(self.mouse_pos):
            if self.cancel_btn_hover.switch_true():
                self.cancel_btn_dim = tuple(
                    [val * 1.05 for val in self.base_name_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.cancel_btn_hover.switch_false():
            self.cancel_btn_dim = self.base_name_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.enter_btn is not None and self.enter_btn.collidepoint(self.mouse_pos):
            if self.enter_btn_hover.switch_true():
                self.enter_btn_dim = tuple(
                    [val * 1.05 for val in self.base_name_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.enter_btn_hover.switch_false():
            self.enter_btn_dim = self.base_name_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def event_check(self: any, event: pygame.event) -> None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()

        can_exit = (self.game.client is None or self.game.client.info is None or 'lobby' not in self.game.client.info or self.game.client.info[
                    'lobby']['state'] == LobbyState.WAITING.name) or not self.is_connected

        if ((self.back_button_hover.state and (not self.choosing_name or not self.is_connected)) or self.cancel_btn_hover.state) and event.type == pygame.MOUSEBUTTONDOWN and can_exit:
            self.game.client.disconnect()
            self.game.goto_page('Menu')

        if self.enter_btn_hover.state and event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and len(self.name_input.manager.value.strip()) and self.choosing_name:
            self.game.client.name = self.name_input.manager.value

        if event.type == pygame.VIDEORESIZE:
            self.back_button_hover.switch_true()
            self.cancel_btn_hover.switch_true()
            self.enter_btn_hover.switch_true()

        self.name_input.event_check(event)
