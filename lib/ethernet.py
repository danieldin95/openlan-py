'''
Created on Feb 27, 2019

@author: Daniel
'''

import struct

class Ethernet(object):
    """"""
    def __init__(self, data):
        """"""
        self.dst = data[0:6]
        self.src = data[6:12]

        self.proto = struct.unpack('!H', data[12:14])

    @classmethod
    def isBrocast(cls, ethaddr):
        """"""
        if ord(ethaddr[0]) & 0x01:
            return True

        return False
    
    @classmethod
    def addr2Str(cls, ethaddr):
        """"""
        addrs = []
        for addr in ethaddr:
            addrs.append('%02x'%(ord(addr)))

        return ':'.join(addrs)