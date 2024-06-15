import pygame
import os
from time import sleep
from typing import Optional
from pages.menu import Menu
from pages.info import Info
from pages.lobby import Lobby
from pages.enter_name import EnterName
from pages.sandbox import Sandbox

class Game():
    def __init__(self:any, dim:tuple[float]=(650, 550))->None:
        self.start_dim = self.dim = dim
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEMOTION, pygame.MOUSEWHEEL, pygame.MOUSEBUTTONDOWN, pygame.VIDEORESIZE, pygame.MOUSEBUTTONUP])
        flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.dim, flags)
        self.running = True
        pygame.display.set_caption('ScribblAI')
        logo = pygame.image.load('./assets/logo.png').convert_alpha()
        pygame.display.set_icon(logo)

        self.pages = {
            'Menu': Menu,
            'EnterName': EnterName,
            'Lobby': Lobby,
            'Sandbox': Sandbox,
            'Info': Info,
        }

        self.fonts = {
            'handwriting': pygame.font.SysFont('Ink Free', 120),
            'subtitle': pygame.font.SysFont('Ink Free', 30),
            'credits': pygame.font.SysFont('Ink Free', 20),
            'text': pygame.font.SysFont('Arial', 30),
        }

    def event_check(self:any, event:pygame.event)->None:
        if event.type == pygame.QUIT:
            self.running = False
        
        if event.type == pygame.VIDEORESIZE:
            self.dim = (event.w, event.h)
            self.page.trigger_update()

    def start(self:any)->None:
        self.goto_page('Menu')
        
    def goto_page(self:any, page:str)->None:
        if page not in self.pages:
            raise ValueError(f'Page {page} does not exist')

        self.pagename = page
        self.page = self.pages[page](self, self.pagename)
        self.page.start()

    def create_btn(self:any, pos:tuple[float], dim:tuple[float], color:tuple, bdrad:float=0, text:str='', font:Optional[str]=None, fontsize:Optional[int]=None, fontcolor:Optional[tuple|str]=None)->pygame.rect:
        btn = pygame.Rect(pos[0], pos[1], dim[0], dim[1])

        if bdrad != 0: 
            btn.inflate(-2 * bdrad, -2 * bdrad)
        
        pygame.draw.rect(self.screen, color, btn, border_radius=bdrad)

        if text != '':
            text_surface = self.text_surface(text, font, fontsize, fontcolor)
            self.draw(text_surface, (btn.x + btn.width // 2 - text_surface.get_width() // 2, btn.y + btn.height // 2 - text_surface.get_height() // 2))
        
        return btn
    
    def draw(self:any, surface:pygame.surface, pos:tuple[float])->None:
        self.screen.blit(surface, pos)
    
    def text_surface(self:any, text:str, fontname:str, size:float, color:tuple|str)->pygame.surface:
        font = pygame.font.SysFont(fontname, round(size))
        surface = font.render(text, True, color)
        return surface

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.start()
    # TODO: send disconnect if connected to server
    pygame.quit()
