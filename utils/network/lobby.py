import threading
from time import sleep, perf_counter
import socket
import json
from random import randint

class Lobby:
    players = []
    state = 'waiting'
    min_players = 2
    max_players = 10
    countdown_len = 60
    countdown = countdown_len

    def __init__(self:any, server:any, id:int, players:list[any])->None:
        self.id = id
        self.server = server

        for player in players:
            self.add_player(player)

        main = threading.Thread(target=self.main, args=())
        main.start()
    
    def remove_player(self:any, player:any)->None:
        if len(self.players) > player.id:
            self.players.pop(player.id)
            del player.id
            del player.lobby

    def add_player(self:any, player:any)->None:
        player.id = len(self.players)
        player.lobby = self
        self.players.append(player)
        print(f'Added player {player.id} to lobby {self.id}')

    def main(self:any)->None:
        while self.state == 'waiting':
            if len(self.players) == 0:
                self.state = 'stopped'

            if len(self.players) >= self.min_players:
                self.countdown -= 1

                if len(self.players) == self.max_players and self.countdown > 10:
                    self.countdown = 10

                if self.countdown == 0:
                    self.state = 'ready'
            else:
                self.countdown = 60
            
            sleep(1)
        
        if self.state == 'ready':
            self.players[randint(0, len(self.players))].role = 'drawer'
            self.state = 'game'
        
        while self.state == 'game':
            self.state = 'results'
        
        while self.state == 'results':
            self.state = 'stopped'
        
        self.close()
    
    def close(self:any)->None:
        for player in self.players:
            player.active = False
        
        self.server.lobbies.pop(self.id)
        print(f'Closed lobby {self.id}')
        exit()
            
class Player:
    active = True
    online = True
    role = 'guesser'
    name = 'Unknown'
    guess = ''
    max_wait_time = 1
    max_packets_lost = 5
    packets_lost = 0

    def __init__(self:any, conn:any, addr:str)->None:
        self.conn = conn
        self.addr = addr
        main = threading.Thread(target=self.main, args=())
        main.start()
    
    def transceive(self:any, packet:dict[str, any])->dict[str, any]|None:
        try:
            self.conn.settimeout(self.max_wait_time)
            self.conn.send(json.dumps(packet).encode())
            data = self.conn.recv(4096)

            if not data:
                self.packets_lost += 1
            else:
                self.packets_lost = 0
                reply = json.loads(data.decode('utf-8'))
                return reply
        except (ConnectionAbortedError, TimeoutError) as error:
            self.packets_lost += 1
        
        self.online = self.packets_lost == 0

        if self.packets_lost >= self.max_packets_lost:
            self.active = False
        
        return None

    def main(self:any)->None:
        print(f'Connected to player at address {self.addr}')

        while self.active:
            packet = {'mode': 'nolobby', 'lobby': {}, 'id': -1}

            if hasattr(self, 'id'):
                packet['mode'] = 'lobby'
                packet['id'] = self.id
                packet['lobby'] = {
                    'id': self.lobby.id,
                    'countdown': self.lobby.countdown,
                    'state': self.lobby.state,
                    'players': [{'name': player.name, 'id': player.id, 'active': player.active, 'online': player.online, 'role': player.role, 'guess': player.guess} for player in self.lobby.players]}

                reply = self.transceive(packet)
                print(f'Sent {str(packet)} to player {self.id} from lobby {self.lobby.id} at {self.addr}')

                if reply is not None:
                    print(f'Received {str(reply)} from player {self.id} in lobby {self.lobby.id} at {self.addr}')
            else:
                reply = self.transceive(packet)
                print(f'Sent {str(packet)} to player at {self.addr}')

                if reply is not None:
                    print(f'Received {str(reply)} from player {self.id} in lobby {self.lobby.id} at {self.addr}')

            sleep(1)
        
        self.disconnect()
    
    def disconnect(self:any)->None:
        if hasattr(self, 'id'):
            print(f'Disconnected player {self.id} from lobby {self.lobby.id}')
            self.lobby.remove_player(self)
        
        try:
            packet = {'mode': 'disconnected', 'lobby': {}}
            self.conn.send(json.dumps(packet).encode())
        except ConnectionAbortedError as error:
            pass

        self.conn.close()
        exit()
