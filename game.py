import pygame
import os
from time import sleep
from typing import Optional
from pages.menu import Menu
from pages.info import Info
from pages.lobby import Lobby
from pages.draw import Draw
from pages.guess import Guess
from pages.chat import Chat
from pages.result import Result
from external.definitions import create_logger
from pages.sandbox import Sandbox
import logging

class Game():
    def __init__(self:any, dim:tuple[float]=(650, 550))->None:
        self.start_dim = self.dim = dim
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEMOTION, pygame.MOUSEWHEEL, pygame.MOUSEBUTTONDOWN, pygame.VIDEORESIZE, pygame.MOUSEBUTTONUP])
        flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.dim, flags)
        self.running = True
        self.client = None
        self.page = None
        self.return_info = None
        self.log = create_logger('game.log', console_level=logging.ERROR)
        pygame.display.set_caption('ScribblAI')
        logo = pygame.image.load('./assets/logo.png').convert_alpha()
        pygame.display.set_icon(logo)

        self.pages = {
            'Menu': Menu,
            'Lobby': Lobby,
            'Sandbox': Sandbox,
            'Info': Info,
            'Draw': Draw,
            'Guess': Guess,
            'Chat': Chat,
            'Result': Result,
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

        if self.page is not None:
            self.page.leave()
        
        self.pagename = page
        self.page = self.pages[page](self, self.pagename)
        self.page.start()

    def create_btn(self:any, pos:tuple[float], dim:tuple[float], color:tuple, bdrad:float=0, text:str='', font:Optional[str]=None, fontsize:Optional[int]=None, fontcolor:Optional[tuple|str]=None, auto_fontsize: bool = False, padding_x: int = 0)->pygame.rect:
        btn = pygame.Rect(pos[0], pos[1], dim[0], dim[1])

        if bdrad != 0: 
            btn.inflate(-2 * bdrad, -2 * bdrad)
        
        pygame.draw.rect(self.screen, color, btn, border_radius=bdrad)

        if text != '':
            while True:
                text_surface = self.text_surface(text, font, fontsize, fontcolor)
                fontsize -= 1

                if not auto_fontsize or text_surface.get_width() <= dim[0] - 2 * padding_x or fontsize < 10:
                    break

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

    try:
        game.start()
    except KeyboardInterrupt:
        print('Game stopped by KeyboardInterrupt')

    if game.client is not None:
        game.client.disconnect()
    
    pygame.quit()
