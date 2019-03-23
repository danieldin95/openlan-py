'''
Created on Mar 22, 2019

@author: info
'''

import struct

"""
    0       7        15       23       31
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
    +     0xFFFF     |      Length     +
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
    + O |        SystemID              +
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
    +    Reserve     |      Zone       +
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
    +         Ethernet Frame           +
    +-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+
"""
class TcpMesg(object):
    """"""
    MAGIC  = '\xff\xff' 
    HLDLEN = 8

    def __init__(self, sysid, zone=0, **kws):
        """"""
        self.sysid   = sysid
        self.zone    = zone
        self.reserve = kws.get('reserve', 0)
        self.length  = kws.get('length', 0)
        self.data    = kws.get('data', '')
        self.private = kws.get('private', None)

        if self.length == 0:
            self.length = self.HLDLEN+len(self.data)

    def pack(self):
        """"""
        rawdata = self.MAGIC
        rawdata += struct.pack('!H', self.length)
        rawdata += struct.pack('!I', self.sysid)
        rawdata += struct.pack('!H', self.reserve)
        rawdata += struct.pack('!H', self.zone)

        return rawdata+self.data

    @classmethod
    def unpack(cls, header):
        """"""
        length = struct.unpack('!H', header[2:4])[0]
        sysid  = struct.unpack('!I', header[4:8])[0]
        reserve= struct.unpack('!H', header[8:10])[0]
        zone   = struct.unpack('!H', header[10:12])[0]
        data   = header[12:]

        return cls(sysid, zone, length=length, data=data, reserve=reserve)
    
    def __str__(self):
        """"""
        return '{sysid: %04x, zone:%02x, length: %d, frame:%s}' % (self.sysid, self.zone, self.length, repr(self.data))
