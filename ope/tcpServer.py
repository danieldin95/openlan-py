'''
Created on Feb 16, 2019

@author: info
'''

import socket
import select
import logging

class TcpConn(object):
    """"""
    def __init__(self, sock, addr):
        """"""
        self.sock = sock
        self.addr = addr
        self.rxpkt = 0
        self.txpkt = 0
        self.txdrop = 0

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
 
        del self.sock
        self.sock = None

    def __del__(self):
        """"""
        self.close()
 
    def isok(self):
        """"""
        return self.sock is not None

    def recvn(self, n):
        """
        """
        buf = ''
        left = n
        while left > 0:
            try:
                d = self.sock.recv(left)
            except socket.error as e:
                if e.errno == 11:
                    continue

            if len(d) == 0:
                raise socket.error(90002, 'receive zero message')

            left -= len(d)
            buf += d

        return buf

    def sendn(self, d):
        """
        TODO support Queue.
        """
        n = 0
        while n < len(d):
            d = d[n:]
            n = self.sock.send(d)
            if n == 0:
                raise socket.error(90002, 'send zero message')

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

        self.sock.setblocking(0)

    def idleDefault(self):
        """"""
        logging.debug("idle...")

    def accept(self):
        """"""
        sock, addrs = self.sock.accept()
        logging.info('accept from %s:%s', addrs[0], addrs[1])

        sock.setblocking(0)
        
        self.conns[sock] = TcpConn(sock, addrs)

        logging.info(self.conns)

    def removeConn(self, sock):
        """"""
        if sock in self.conns:
            conn = self.conns.pop(sock)
            conn.close()

        logging.info(self.conns)

    def recv(self, conn, s=1024):
        """"""
        logging.debug("receive size: %s", s)
        try:
            d = conn.recvn(s)
        except socket.error as e:
            logging.error("receive data with %s on %s", e, conn)
            self.removeConn(conn.sock)
            return []

        if not d:
            self.removeConn(conn.sock)
        else:
            logging.debug("receive data: %s", repr(d))

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

            del self.conns
            self.conns = None

        if self.sock is None:
            return

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            logging.warning('shutdown %s', self.sock.fileno())
        except socket.error as e:
            logging.error('%s', e)

        del self.sock
        self.sock = None
