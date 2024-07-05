import threading
import pygame
from utils.colors import Colors
from utils.eventbool import EventBool
from pages.page import Page
from utils.client import Client, ClientStatus

class Menu(Page):
    modebtn_radius = 10
    buttons_distance = 50
    base_qbr = qbr = 40
    rotate_title = 0.1
    rotate_bg = -0.1
    rotate = pygame.USEREVENT + 1
    base_modebtn_dim = modebtn_dim = modebtn1_dim = modebtn2_dim = (220, 140)
    
    def on_init(self:any)->None:
        pygame.event.set_allowed([self.rotate])
        self.modebtn1_hover = EventBool(self.trigger_update)
        self.modebtn2_hover = EventBool(self.trigger_update)
        self.qb_hover = EventBool(self.trigger_update)
        self.connect_thread = None
    
    def on_start(self:any)->None:
        pygame.time.set_timer(self.rotate, 500)
        self.multiplayer_info = None

        if self.game.return_info is not None:
            if self.game.return_info == 'play_again':
                self.start_game()
            
            self.multiplayer_info = self.game.return_info
            self.game.return_info = None

    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)

        title_fs = round(min(180, self.game.dim[0] / 5.147, self.game.dim[1] / 4.583))
        self.modebtn_dim = tuple([val*title_fs/120 for val in self.base_modebtn_dim])
        self.base_qbr = 40 * title_fs / 120
        self.buttons_distance = self.modebtn_dim[0] / 5
        title_padding_top = 30
        title = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.purple)
        title_bg = self.game.text_surface('ScribblAI', 'Ink Free', title_fs, Colors.pink)
        title_x = self.game.dim[0] // 2 - title.get_width() // 2

        subtitle = self.game.text_surface('Bist du besser als die KI?', 'Ink Free', title_fs / 4, Colors.purple)
        subtitle_x = self.game.dim[0] // 2 - subtitle.get_width() // 2
        subtitle_y = title.get_height() + title_padding_top

        self.game.draw(subtitle, (subtitle_x, subtitle_y))
        self.game.draw(pygame.transform.rotate(title_bg, self.rotate_bg / 120 * title_fs), (title_x, title_padding_top + title_fs/12))
        self.game.draw(pygame.transform.rotate(title, self.rotate_title / 120 * title_fs), (title_x, title_padding_top))

        modebtn_y = self.game.dim[1]/2 - self.modebtn_dim[1]/2
        modebtn1_x = self.game.dim[0]/2 - self.modebtn_dim[0] - self.buttons_distance/2 + self.modebtn_dim[0]/2 - self.modebtn1_dim[0]/2
        modebtn1_y = modebtn_y + self.modebtn_dim[1]/2 - self.modebtn1_dim[1]/2
        self.modebtn1 = self.game.create_btn((modebtn1_x, modebtn1_y), self.modebtn1_dim, Colors.purple, self.modebtn_radius, 'Mehrspieler', 'Arial', title_fs / 4, Colors.salmon)

        if self.multiplayer_info is not None:
            multiplayer_info_text = self.game.text_surface(self.multiplayer_info, 'Arial', title_fs / 8, Colors.salmon)
            info_dim = (multiplayer_info_text.get_width() + title_padding_top, multiplayer_info_text.get_height() * 1.5)
            info_pos = (title_fs / 10, self.game.dim[1] - info_dim[1] - title_fs / 10)
            self.game.create_btn(info_pos, info_dim, Colors.black, 10, self.multiplayer_info, 'Arial', title_fs / 8, Colors.white)
        
        modebtn2_x = self.game.dim[0]/2 + self.buttons_distance/2 + self.modebtn_dim[0]/2 - self.modebtn2_dim[0]/2
        modebtn2_y = modebtn_y + self.modebtn_dim[1]/2 - self.modebtn2_dim[1]/2
        self.modebtn2 = self.game.create_btn((modebtn2_x, modebtn2_y), self.modebtn2_dim, Colors.salmon, self.modebtn_radius, 'Sandkiste', 'Arial', title_fs / 4, Colors.purple)

        self.qbtn = pygame.Rect(self.game.dim[0] // 2 - self.qbr, self.game.dim[1] - (140 * title_fs / 120) - self.qbr, 2 * self.qbr, 2 * self.qbr)
        pygame.draw.circle(self.game.screen, Colors.pink, (self.qbtn.center), self.qbr)
        q_surface = self.game.text_surface('?', 'Arial', title_fs / 2, Colors.beige)
        self.game.draw(q_surface, (self.qbtn.center[0] - q_surface.get_width() // 2, self.qbtn.center[1] - q_surface.get_height() // 2))

        credits = self.game.text_surface('Ennio Binder 2024', 'Ink Free', title_fs / 6, Colors.purple)
        credits_x = self.game.dim[0] // 2 - credits.get_width() // 2
        self.game.draw(credits, (credits_x, self.game.dim[1] - credits.get_height() - 10))

    def iteration(self:any)->None:
        if self.modebtn1.collidepoint(self.mouse_pos):
            if self.modebtn1_hover.switch_true():
                self.modebtn1_dim = tuple([val * 1.05 for val in self.modebtn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.modebtn1_hover.switch_false():
            self.modebtn1_dim = self.modebtn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.modebtn2.collidepoint(self.mouse_pos):
            if self.modebtn2_hover.switch_true():
                self.modebtn2_dim = tuple([val * 1.05 for val in self.modebtn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.modebtn2_hover.switch_false():
            self.modebtn2_dim = self.modebtn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.qbtn.collidepoint(self.mouse_pos):
            if self.qb_hover.switch_true():
                self.qbr = self.base_qbr * 1.1
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.qb_hover.switch_false():
            self.qbr = self.base_qbr
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        if self.game.client is not None:
            if self.game.client.status is ClientStatus.CONNECTED and self.connect_thread is not None:
                self.multiplayer_info = 'Verbunden'
                self.connect_thread.join()
                self.game.goto_page('Lobby')
            elif self.game.client.status is ClientStatus.CONNECTING:
                self.multiplayer_info = 'Verbinde...'
            elif self.game.client.status is ClientStatus.ERROR:
                self.multiplayer_info = 'Verbindung fehlgeschlagen'

    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()
    
        if self.qb_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.goto_page('Info')
        
        if self.modebtn2_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.goto_page('Sandbox')

        if self.modebtn1_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.start_game()
        
        if event.type == pygame.VIDEORESIZE:
            self.qb_hover.switch_true()
            self.modebtn1_hover.switch_true()
            self.modebtn2_hover.switch_true()
    
    def start_game(self: any) -> None:
        self.game.client = Client('localhost', 1000, self.game.log)
        self.connect_thread = threading.Thread(target=self.game.client.start)
        self.connect_thread.start()