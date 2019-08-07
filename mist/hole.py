import time
import socket 
import threading

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.bind(('', 20090))

todest=('180.110.209.235', 13506)
tobroker=('openlan.net', 10080)

def sendto(sock, addr):
    while True:
        time.sleep(1)
        sock.sendto('hello from 151', addr)

def recvfrom(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        print data, addr

t1 = threading.Thread(target=sendto, args=(clientSock,todest))
t2 = threading.Thread(target=recvfrom, args=(clientSock,))
t3 = threading.Thread(target=sendto, args=(clientSock,tobroker))

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()
