'''
Created on Feb 16, 2019

@author: Daniel
'''

import socket  

class UdpClient(object):
    """"""
    STOOSMALL = 90001
    RTOOSMALL = 80001
    
    def __init__(self, addr, **kwargs):
        """
        @param addr: ('192.168.1.1', 10001) 
        """
        self.addr    = addr
        self.maxsize = kwargs.get('maxsize', 1422) # 1500-20-8

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.hello()

    def hello(self):
        """"""
        self.sendto("hello")

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

    def recvfrom(self, n, waitall=True):
        """"""
        flags = 0
        if waitall:
            flags = socket.MSG_WAITALL

        return self.sock.recvfrom(n, flags)
    
    def close(self):
        """"""
        self.sock.close()

if __name__ == '__main__':
    import sys
    import time

    addr = sys.argv[1]
    ip, port = addr.split(':')
    
    u = UdpClient((ip, int(port)))
    u.hello()

    while True:
        d = '%s: hi' % id(u)
        s = 1422 - len(d)
        d = d + 'a'*(s-1)+'b'+'c'*24

        print len(d)

        u.sendto(d)
        try:
            d, a = u.recvfrom(u.maxsize, False)
            print a, len(d), repr(d)
        except socket.error as e:
            #print e
            if e.errno == 11:
                #time.sleep(1)
                pass

