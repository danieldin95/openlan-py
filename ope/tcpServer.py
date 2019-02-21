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
    
    def __repr__(self):
        """"""
        return '{ fd: %s, addr: %s}' % (self.fd.fileno(), self.addr)

    def close(self):
        """"""
        if self.fd is None:
            return
 
        try:
            self.fd.shutdown(2)
            self.fd.close()
        except socket.error as e:
            print e
 
        del self.fd
        self.fd = None

     def __del__(self):
        """"""
        self.close()
 
     def isok(self):
        """"""
        return self.fd is not None

    def recvn(self, n):
        """"""
        buf = ''
        left = n
        while left > 0:
            d = self.fd.recv(left)
            if len(d) == 0:
                return buf 

            left -= len(d)
            buf += d

        return buf
    
    def sendn(self, d):
        """"""
        n = 0
        while n < len(d):
            d = d[n:]
            n = self.fd.send(d)
            if n == 0:
                return False
   
        return True

class TcpMesg(object):
    """"""
    def __init__(self, conn, data):
        """"""
        self.conn = conn
        self.data = data

    def __str__(self):
        """"""
        return '{ conn: %s, data: %s }' % (self.conn, repr(self.data))

    def __repr__(self):
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
        self.idleTimeout = 5
        self.idleFunc = self.idleDefault
        
        self.DEBUG = kws.get('DEBUG', False)

    def idleDefault(self):
        """"""
        print "idle..."

    def accept(self):
        """"""
        fd, addrs = self.s.accept()
        print 'accept from %s:%s'%(addrs[0], addrs[1])

        conn = TcpConn(fd, addrs)
        self.conns[fd] = conn

        print self.conns

    def removeConn(self, fd):
        """"""
        if fd in self.conns:
            conn = self.conns.pop(fd)
            conn.close()

    def recv(self, conn, s=1024):
        """"""
        if self.DEBUG:
            print "receive size: %s"%s
        try:
            d = conn.recvn(s)
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
            try:
                rs, _, es = select.select(fds, [], fds, self.idleTimeout)
            except select.error as e:
                print e
                break

            if len(rs) == 0 and len(es) == 0:
                self.idleFunc()
                continue

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

        self.close()

    def close(self):
        """"""
        if self.conns:
            del self.conns
            self.conns = None

        if self.s is None:
            return

        try:
            self.s.shutdown(2)
            self.s.close()
        except socket.error as e:
            print e

        del self.s
        self.s = None
