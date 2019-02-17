'''
Created on Feb 16, 2019

@author: info
'''

import socket
import select

class TcpConn(object):
    """"""
    def __init__(self, fd, addr):
        """"""
        self.fd = fd
        self.addr = addr
    
    def __str__(self):
        """"""
        return '{ fd: %s, addr: %s}' % (self.fd.fileno(), self.addr)

class TcpMesg(object):
    """"""
    def __init__(self, conn, data):
        """"""
        self.conn = conn
        self.data = data

    def __str__(self):
        """"""
        return '{ conn: %s, data: %s }' % (self.conn, repr(self.data))

class TcpServer(object):
    """"""

    def __init__(self, port=10001, **kws):
        """"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('0.0.0.0', port))

        self.s.listen(32)
        self.conns = {}
        self.onMsg = None
        self.idleTimeout = 0.5
        self.idleFunc = self.idleDefault
        
        self.DEBUG = kws.get('DEBUG', False)

    def idleDefault(self):
        """"""
        pass

    def accept(self):
        """"""
        fd, addrs = self.s.accept()
        print 'accept from %s:%s'%(addrs[0], addrs[1])

        conn = TcpConn(fd, addrs)
        self.conns[fd] = conn

    def removeConn(self, fd):
        """"""
        if fd in self.conns:
            self.conns.pop(fd)

    def recvn(self, s, n):
        """"""
        buf = s.recv(n)
        left = n - len(buf)
        while left > 0:
            d = s.recv(left)
            if len(d) == 0:
                return buf 

            left -= len(d)
            buf += d

        return buf

    def recv(self, conn, s=1024):
        """"""
        if self.DEBUG:
            print "receive size: %s"%s
        try:
            d = self.recvn(conn.fd, s)
        except socket.error as e:
            print "receive data with %s"%e
            self.removeConn(conn.fd)
            return []
    
        if not d:
            self.removeConn(conn.fd)
        else:
            if self.DEBUG:
                print "receive data: %s"%repr(d)

        return d

    def getfds(self):
        """"""
        fds = [self.s]
        for fd in self.conns.keys():
            fds.append(fd)

        return fds

    def loop(self):
        """"""
        while True:
            fds = self.getfds()

            rs, ws, es = select.select(fds, [], fds, self.idleTimeout)
            if len(rs) == 0 and len(es) == 0 and len(ws) == 0:
                self.idleFunc()

            for r in rs:
                if r is self.s:
                    self.accept()
                else:
                    conn = self.conns.get(r)
                    if conn:
                        self.recv(conn)
    
            for e in es:
                if e is self.s:
                    raise SystemError('server has exception')
                else:
                    print "socket %s exit"%e
                    self.removeConn(e)

    def close(self):
        """"""  
        self.s.close()
