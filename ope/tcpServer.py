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
    def __init__(self, port=10001):
        """"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('0.0.0.0', port))

        self.s.listen(32)
        self.conns = {}
        self.onMsg = None
        self.idle_timeout = 0.5
        self.idleFunc = self.idleDefault

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

    def recv(self, conn, s=1024):
        """"""
        print "receive size: %s"%s
        d = conn.fd.recv(s)
        if not d:
            self.removeConn(conn.fd)
        else:
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

            rs, ws, es = select.select(fds, [], fds, self.idle_timeout)
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
