import socket
import threading
import json
from time import sleep
import sys
sys.path.append('../..')
from external.definitions import LobbyState, PlayerRole, create_logger, EXTERNAL_DIR
import os
from enum import Enum, auto
from dotenv import load_dotenv

env_path = os.path.join(EXTERNAL_DIR, '.env')

class ClientStatus(Enum):
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTED = auto()
    ERROR = auto()

class Client:
    def __init__(self:any, host:str='', port:int=5555, log:any=None, name:str='Unknown', on_receive:callable=lambda: None)->None:
        try:
            load_dotenv(env_path)
            self.max_wait_time = float(os.getenv('CLIENT_MAX_WAIT_TIME'))
            self.max_packets_lost = int(os.getenv('CLIENT_MAX_PACKETS_LOST'))
        except (KeyError, TypeError, ValueError) as error:
            if log is not None:
                log.exception(F'Environment variables wrong or missing in {env_path}')
            
            exit()
        
        self.active = True
        self.online = True
        self.status = ClientStatus.CONNECTING
        self.packets_lost = 0
        # info should never be changed by the client
        self.info = {}
        self.name = name
        self.guess = ''
        self.has_guessed = False
        self.grid = None # {'tiles': float[][], 'dim': int[]}
        self.word_index = None
        # self.grid = {'tiles': [[1,2],[1,3]], 'dim': (1,2)} TODO: remove this for production
        self.host = host
        self.port = port
        self.log = log
        self.on_receive = on_receive         
        self.addr = (self.host, self.port)
        self.addr_str = f'{self.host}:{self.port}'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.max_wait_time)
    
    def start(self:any)->None:
        self.connect()
        self.client_thread = threading.Thread(target=self.main, args=())
        self.client_thread.start()

        if __name__ == '__main__':
            while self.active:
                try:
                    sleep(1)
                except KeyboardInterrupt:
                    if self.log is not None:
                        self.log.info('Program stopped by KeyboardInterrupt')
                    
                    self.active = False
            
            if self.client_thread.is_alive():
                self.client_thread.join()
            
            self.disconnect()
    
    def connect(self:any)->None:
        try:
            self.s.connect(self.addr)
            self.status = ClientStatus.CONNECTED
        except socket.error as error:
            if self.log is not None:
                self.log.exception('Connection to server failed')
            
            self.active = self.online = False
            self.status = ClientStatus.ERROR
            exit()

    def main(self:any)->None:
        if self.log is not None:
            self.log.info(f'Player client connected at {self.addr_str}')

        while self.active:
            try:
                data = self.s.recv(4096)

                if not data:
                    self.lose_packet()
                else:
                    self.packets_lost = 0
                    packet = json.loads(data.decode('utf-8'))

                    if packet['mode'] == LobbyState.DISCONNECTED.name:
                        self.disconnect()
                    
                    self.info = packet
                    self.on_receive()
                    reply = {'name': self.name, 'guess': self.guess, 'has_guessed': self.has_guessed}

                    if 'id' in self.info:
                        if self.info['lobby']['players'][self.info['id']]['role'] == PlayerRole.DRAWER.name:
                            reply['grid'] = self.grid
                            reply['word_index'] = self.word_index
                        
                        if self.log is not None:
                            self.log.info(f'Received {str(packet)} from server - client {self.info["id"]} in lobby {self.info["lobby"]["id"]} at {self.addr_str}')
                    else:
                        if self.log is not None:
                            self.log.info(f'Received {str(packet)} from server - client at {self.addr_str}')
                    
                    self.s.send(json.dumps(reply).encode())

                    if 'id' in self.info:
                        if self.log is not None:
                            self.log.info(f'Sent {str(reply)} to server from client {self.info["id"]} in lobby {self.info["lobby"]["id"]} at {self.addr_str}')
                    else:
                        if self.log is not None:
                            self.log.info(f'Sent {str(reply)} to server from client at {self.addr_str}')
            except (ConnectionAbortedError, TimeoutError) as error:
                if self.log is not None:
                    self.log.exception('Network problem')
                
                self.lose_packet()
            except json.JSONDecodeError as error:
                if self.log is not None:
                    self.log.exception('Invalid JSON syntax')
                
                self.lose_packet()
            except KeyError as error:
                if self.log is not None:
                    self.log.exception('Received data missing key')
            except OSError as error:
                if self.log is not None:
                    self.log.info('Data receiving aborted')
                
                exit()
            
            self.online = self.packets_lost == 0

            if self.packets_lost >= self.max_packets_lost:
                self.active = False
            
            sleep(0.5)
                        
    def lose_packet(self:any)->None:
        self.packets_lost += 1

        if 'id' in self.info:
            if self.log is not None:
                self.log.warning(f'Lost packet ({self.packets_lost}/{self.max_packets_lost}) - client {self.info["id"]} in lobby {self.info["lobby"]["id"]} at {self.addr_str}')
        else:
            if self.log is not None:
                self.log.warning(f'Lost packet ({self.packets_lost}/{self.max_packets_lost}) - client at {self.addr_str}')

    def disconnect(self:any)->None:
        if self.log is not None:
            if 'id' in self.info:
                self.log.info(f'Disconnected client {self.info["id"]} from lobby {self.info["lobby"]["id"]} at {self.addr_str}')
            else:
                self.log.info(f'Disconnected client from server at {self.addr_str}')
        
        leave_message = {'disconnect': True}

        try:
            # wait for server to send packet and answer with leave_message
            self.s.recv(4096)
            self.s.send(json.dumps(leave_message).encode())
        except Exception as error:
            pass
            
        self.online = self.active = False
        self.s.close()
        self.status = ClientStatus.DISCONNECTED

if __name__ == '__main__':
    logger = create_logger('client.log')
    client_count = 2
    clients = []

    for i in range(client_count):
        client = Client(host='localhost', port=1000, log=logger)
        client_thread = threading.Thread(target=client.start, args=())
        client_thread.start()
        clients.append(client)
        sleep(0.5)
    
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            for client in clients:
                client.disconnect()
            
            break
