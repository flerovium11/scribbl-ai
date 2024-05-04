import threading
from time import sleep, perf_counter
import json
from random import randint

class Lobby:
    players = []
    state = 'waiting'
    min_players = 2
    max_players = 10
    countdown_len = 60
    countdown = countdown_len

    def __init__(self:any, id:int)->None:
        self.id = id
        main = threading.Thread(target=self.main, args=())
        main.start()
    
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
            self.state == 'stopped'

            

class Player:
    active = False
    online = False
    role = 'guesser'
    max_wait_time = 1000
    max_lost_kick = 10

    def __init__(self:any, conn:any)->None:
        self.conn = conn
        main = threading.Thread(target=self.main, args=())
        main.start()
    
    def main(self:any)->None:
        while self.active:
            packet = {'mode': 'nolobby', 'lobby': {}}

            if hasattr(self, 'lobby'):
                pass
            else:
                pass

            self.conn.send(json.dumps(packet).encode())
            sleep(1)



        



        

