'''
Created on Feb 16, 2019

@author: Daniel
'''

import socket

class UdpClient(object):
    """"""
    def __init__(self, sock, addr, **kwargs):
        """"""
        self.addr = addr
        self.ipaddr = addr[0]
        self.udport = addr[1]
        self.sock = sock
        self.maxsize = kwargs.get('maxsize', 1422)

    def __hash__(self):
        """"""
        return self.key()
    
    def __eq__(self, other):
        """"""
        return other.key() == self.key()

    def __ne__(self, other):
        """"""
        return other.key() != self.key()

    def __str__(self):
        """"""
        return self.key()

    def sendto(self, data):
        """"""
        data0 = data[:self.maxsize]
        data1 = data[self.maxsize:]

        n = self.sock.sendto(data0, self.addr)
        if n != len(data0):
            raise socket.error(self.STOOSMALL, "send too small %d for %s"%(n, len(data0)))

        if len(data1) > 0:
            self.sendto(data1)

        # sendto successfully.

    def key(self):
        """"""
        return '%s:%s'%(self.ipaddr, self.udport)

class UdpServer(object):
    """"""
    def __init__(self, addr, **kwargs):
        """
        @param addr: ('192.168.1.1', 10001)
        """
        self.addr = addr
        self.maxsize = kwargs.get('maxsize', 1422)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print self.addr
        self.sock.bind(self.addr)

        self.clients = {}

    def recvfrom(self, n=0):
        """"""
        if n == 0:
            n = self.maxsize

        data, addr = self.sock.recvfrom(n)
        uaddr = UdpClient(self.sock, addr, maxsize=self.maxsize)
        if self.clients.get(uaddr.key()) is None:
            self.clients[uaddr.key()] = uaddr
            print self.clients

        return data, uaddr

    def close(self):
        """"""
        self.sock.close()

if __name__ == '__main__':
    import sys

    addr = sys.argv[1]
    ip, port = addr.split(':')
    
    u = UdpServer((ip, int(port)))
    while True:
        d, uaddr = u.recvfrom()
        for caddr in u.clients.values():
            if uaddr != caddr: 
                print 'from ', uaddr , 'to', caddr
                caddr.sendto(d)
    
