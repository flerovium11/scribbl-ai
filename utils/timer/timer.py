import pygame
from math import pi as cake
from utils.colors import Colors


class Timer:
    @staticmethod
    def draw(game: any, pos: tuple[int], rad: int, color: Colors, font_color: Colors, state: int, max: int):
        arc_rect = pygame.Rect(*pos, rad*2, rad*2)
        pygame.draw.arc(game.screen, color, arc_rect, 0.5 * cake,
                        0.5 * cake + 2 * cake * state / max, round(rad))
        text = game.text_surface(str(round(state)), 'Arial', rad, font_color)
        game.draw(text, (pos[0] + rad - text.get_width() //
                  2, pos[1] + rad - text.get_height() // 2))
