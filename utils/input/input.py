
from pages.page import Page
from ..colors import Colors
import pygame_textinput
import pygame

class Input:
    def __init__(self:any, game:any, page:Page, color:Colors=Colors.white, font_size:int=20, font_color:Colors=Colors.black, font:str='Arial')->None:
        self.page = page
        self.game = game
        self.color = color
        self.font_size = font_size
        self.font_color = font_color
        self.font = font

        def validate(input:str)->bool:
            test = self.game.text_surface(input, self.font, self.font_size, Colors.black)
            self.page.trigger_update()
            return (test.get_width() <= self.rect.width - 2 * self.padding[0]) if hasattr(self, 'rect') else True

        self.manager = pygame_textinput.TextInputManager(validator=validate)
        
    def draw(self:any, pos:tuple[float], width:float, padding:tuple[float], bdrad:float)->None:
        self.padding = padding
        self.text_surface = self.game.text_surface(self.manager.value[:self.manager.cursor_pos] + ('|' if pygame.time.get_ticks() % 1000 < 500 else '') + self.manager.value[self.manager.cursor_pos:], self.font, self.font_size, Colors.black)
        self.rect = pygame.Rect(pos[0], pos[1], width + 2 * padding[0], self.text_surface.get_height() + 2 * padding[1])
        self.bdrad = bdrad
        self.rect.inflate(-2 * bdrad, -2 * bdrad)
        pygame.draw.rect(self.game.screen, self.color, self.rect, border_radius=bdrad)
        self.game.draw(self.text_surface, (pos[0] + padding[0], pos[1] + padding[1]))
    
    def event_check(self:any, event:any)->None:
        self.manager.update([event])
