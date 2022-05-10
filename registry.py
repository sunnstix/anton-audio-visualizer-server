import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import logging

class Registry:
    HEARTBEAT = 60
    def __init__(self, host, port) -> None:
        self.clients = set()
        self.clLock = threading.Lock()
        threading.Thread(target=self.__registration__, args=(host, port,)).start()
        threading.Thread(target=self.__heartbeat__, args=()).start()
        self.logger = logging.getLogger(__name__)

    def __registration__(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            while True:
                # establish connection with client
                c, addr = s.accept()
                
                # lock acquired by client
                self.clLock.acquire()
                self.clients.add(Registry.Client(c, addr))
                self.clLock.release()
                
    def __heartbeat__(self):
        def check_conn(client: Registry.Client):
            if self.is_socket_closed(client.conn):
                client.tick()
            else:
                client.reset()
                
        while True:
            self.clLock.acquire()
                    
            with ThreadPoolExecutor() as executor:
                [executor.submit(check_conn, client) for client in self.clients]
            
            client: Registry.Client
            new_clients = self.clients.copy()
            for client in self.clients:
                if client.boom():
                    client.conn.close()
                    new_clients.remove(client)
                    
            self.clients = new_clients
            self.clLock.release()
            time.sleep(Registry.HEARTBEAT)

    def broadcast(self, msg:str):
        self.clLock.acquire()
        self.subLock = threading.Lock()
        def sender(client: Registry.Client):
            try:
                client.conn.sendall(msg.encode('utf-8'))
            except:
                self.subLock.acquire()
                self.clients.remove(client)
                self.subLock.release()
        with ThreadPoolExecutor() as executor:
            [executor.submit(sender, client) for client in self.clients]
        self.clLock.release()
        
    def __is_socket_closed__(self,sock: socket.socket) -> bool:
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                return True
        except BlockingIOError:
            return False  # socket is open and reading from it would block
        except ConnectionResetError:
            return True  # socket was closed for some other reason
        except Exception as e:
            self.logger.exception("unexpected exception when checking if a socket is closed")
            return False
        return False
    
    def getIPs(self):
        self.clLock.acquire()
        res = [client.addr[0] for client in self.clients]
        self.clLock.release()
        return res
    
    class Client:
        DEAD = 10
        def __init__(self, conn: socket.socket, addr) -> None:
            self.addr = addr
            self.conn = conn
            self.ticks = 0

        def tick(self) -> bool:
            self.ticks += 1
            
        def reset(self):
            self.ticks = 0
            
        def boom(self) -> bool:
            return Registry.Client.DEAD <= self.ticks