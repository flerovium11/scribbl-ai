import pygame
from utils.colors import Colors
from external.definitions import PlayerRole

class PlayerList:
    def __init__(self:any, game:any)->None:
        self.game = game

    def draw(self: any, 
             pos: tuple[float], 
             dim: tuple[float],
             bdrad: float,
             players: list[any], 
             player_id: int,
             player_bdrad: float,
             player_max_height: float,
             padding: tuple[float], 
             row_gap: float, 
             bg_color: Colors = Colors.white, 
             player_bg: Colors = Colors.beige,
             player_inactive_bg: Colors = Colors.gray, 
             text_color: Colors = Colors.black,
            ) -> None:
        
        self.rect = pygame.Rect(pos[0], pos[1], dim[0], dim[1])
        self.rect.inflate(-2 * bdrad, -2 * bdrad)
        pygame.draw.rect(self.game.screen, bg_color, self.rect, border_radius=bdrad)

        player_dim = (dim[0] - 2 * padding[0], min(player_max_height, dim[1] / len(players) - len(players) * row_gap - 2 * padding[1]))

        for i, player in enumerate(players):
            player_rect = pygame.Rect(pos[0] + padding[0], pos[1] + padding[1] + i * (player_dim[1] + row_gap), player_dim[0], player_dim[1])
            player_rect.inflate(-2 * bdrad, -2 * bdrad) 
            pygame.draw.rect(self.game.screen, player_bg if player['active'] else player_inactive_bg, player_rect, border_radius=bdrad)
            player_name = player['name'] if player['name'] is not None else 'Unknown'

            if player['role'] is not None:
                add_symbol = '✎' if player['role'] == PlayerRole.DRAWER.name else '🗭' if not player['has_guessed'] else '✔'
                player_name = f'{add_symbol} {player_name}'

            if i == player_id:
                player_name += ' (You)'

            text = self.game.text_surface(player_name, 'Segoe UI Symbol', player_dim[1] / 2, text_color)
            self.game.draw(text, (player_rect.x + padding[0], player_rect.y + player_rect.height // 2 - text.get_height() // 2))

            status = 'Ⓧ' if not player['active'] else u'⬤'
            status_color = Colors.red if not player['active'] else Colors.pink if player['online'] else Colors.gray
            status_text = self.game.text_surface(status, 'Segoe UI Symbol', player_dim[1] / 2, status_color)
            self.game.draw(status_text, (player_rect.x + player_rect.width - padding[0] * 1.5, player_rect.y + player_rect.height // 2 - status_text.get_height() // 2))
        
