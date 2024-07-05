import math
import pygame
from utils.colors import Colors
from utils.canvas import Canvas
from pages.page import Page
from external.ai import AI
from utils.input import Input
import matplotlib.pyplot as plt
from external.image import image

class Sandbox(Page):
    rotate = pygame.USEREVENT + 1
    
    def on_init(self:any)->None:
        self.canvas = Canvas(self.game, self)
        self.ai = AI()
        self.text_input = Input(self.game, self)
    
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
        canvas_y = 75 * min_ratio + 2 * title_padding
        canvas_height = self.game.dim[1] - canvas_y - title_padding
        canvas_width = (self.game.dim[0] - 2 * title_padding) / 3 * 2
        canvas_size = min(canvas_width, canvas_height)
        self.canvas.draw((title_padding, canvas_y), (canvas_size, canvas_size), Colors.white)
        self.text_input.draw((title_padding + canvas_size * 0.5, canvas_y + canvas_size * 0.875 + title_padding / 2), canvas_size * 0.5 - title_padding, (title_padding / 2, title_padding / 2), 10)

        if hasattr(self, 'result'):
            y = canvas_y
            ys = []
            hs = []
            max_width = 0
            display_count = 5
            total = sum([guess['certainty'] for guess in self.result[:display_count]])
            relative_certainties = []

            for i in range(display_count):
                guess = self.result[i]
                percentage = round(guess['certainty'] * 100, 1)
                relative_certainties.append(guess['certainty'] / total)
                string = f'{guess["category"]} ({percentage}%)'
                font_size = 20
                text = self.game.text_surface(string, 'Arial', font_size, Colors.black)
                self.game.draw(text, (canvas_size + 2 * title_padding, y))
                height = font_size * 1.5
                hs.append(height)
                ys.append(y)
                y += height + title_padding
                max_width = max(len(string) * font_size * 0.35, max_width)

            width = self.game.dim[0] - (canvas_size + 2 * title_padding) - max_width - 2 * title_padding
            x = self.game.dim[0] - width

            for i, y in enumerate(ys):
                bar = pygame.Rect(x, y, width * relative_certainties[i], hs[i])
                pygame.draw.rect(self.game.screen, Colors.pink, bar)

    def iteration(self:any)->None:
        # Handle mouse clicks
        if self.btn.collidepoint(self.mouse_pos):
            if self.back_button_hover.switch_true():
                self.btn_dim = tuple([val * 1.05 for val in self.base_btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_button_hover.switch_false():
            self.btn_dim = self.base_btn_dim
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if self.canvas.ai_predict:
            self.canvas.ai_predict = False
            img_array = image.format_for_ai(self.canvas.grid)
            # präsentation
            # imgplot = plt.imshow(img_array, cmap='gray')
            # plt.show()

            self.result = self.ai.predictImage(img_array)
        
        self.canvas.iteration()

    def event_check(self:any, event:pygame.event)->None:
        if event.type == self.rotate:
            self.rotate_title *= -1
            self.rotate_bg *= -1
            self.trigger_update()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and len(self.text_input.manager.value.strip()):
            self.add_training_example()
        
        if self.back_button_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.goto_page('Menu')

        self.canvas.event_check(event)    
        self.text_input.event_check(event)  

        if event.type == pygame.VIDEORESIZE:
            self.back_button_hover.switch_true()
    
    def add_training_example(self:any)->None:
        img = image.format_for_ai(self.canvas.grid)        
        imgplot = plt.imshow(img, cmap='gray')
        plt.show()