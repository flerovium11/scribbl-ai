import socket
import threading
import sys
from time import sleep

class Network:
    def __init__(self:any, server:str='', port:int=5555, mode:str='server')->None:
        if mode not in ['server', 'client']:
            raise ValueError('Mode must be "server" or "client"!')
        
        self.server = server
        self.port = port
        self.running = True
        self.addr = (self.server, self.port)
        self.mode = mode
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.mode == 'server':
            try:
                self.s.bind((self.server, self.port))
            except socket.error as error:
                raise RuntimeError('Connection to server failed: ' + str(error))
            

    def start(self:any)->None:
        if self.mode == 'server':
            self.start_server()

        if self.mode == 'client':
            self.start_client()    
    
    def start_client(self:any)->None:
        self.id = self.connect()
        print(self.id) 
    
    def connect(self:any)->None:
        try:
            self.s.connect(self.addr)
            return self.s.recv(2048).decode()
        except Exception as error:
            raise RuntimeError('Connecting to server failed: ' + str(error))

        
    def start_server(self:any)->None:
        self.s.listen(2)
        listen = threading.Thread(target=self.listen, args=())
        listen.start()

        while True:
            try:
                sleep(1)
            except KeyboardInterrupt:
                print('Program stopped by KeyboardInterrupt')
                self.running = False

    def listen(self:any)->None:
        print('Server started, waiting for connection...')

        while self.running:
            conn, addr = self.s.accept()
            print('Connected to:', addr)
            client = threading.Thread(target=self.client, args=[conn])
            client.start()
    
    def client(self:any, conn)->None:
        conn.send(str.encode("Hello from the other siiiihiide"))
        reply = ''

        while self.running:
            try:
                data = conn.recv(2048)
                reply = data.decode('utf-8')

                if not data:
                    print('Disconnected')
                    break
                else:
                    print('Received: ' + reply)
                    print('Sending: ' + reply)
                    
                    conn.sendall(str.encode(reply))
            except Exception as error:
                print('Error while communication with client: ' + str(error))
                break
        
        conn.close()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Network test')
    parser.add_argument('--mode', action="store", dest='mode', default=0)
    args = parser.parse_args()
    server = Network(server='192.168.193.18', mode=args.mode)
    server.start()

