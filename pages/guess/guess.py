import pygame
from utils.colors import Colors
from utils.timer import Timer
from pages.page import Page
from utils.eventbool import EventBool
from utils.canvas import Canvas
from utils.input import Input
from external.definitions import LobbyState, PlayerRole, decompress_grid


class Guess(Page):
    rotate = pygame.USEREVENT + 1

    def on_init(self: any) -> None:
        self.canvas = Canvas(self.game, self, grid_width=100,
                             grid_height=100, readonly=True)
        self.text_input = Input(
            self.game, self, placeholder='Errate das Wort...', disabled_color=Colors.salmon)
        self.done_btn_hover = EventBool(self.trigger_update)

    def on_start(self: any) -> None:
        # Otherwise mouse might stay hand on page switch
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw(self: any) -> None:
        self.check_network_connection(
            [LobbyState.CHOOSE_WORD.name, LobbyState.GAME.name], [PlayerRole.GUESSER.name])

        if self.game.pagename != self.name or not self.game.running:
            return

        self.game.screen.fill(Colors.beige)
        min_ratio = min([val / self.game.start_dim[i]
                        for i, val in enumerate(self.game.dim)])
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

        status_color = Colors.pink if self.clt.player['online'] else Colors.gray

        canvas_size = min(self.game.dim[1] - (title_padding * 2 + title.get_height()) -
                          title_padding * 3, self.game.dim[0] * (2 / 3) - title_padding * 3)
        playerlist_dim = (
            self.game.dim[0] - canvas_size - 3 * title_padding, self.game.dim[1] - title_padding * 6 - title.get_height())
        playerlist_pos = (self.game.dim[0] - playerlist_dim[0] -
                          title_padding, title_padding * 2 + title.get_height())

        grid = self.clt.lobby['grid'] if self.clt.lobby['grid'] is not None else {
            'tiles': [[0]], 'dim': (1, 1)}
        self.canvas.grid_width = grid['dim'][0]
        self.canvas.grid_height = grid['dim'][1]
        self.canvas.grid = decompress_grid(
            grid['tiles'], self.canvas.grid_width) if 'compressed' in grid else grid['tiles']

        self.game.playerlist.draw(playerlist_pos, playerlist_dim, 10, self.clt.players, self.clt.info['id'], 5, title_padding * 2, (
            title_padding, title_padding), 3, Colors.white, Colors.salmon, Colors.gray, Colors.black)
        self.canvas.draw(
            (title_padding, playerlist_pos[1]), (canvas_size, canvas_size), Colors.white)

        status_info_text = self.game.text_surface(
            self.clt.status, 'Arial', title_fs / 3, Colors.salmon)
        info_dim = (status_info_text.get_width() + title_padding,
                    status_info_text.get_height() * 1.5)
        info_pos = (
            title_fs / 3, self.game.dim[1] - info_dim[1] - title_fs / 3)
        self.game.create_btn(info_pos, info_dim, status_color, 10,
                             self.clt.status, 'Arial', title_fs / 3, Colors.black)

        info = 'Der Zeichner wählt ein Wort aus...' if self.clt.game_state == LobbyState.CHOOSE_WORD.name else 'Errate, was der Zeichner zeichnet!'
        info_text = self.game.text_surface(
            info, 'Arial', title_fs / 2.5, Colors.purple)
        self.game.draw(info_text, (title_padding, title_padding +
                       title.get_height() // 2 - info_text.get_height() // 2))
        Timer.draw(self.game, (canvas_size - title_padding, title.get_height() // 2), title_padding,
                   Colors.pink, Colors.black, self.clt.lobby['countdown'], self.clt.lobby['draw_time'])

        input_dim = (self.game.dim[0] / 2, self.game.dim[1] -
                     playerlist_pos[1] - playerlist_dim[1] - 2 * title_padding)

        self.done_btn_base_rad = input_dim[1] / 2
        if not hasattr(self, 'done_btn_rad'):
            self.done_btn_rad = self.done_btn_base_rad

        done_btn_pos = (self.game.dim[0] - title_padding - 2 * self.done_btn_rad,
                        playerlist_pos[1] + playerlist_dim[1] + title_padding)
        input_pos = (done_btn_pos[0] - input_dim[0] -
                     2 * title_padding, done_btn_pos[1])
        self.done_btn = pygame.Rect(
            *done_btn_pos, 2 * self.done_btn_rad, 2 * self.done_btn_rad)
        done_btn_text = self.game.text_surface(
            '⮐' if self.clt.has_guessed else '✔', 'Segoe UI Symbol', title_fs / 2, Colors.beige)

        if self.clt.game_state == LobbyState.GAME.name:
            if self.text_input.manager.value != '':
                pygame.draw.circle(self.game.screen, Colors.red if self.clt.has_guessed else Colors.purple, (
                    self.done_btn.center), self.done_btn_rad)
                self.game.draw(done_btn_text, (self.done_btn.center[0] - done_btn_text.get_width(
                ) // 2, self.done_btn.center[1] - done_btn_text.get_height() // 2))

            self.text_input.font_size = input_dim[1] - title_padding
            self.text_input.disabled = self.clt.has_guessed
            self.text_input.draw(
                input_pos, input_dim[0], (title_padding / 2, title_padding / 2), 10)

    def iteration(self: any) -> None:
        self.canvas.iteration()
        self.clt.guess = self.text_input.manager.value

        if self.done_btn.collidepoint(self.mouse_pos):
            if self.done_btn_hover.switch_true():
                self.done_btn_rad = 1.1 * self.done_btn_base_rad
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.done_btn_hover.switch_false():
            self.done_btn_rad = self.done_btn_base_rad
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def event_check(self: any, event: pygame.event) -> None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()

        if event.type == pygame.MOUSEBUTTONDOWN and self.done_btn_hover.state:
            self.clt.has_guessed = not self.clt.has_guessed

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.text_input.manager.value.strip()):
                self.clt.has_guessed = True

            if event.key == pygame.K_ESCAPE:
                self.clt.has_guessed = False

        if event.type == pygame.VIDEORESIZE:
            self.done_btn_hover.switch_true()

        self.canvas.event_check(event)
        self.text_input.event_check(event)
