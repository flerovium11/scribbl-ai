import socket
import threading
import sys
import json
from time import sleep
from lobby import Lobby, Player
from functools import cmp_to_key

class Server:
    running = True
    lobbies = []

    def __init__(self:any, server:str='', port:int=5555)->None: 
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.s.bind((self.server, self.port))
        except socket.error as error:
            raise RuntimeError('Connection to server failed: ' + str(error)) 
    
    def start_client(self:any)->None:
        self.connect()
        while self.running:
            data = self.s.recv(4096)
            reply = data.decode('utf-8')
            print(reply)

    def start(self:any)->None:
        self.s.listen(2)
        listen = threading.Thread(target=self.listen, args=())
        listen.start()

        while self.running:
            try:
                sleep(1)
            except KeyboardInterrupt:
                print('Program stopped by KeyboardInterrupt')
                self.turn_off_server()
    
    def turn_off_server(self:any)->None:
        self.running = False

        for lobby in self.lobbies:
            lobby.state = 'stopped'

        self.s.close()
        exit()

    def listen(self:any)->None:
        print('Server started, waiting for connection...')

        while self.running:
            try:
                conn, addr = self.s.accept()
                sorted_lobbies = sorted(self.lobbies, key=cmp_to_key(lambda lobby1, lobby2: len(lobby1.players) - len(lobby2.players)))
                open_lobbies = list(filter(lambda lobby: lobby.state == 'waiting' and lobby.players < lobby.max_players, sorted_lobbies))
                
                player = Player(conn, addr)

                if len(open_lobbies) > 0:
                    lobby = open_lobbies[0]
                    lobby.add_player(player)
                else:
                    lobby = Lobby(self, len(self.lobbies), [player])
                    self.lobbies.append(lobby)
            except IOError as error:
                print('Socket accept aborted')
            
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Network test')
    parser.add_argument('--mode', action="store", dest='mode', default=0)
    args = parser.parse_args()
    server = Network(server='localhost', mode=args.mode)
    server.start()

class Client:
    active = True
    online = True
    role = 'guesser'
    max_wait_time = 2
    max_packets_lost = 10
    packets_lost = 0

    def __init__(self:any, server:str='', port:int=5555)->None:
        self.conn = conn
        self.addr = addr
        main = threading.Thread(target=self.main, args=())
        main.start()
    
    def connect(self:any)->None:
        try:
            self.s.connect(self.addr)
        except Exception as error:
            raise RuntimeError('Connecting to server failed: ' + str(error))

    def main(self:any)->None:
        print(f'Player client active at address {self.addr}')

        while self.active:
            try:
                self.conn.settimeout(self.max_wait_time)
                data = self.conn.recv(4096)

                if not data:
                    self.packets_lost += 1
                else:
                    self.packets_lost = 0
                    packet = json.loads(data.decode('utf-8'))
                    reply = {}
                    self.conn.send(json.dumps(reply).encode())
            except (ConnectionAbortedError, TimeoutError) as error:
                self.packets_lost += 1
            
            self.online = self.packets_lost == 0

            if self.packets_lost >= self.max_packets_lost:
                self.active = False
            
            sleep(1)
        
        self.disconnect()
    
    def disconnect(self:any)->None:
        print(f'Disconnected client from address {self.addr}')
        self.online = self.active = False
        self.conn.close()
        exit()