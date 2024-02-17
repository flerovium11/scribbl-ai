import pygame
from components.colors import Colors
from components.page import Page

class Menu(Page):
    title_text = 'ScribblAI'
    subtitle_text = 'Bist du besser als die KI?'
    gamemode_text1 = 'Mehrspieler'
    gamemode_text2 = 'Sandkiste'
    credits_text = 'Ennio Binder 2024'
    modebtn_radius = 10
    buttons_distance = 50
    question_button_radius = qbr = 40
    rotate_title = 0.1
    rotate_bg = -0.1
    rotate = pygame.USEREVENT + 1
    modebtn_dim = modebtn1_dim = modebtn2_dim = (240, 140)
    
    def on_init(self:any)->None:
        self.fonts = {
            'handwriting': pygame.font.SysFont('Ink Free', 120),
            'subtitle': pygame.font.SysFont('Ink Free', 30),
            'credits': pygame.font.SysFont('Ink Free', 20),
            'text': pygame.font.SysFont('Arial', 30),
        }
    
    def on_start(self:any)->None:
        pygame.time.set_timer(self.rotate, 500)

    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)

        title_fs = round(min(180, self.game.dim[0] / 5.416))
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

        modebtn_y = subtitle_y + subtitle.get_height() * 2
        modebtn1_x = self.game.dim[0]/2 - self.modebtn_dim[0] - self.buttons_distance/2 + self.modebtn_dim[0]/2 - self.modebtn1_dim[0]/2
        modebtn1_y = modebtn_y + self.modebtn_dim[1]/2 - self.modebtn1_dim[1]/2
        self.modebtn1 = self.game.create_btn((modebtn1_x, modebtn1_y), self.modebtn1_dim, Colors.purple, self.modebtn_radius, 'Mehrspieler', 'Arial', 30, Colors.salmon)
        
        modebtn2_x = self.game.dim[0]/2 + self.buttons_distance/2 + self.modebtn_dim[0]/2 - self.modebtn2_dim[0]/2
        modebtn2_y = modebtn_y + self.modebtn_dim[1]/2 - self.modebtn2_dim[1]/2
        self.modebtn2 = self.game.create_btn((modebtn2_x, modebtn2_y), self.modebtn2_dim, Colors.salmon, self.modebtn_radius, 'Sandkiste', 'Arial', 30, Colors.purple)

        self.qbtn = pygame.Rect(self.game.dim[0] // 2 - self.qbr, self.game.dim[1] - 140 - self.qbr, 2 * self.qbr, 2 * self.qbr)
        pygame.draw.circle(self.game.screen, Colors.pink, (self.qbtn.center), self.qbr)
        q_surface = self.game.text_surface('?', 'Arial', 60, Colors.beige)
        self.game.draw(q_surface, (self.qbtn.center[0] - q_surface.get_width() // 2, self.qbtn.center[1] - q_surface.get_height() // 2))

        credits = self.game.text_surface('Ennio Binder 2024', 'Ink Free', title_fs / 6, Colors.purple)
        credits_x = self.game.dim[0] // 2 - credits.get_width() // 2
        self.game.draw(credits, (credits_x, self.game.dim[1] - credits.get_height() - 10))

    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
        
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Handle mouse clicks
        if self.modebtn1.collidepoint(mouse_pos):
            self.modebtn1_dim = tuple([val * 1.05 for val in self.modebtn_dim])
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            if event.type == pygame.MOUSEBUTTONDOWN:
                print('Button 1 clicked')
        else:
            self.modebtn1_dim = self.modebtn_dim

        if self.modebtn2.collidepoint(mouse_pos):
            self.modebtn2_dim = tuple([val * 1.05 for val in self.modebtn_dim])
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('Button 2 clicked')
        else:
            self.modebtn2_dim = self.modebtn_dim

        if self.qbtn.collidepoint(mouse_pos):
            self.qbr = self.question_button_radius * 1.1
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('Question mark button clicked')
        else:
            self.qbr = self.question_button_radius
