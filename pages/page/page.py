import pygame
from utils.colors import Colors
from utils.eventbool import EventBool

class Page:
    # not for menu page
    rotate_title = 0.2
    rotate_bg = -0.2

    def __init__(self:any, game:any, pagename:str)->None:
        self.game = game
        self.name = pagename
        self.update = False
        self.back_button_hover = EventBool(self.trigger_update)
        self.on_init()
    
    def start(self:any)->None:
        self.on_start()
        self.draw()
        pygame.display.flip()

        while self.game.running and self.game.pagename == self.name:
            self.mouse_pos = pygame.mouse.get_pos()
            self.iteration()

            for event in pygame.event.get():
                self.game.event_check(event)
                self.event_check(event)

            if self.update:
                self.draw()
                pygame.display.flip()
                self.update = False  

    def draw(self:any)->None:
        if not hasattr(self, 'btn_dim'): self.btn_dim = (200, 100)
        self.game.screen.fill(Colors.beige)
        surface = self.game.text_surface(f'Page {self.name}', 'Ink Free', 100, Colors.purple)
        self.game.screen.blit(surface, (self.game.dim[0]/2 - surface.get_width()/2, self.game.dim[1]/2 - surface.get_height()/2))
        self.btn = self.game.create_btn((20, 20), self.btn_dim, Colors.salmon, 10, 'Zurück', 'Arial', 30, Colors.purple)     
    
    def on_init(self:any)->None:
        pass

    def event_check(self:any, event:pygame.event)->None:
        if self.back_button_hover.state and event.type == pygame.MOUSEBUTTONDOWN:
            self.game.goto_page('Menu')
    
    def trigger_update(self:any)->None:
        self.update = True
    
    def iteration(self:any)->None:
        self.btn_dim = (200, 100)

        if self.btn.collidepoint(self.mouse_pos):
            if self.back_button_hover.switch_true():
                self.btn_dim = tuple([val * 1.05 for val in self.btn_dim])
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif self.back_button_hover.switch_false():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def on_start(self:any)->None:
        pass
