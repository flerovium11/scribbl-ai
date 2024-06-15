from enum import Enum
import socket
import os
import logging
import threading
import json
from time import sleep
from functools import cmp_to_key
import sys
sys.path.append('../..')
from external.ai import AI, german_categories
from external.definitions import create_logger, LobbyState, PlayerRole, EXTERNAL_DIR
from random import randint, shuffle
from dotenv import load_dotenv

env_path = os.path.join(EXTERNAL_DIR, '.env')

class Lobby:
    def __init__(self:any, server:any, id:int, players:list[any], log:any=None)->None:
        try:
            load_dotenv(env_path)
            self.min_players = int(os.getenv('LOBBY_MIN_PLAYERS'))
            self.max_players = int(os.getenv('LOBBY_MAX_PLAYERS'))
            self.choose_word_time = float(os.getenv('LOBBY_CHOOSE_WORD_TIME'))
            self.choose_word_count = int(os.getenv('LOBBY_CHOOSE_WORD_COUNT'))
            self.lobby_wait_time = float(os.getenv('LOBBY_WAIT_TIME'))
            self.min_lobby_wait_time = float(os.getenv('LOBBY_MIN_WAIT_TIME'))
            self.draw_time = float(os.getenv('LOBBY_DRAW_TIME'))
            self.model_path = os.getenv('LOBBY_MODEL_PATH')

            if self.model_path is None:
                raise KeyError()
        except (KeyError, TypeError, ValueError) as error:
            if log is not None:
                log.exception(F'Environment variables wrong or missing in {env_path}')
            
            exit()

        self.id = id
        self.server = server
        self.players = []
        self.state = LobbyState.WAITING
        self.countdown = self.lobby_wait_time
        self.log = log
        self.ai_guess = None
        self.grid = None
        self.word = None
        self.model = AI(model_path=self.model_path)
        self.all_words = german_categories[:]
        shuffle(self.all_words)
        self.words = self.all_words[:self.choose_word_count]

        for player in players:
            self.add_player(player)

        self.lobby_thread = threading.Thread(target=self.main, args=())
        self.lobby_thread.start()
    
    def remove_player(self:any, player:any)->None:
        if self.state in [LobbyState.WAITING, LobbyState.READY] and len(self.players) > player.id: # players are not removed from the player list during game and results
            self.players.pop(player.id)

            for p in self.players[player.id:]:
                p.id -= 1

            del player.id
            del player.lobby

    def add_player(self:any, player:any)->None:
        player.id = len(self.players)
        player.lobby = self
        self.players.append(player)

        if self.log is not None:
            self.log.info(f'Added player {player.id} to lobby {self.id}')

    def main(self:any)->None:
        while self.state is LobbyState.WAITING:
            try:
                if len(self.players) == 0:
                    self.state = LobbyState.STOPPED

                if len(self.players) >= self.min_players:
                    self.countdown -= 1

                    if len(self.players) == self.max_players and self.countdown > 10:
                        self.countdown = self.min_lobby_wait_time

                    if self.countdown == 0:
                        self.state = LobbyState.READY
                else:
                    self.countdown = self.lobby_wait_time
                
                sleep(1)
            except Exception:
                if self.log is not None:
                    self.log.exception('Unexpected error in lobby waiting loop')
                
                self.state = LobbyState.STOPPED
        
        if self.state is LobbyState.READY:
            try:
                sleep(2) # for suspense
                
                if len(self.players) == 0:
                    self.state = LobbyState.STOPPED
                
                # check if lobby hasn't been killed yet by higher force
                if self.state is LobbyState.READY:
                    drawer_index = randint(0, len(self.players) - 1)

                    for i, player in enumerate(self.players):
                        player.role = PlayerRole.GUESSER if i != drawer_index else PlayerRole.DRAWER
                    
                    self.state = LobbyState.CHOOSE_WORD
                    self.countdown = self.choose_word_time
            except Exception:
                if self.log is not None:
                    self.log.exception('Unexpected error in lobby ready loop')
                
                self.state = LobbyState.STOPPED
        
        while self.state is LobbyState.CHOOSE_WORD:
            try:
                if self.countdown == 0:
                    self.word = self.words[randint(0, len(self.words) - 1)]

                if len(self.players) == 0:
                    self.state = LobbyState.STOPPED
                
                if self.word is not None:
                    self.countdown = self.draw_time
                    self.state = LobbyState.GAME
                
                self.countdown -= 1
                sleep(1)
            except Exception:
                if self.log is not None:
                    self.log.exception('Unexpected error in lobby choose word loop')
                
                self.state = LobbyState.STOPPED
        
        while self.state is LobbyState.GAME:
            try:
                self.countdown -= 1

                # disconnected players during the game are not removed from the list but just set to inactive
                if not any([player.active for player in self.players]):
                    self.state = LobbyState.STOPPED
                
                if self.countdown == 0 or all([player.has_guessed or player.role is PlayerRole.DRAWER for player in self.players]):
                    self.state = LobbyState.RESULTS
                
                sleep(1)
            except Exception:
                if self.log is not None:
                    self.log.exception('Unexpected error in lobby game loop')
                
                self.state = LobbyState.STOPPED
        
        while self.state is LobbyState.RESULTS:
            self.state = LobbyState.STOPPED
        
        self.close()
    
    def close(self:any)->None:
        self.server.close_lobby(self)
        exit()
            
class Player:
    def __init__(self:any, conn:any, addr:str, role:PlayerRole=None, name:str='Unknown', log:any=None)->None:
        try:
            load_dotenv(env_path)
            self.max_packets_lost = int(os.getenv('PLAYER_MAX_PACKETS_LOST'))
            self.max_wait_time = float(os.getenv('PLAYER_MAX_WAIT_TIME'))
        except (KeyError, TypeError, ValueError) as error:
            if log is not None:
                log.exception(F'Environment variables wrong or missing in {env_path}')
            
            exit()
        
        self.active = True
        self.online = True
        self.role = role
        self.name = name
        self.log = log
        self.guess = ''
        self.has_guessed = False
        self.packets_lost = 0
        self.conn = conn
        self.addr = addr
        self.addr_str = f'{self.conn.getsockname()[0]}:{self.conn.getsockname()[1]}' # getpeername()?

        self.player_thread = threading.Thread(target=self.main, args=())
        self.player_thread.start()
    
    def transceive(self:any, packet:dict[str, any])->dict[str, any]|None:
        try:
            self.conn.settimeout(self.max_wait_time)
            self.conn.send(json.dumps(packet).encode())
            data = self.conn.recv(4096)

            if not data:
                self.lose_packet()
            else:
                self.packets_lost = 0
                reply = json.loads(data.decode('utf-8'))
                return reply
        except ConnectionResetError as error:
            # no log here because error is expected when client leaves and warning will be displayed by lose_packet() anyway
            self.lose_packet()
        except (ConnectionError, TimeoutError) as error:
            # the rest of exceptions are unexpected
            if self.log is not None:
                self.log.exception('Connection to client failed.!')
            
            self.lose_packet()
        except json.JSONDecodeError as error:
            if self.log is not None:
                self.log.exception('Invalid JSON syntax')
            
            self.lose_packet()
    
        return None

    def lose_packet(self:any)->None:
        self.packets_lost += 1
        self.online = False

        if self.log is not None:
            if hasattr(self, 'id'):
                self.log.warning(f'Lost package from player {self.id} in lobby {self.lobby.id} at {self.addr_str} ({self.packets_lost}/{self.max_packets_lost})')
            else:
                self.log.warning(f'Lost package from player at {self.addr_str} ({self.packets_lost}/{self.max_packets_lost})')

        if self.packets_lost >= self.max_packets_lost:
            self.active = False

            if hasattr(self, 'id'):
                if self.log is not None:
                    self.log.warning(f'Player {self.id} in lobby {self.lobby.id} at {self.addr_str} disconnected due to max package loss ({self.max_packets_lost})')
            else:
                if self.log is not None:
                    self.log.warning(f'Player at {self.addr_str} disconnected due to max package loss ({self.max_packets_lost})')
        
    def main(self:any)->None:
        self.log.info(f'Connected to player at {self.addr_str}')

        while self.active:
            packet = {'mode': 'nolobby'}

            if hasattr(self, 'id'):
                packet['mode'] = 'lobby'
                packet['id'] = self.id
                packet['lobby'] = {
                    'id': self.lobby.id,
                    'draw_time': self.lobby.draw_time,
                    'lobby_wait_time': self.lobby.lobby_wait_time,
                    'min_lobby_wait_time': self.lobby.min_lobby_wait_time,
                    'words': self.lobby.words,
                    'word': self.lobby.word,
                    'choose_word_time': self.lobby.choose_word_time,
                    'min_players': self.lobby.min_players,
                    'max_players': self.lobby.max_players,
                    'countdown': self.lobby.countdown,
                    'state': self.lobby.state.name,
                    'grid': self.lobby.grid,
                    'ai_guess': self.lobby.ai_guess,
                    'players': [{
                            'name': player.name,
                            'id': player.id,
                            'active': player.active,
                            'online': player.online,
                            'role': player.role.name if player.role is not None else None,
                            'guess': player.guess,
                            'has_guessed': player.has_guessed
                        } for player in self.lobby.players]}

            reply = self.transceive(packet)

            if self.log is not None:
                if hasattr(self, 'id'):
                    self.log.info(f'Sent {str(packet)} to player {self.id} in lobby {self.lobby.id} at {self.addr_str}')
                else:
                    self.log.info(f'Sent {str(packet)} to player at {self.addr_str}')

            if reply is not None:
                try:
                    if 'disconnect' in reply:
                        if self.log is not None:
                            self.log.info(f'Received disconnect from player at {self.addr_str}')
                        
                        self.disconnect()

                    if hasattr(self, 'id'):
                        if self.log is not None:
                            self.log.info(f'Received {str(reply)} from player {self.id} in lobby {self.lobby.id} at {self.addr_str}')
                        
                        self.name = reply['name']
                        self.guess = reply['guess']
                        self.has_guessed = reply['has_guessed']

                        if self.role is PlayerRole.DRAWER:
                            self.lobby.grid = reply['grid'] if 'grid' in reply else None

                            if self.lobby.word is None and reply['word_index'] is not None:
                                self.lobby.word = self.lobby.words[reply['word_index']]
                    else:
                        if self.log is not None:
                            self.log.info(f'Received {str(reply)} from player at {self.addr_str}')
                except KeyError as error:
                    if self.log is not None:
                        self.log.exception('Received data missing key')
                    
                    self.lose_packet()

            sleep(0.5)
        
        self.disconnect()
    
    def disconnect(self:any)->None:
        if hasattr(self, 'id'):
            if self.log is not None:
                self.log.info(f'Disconnected player {self.id} from lobby {self.lobby.id} at {self.addr_str}')

            self.lobby.remove_player(self)
        
        self.online = self.active = False
        
        try:
            packet = {'mode': LobbyState.DISCONNECTED.name}
            self.conn.settimeout(self.max_wait_time)
            self.conn.send(json.dumps(packet).encode())
        except (ConnectionError, TimeoutError) as error:
            pass

        self.conn.close()
        exit()

class Server:
    def __init__(self:any, host:str='', port:int=5555, log:any=None)->None: 
        self.lobbies = []
        self.running = True
        self.host = host
        self.port = port
        self.log = log
        self.addr = (self.host, self.port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.s.bind((self.host, self.port))
        except socket.error as error:
            if self.log is not None:
                self.log.exception('Socket binding failed')
            
            raise RuntimeError('Socket binding failed: ' + str(error))

    def start(self:any)->None:
        self.s.listen(2)
        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.listen_thread.start()

        while self.running:
            try:
                sleep(1)
            except KeyboardInterrupt:
                if self.log is not None:
                    self.log.info('Program stopped by KeyboardInterrupt')
                
                self.turn_off_server()
    
    def close_lobby(self:any, lobby:any)->None:
        for player in lobby.players:
            player.active = False
        
        lobby.state = LobbyState.STOPPED
        self.lobbies.pop(lobby.id)

        for l in self.lobbies[lobby.id:]:
            l.id -= 1

        if self.log is not None:
            self.log.info(f'Closing lobby {lobby.id}')
        
    def turn_off_server(self:any)->None:
        self.running = False

        for lobby in self.lobbies:
            lobby.state = LobbyState.STOPPED

        self.s.close()
        self.listen_thread.join()
        exit()

    def listen(self:any)->None:
        if self.log is not None:
            self.log.info(f'Server started at {self.addr[0]}:{self.addr[1]}, waiting for connection...')

        while self.running:
            try:
                conn, addr = self.s.accept()
                sorted_lobbies = sorted(self.lobbies, key=cmp_to_key(lambda lobby1, lobby2: len(lobby1.players) - len(lobby2.players)))
                open_lobbies = list(filter(lambda lobby: lobby.state == LobbyState.WAITING and len(lobby.players) < lobby.max_players, sorted_lobbies))
                player = Player(conn, addr, log=self.log)

                if len(open_lobbies) > 0:
                    lobby = open_lobbies[0]
                    lobby.add_player(player)
                else:
                    lobby = Lobby(self, len(self.lobbies), [player], log=self.log)
                    self.lobbies.append(lobby)
            except IOError as error:
                if self.log is not None:
                    self.log.info('Socket accept aborted')

if __name__ == '__main__':
    logger = create_logger('server.log')
    server = Server(host='localhost', port=1000, log=logger)
    server.start()