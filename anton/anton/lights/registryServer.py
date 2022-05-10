import socket
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Type

class RegistryServer:
    class Client:
        DEAD = 10
        def __init__(self, conn: socket.socket, addr) -> None:
            self.addr = addr
            self.conn = conn
            self.ticks = 0
            
        def __del__(self):
            self.conn.close()

        def tick(self) -> bool:
            self.ticks += 1
            
        def reset(self):
            self.ticks = 0
            
        def dead(self) -> bool:
            return RegistryServer.Client.DEAD <= self.ticks
        
    HEARTBEAT = 60
    def __init__(self, host:str, tcpPort: int, udpPort: int, clientClass: Type[Client] = Client) -> None:
        self.__clients = set()
        self.__clLock = threading.Lock()
        threading.Thread(target=self.__registration__, args=(host, tcpPort,)).start()
        threading.Thread(target=self.__heartbeat__, args=()).start()
        self.__logger = logging.getLogger(__name__)
        self.__udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__clientClass = clientClass
        self.__udpPort = udpPort

    def broadcast(self, msg:bytes):
        self.__clLock.acquire()
        self.subLock = threading.Lock()
        newClients = self.__clients.copy()
        def sender(client: RegistryServer.Client):
            try:
                client.conn.sendall(msg)
            except socket.error:
                self.subLock.acquire()
                newClients.remove(client)
                self.subLock.release()
        [sender(client) for client in self.__clients]
        self.__clients = newClients
        self.__clLock.release()
    
    def send(self, msg:bytes):
        for ip in self.__get_ips__():
            try:
                self.__udpSock.sendto(msg,(ip, self.__udpPort))
            except socket.error:
                continue
        
    def __registration__(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            while True:
                # establish connection with client
                c, addr = s.accept()
                
                # lock acquired by client
                self.__clLock.acquire()
                self.__clients.add(self.__clientClass(c, addr))
                self.__clLock.release()
                
    def __heartbeat__(self):
        def check_conn(client: RegistryServer.Client):
            if self.is_socket_closed(client.conn):
                client.tick()
            else:
                client.reset()
                
        while True:
            self.__clLock.acquire()
                    
            with ThreadPoolExecutor() as executor:
                [executor.submit(check_conn, client) for client in self.__clients]
            
            client: RegistryServer.Client
            new_clients = self.__clients.copy()
            for client in self.__clients:
                if client.dead():
                    client.conn.close()
                    new_clients.remove(client)
                    
            self.__clients = new_clients
            self.__clLock.release()
            time.sleep(RegistryServer.HEARTBEAT)

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
            self.__logger.exception("unexpected exception when checking if a socket is closed")
            return False
        return False
    
    def __get_ips__(self):
        self.__clLock.acquire()
        res = [client.addr[0] for client in self.__clients]
        self.__clLock.release()
        return res

if __name__ == "__main__":
    test = RegistryServer("",5050, 5020)
    while True:
        test.broadcast(input().encode('utf-8'))