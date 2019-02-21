'''
Created on Feb 16, 2019

@author: Daniel
'''

import struct

"""
    0        7        15       23       31
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     Length      |        Reserve    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                Zone                 |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |F|M| C |           Identify          |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

      Length(16) : The length of this message.
     Reserve(16) : Reserve bits.
        Zone(32) : OpenLan Zone Value.  
            F(1) : Flagment bit.
            M(1) : More Flagment bit.
            C(4) : Offset Index.
    Identify(24) : The Identify of this message.
    
"""
class UdpMesg(object):
    """
    """
    ETHSIZE  = 14
    HSIZE    = 12
    MSIZE   = 1460 # 1500-20-8-12
    identify = 0

    @classmethod
    def genid(cls):
        """"""
        i = cls.identify

        cls.identify += 1
        cls.identify &= 0xffFFff

        return i 

    def __init__(self, pkt, zone=0, **kwargs):
        """"""
        self.pkt = pkt
        self.zone = zone
        self.reserve = kwargs.get('reserve', 0)
        self.maxsize = kwargs.get('maxsize', self.MSIZE)
        self.id = self.__class__.genid()

    def pack(self):
        """"""
        payloads = []
        if len(self.pkt) <= self.MSIZE:
            payloads.append(self.pkt)
        else:
            eth = self.pkt[:self.ETHSIZE]
            pkt = self.pkt[self.ETHSIZE:]
            truesize = self.MSIZE - self.ETHSIZE

            while len(pkt) > 0:
                payloads.append(eth+pkt[:truesize])
                pkt = pkt[truesize:]
 
        psize = len(payloads)
        if psize > 0:
            fbit = True
        else:
            fbit = False

        frags = []
        # process fragment messages.
        for i in range(1, psize):
            p = payloads[i]
            
            size = len(p) + self.HSIZE
            idx = self.id
            idx |= 0xc0000000 # F|M
            idx |= (i & 0x3f) << 24

            d = struct.pack('!HHII', size, self.reserve, self.zone, idx)

            frags.append(d+p)

        # process END messages.
        p = payloads[-1]
        size = len(p) + self.HSIZE
        idx = self.id
        if fbit:
            idx |= 0x80000000 # F
        idx |= (psize & 0x3f) << 24

        d = struct.pack('!HHII', size, self.reserve, self.zone, idx)

        frags.append(d+p)

        return frags
            
class UdpMesgBin(object):
    """"""
    def __init__(self, data, **kwargs):
        """"""
        self.data = data

    def unpack(self):
        """"""
