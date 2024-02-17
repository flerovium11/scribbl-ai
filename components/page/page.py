import pygame
import sys
from components.colors import Colors

class Page:
    def __init__(self:any, game:any, pagename:str)->None:
        self.game = game
        self.name = pagename
        self.on_init()
    
    def start(self:any)->None:
        self.on_start()

        while self.game.running and self.game.pagename == self.name:
            self.draw()

            for event in pygame.event.get():
                self.game.event_check(event)
                self.event_check(event)
            
            pygame.display.flip()

    def draw(self:any)->None:
        self.game.screen.fill(Colors.beige)
        surface = self.game.text_surface(f'Page {self.name}', 'Ink Free', 100, Colors.purple)
        self.game.screen.blit(surface, (self.game.dim[0]/2 - surface.get_width()/2, self.game.dim[1]/2 - surface.get_height()/2))
    
    def on_init(self:any)->None:
        pass

    def event_check(self:any, event:pygame.event)->None:
        pass

    def on_start(self:any)->None:
        pass
