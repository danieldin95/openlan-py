'''
Created on Feb 16, 2019

@author: info
'''

import socket
import select
import logging
import Queue
import time

ERRZMSG = 9000 # zero message
ERRSBIG = 9001 # size big
ERRSNOM = 9002 # size not match
ERRDNOR = 9003 # data not right

class TcpConn(object):
    """"""
    def __init__(self, sock, addr, **kws):
        """"""
        self.sock = sock
        self.addr = addr
        self.txbuf = ''
        self.txq   = Queue.Queue()

        self.maxsize = kws.get('maxsize', 1514)
        self.minsize = kws.get('minsize', 15)
        
        self.lastsenderr = 0
        self.lastrecverr = 0

    def txput(self, d):
        """"""
        if d is None:
            return

        if self.txq.qsize() >= self.maxsize:
            logging.warning('%s dropping %s', self, d)
            return 
        else:
            logging.debug('%s queue %s', self, repr(d))
            self.txq.put(d)

    def txget(self):
        """"""
        if not self.txq.empty():
            return self.txq.get()
        
        return None

    def __str__(self):
        """"""
        return self.__repr__()
    
    def __repr__(self):
        """"""
        if self.sock:
            return '{sock:%s,addr:%s}' %(self.sock.fileno(), self.addr)
        
        return "{addr:%s}"%str(self.addr)

    def close(self):
        """"""
        if self.sock is None:
            return
 
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            logging.warning('shutdown %s', self.sock.fileno())
        except socket.error as e:
            logging.error('%s', e)
 
        self.sock = None
 
    def isok(self):
        """"""
        return self.sock is not None

    def recvn(self, n):
        """"""
        buf = ''
        left = n
        while left > 0:
            d = ''
            try:
                d = self.sock.recv(left)
                self.lastrecverr = 0
            except socket.error as e:
                logging.debug("send %s with %s", self, e)
                if e.errno == 11:
                    if self.lastrecverr == 0:
                        self.lastrecverr = time.time()
                        
                    if time.time() - self.lastrecverr > 300:
                        logging.warn("%s receive errno 11 during 300s", self)
                        self.lastrecverr = 0
                    
                    continue

            if len(d) == 0:
                raise socket.error(ERRZMSG, 'receive zero message')

            left -= len(d)
            buf += d

        return buf

    def recvall(self):
        """"""
        raise NotImplementedError

    def sendn(self, d):
        """"""
        n = 0
        c = 0
        while n < len(d):
            d = d[n:]
            try:
                n = self.sock.send(d)
                c += n
                self.lastsenderr = 0
            except socket.error as e:
                logging.debug("send %s with %s", self, e)
                if e.errno == 11:
                    if self.lastsenderr == 0:
                        self.lastsenderr = time.time()
                    
                    if time.time() - self.lastsenderr > 300:
                        logging.warn("%s socket errno 11 during 300s", self)
                        self.lastsenderr = 0

                    break

            if n == 0:
                raise socket.error(ERRZMSG, 'send zero message')

        return c

    def sendone(self, d=None):
        """"""
        buf = None
        
        if self.txbuf != '':
            buf = self.txbuf
            self.txput(d)
        else:
            buf = self.txget()

        if buf is None:
            buf = d
        else:
            self.txput(d)

        if buf is None:
            return 

        n = self.sendn(buf)
        if n != len(buf):
            self.txbuf = buf[n:]
            return

        self.txbuf = ''

    def sendall(self, d):
        """"""
        raise NotImplementedError

class TcpMesg(object):
    """"""
    def __init__(self, conn, data):
        """"""
        self.conn = conn
        self.data = data

    def __str__(self):
        """"""
        return self.__repr__()

    def __repr__(self):
        """"""
        return '{conn:%s,data:%s}' %(self.conn, repr(self.data))

class TcpServer(object):
    """"""

    def __init__(self, port=10001, **kws):
        """"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', port))

        self.sock.listen(32)
        self.conns = {}
        self.onMsg = None
        self.idleTimeout = 5
        self.idleFunc = self.idleDefault
        self.maxsize = kws.get('maxsize', 1514)
        self.minsize = kws.get('minsize', 15)

        self.sock.setblocking(0)
        self.conncls = kws.get('tcpConn', TcpConn)

    def idleDefault(self):
        """"""
        logging.debug("idle...")

    def accept(self):
        """"""
        sock, addrs = self.sock.accept()
        logging.info('accept from %s:%s', addrs[0], addrs[1])

        sock.setblocking(0)
        
        self.conns[sock] = self.conncls(sock, addrs, maxsize=self.maxsize)

        logging.info(self.conns)

    def removeConn(self, sock):
        """"""
        if sock in self.conns:
            conn = self.conns.pop(sock)
            conn.close()

        logging.info(self.conns)

    def recv(self, conn):
        """"""
        try:
            d = conn.recvall()
        except socket.error as e:
            logging.error("receive data with %s on %s", e, conn)
            self.removeConn(conn.sock)
            return None

        logging.debug("receive data %s: %s", conn, repr(d))

        return d

    def getsocks(self):
        """"""
        socks = [self.sock]
        for sock in self.conns.keys():
            socks.append(sock)

        return socks

    def loop(self):
        """"""
        while True:
            socks = self.getsocks()
            try:
                rs, _, es = select.select(socks, [], socks, self.idleTimeout)
            except select.error as e:
                logging.error('%s', e)
                break

            if len(rs) == 0 and len(es) == 0:
                self.idleFunc()
                continue

            for r in rs:
                if r is self.sock:
                    self.accept()
                else:
                    conn = self.conns.get(r)
                    if conn:
                        self.recv(conn)

            for e in es:
                if e is self.sock:
                    raise SystemError('server has exception')
                else:
                    logging.error("socket %s exit", e)
                    self.removeConn(e)

        self.close()

    def close(self):
        """"""
        if self.conns:
            for conn in self.conns.values():
                conn.close()

            self.conns = None

        if self.sock is None:
            return

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            logging.warning('shutdown %s', self.sock.fileno())
        except socket.error as e:
            logging.error('%s', e)

        self.sock = None
