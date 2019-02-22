import struct

class UdpMesg(object):
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
    MSIZE = 1460 # 1500-20-8-12

    def __init__(self, **kwargs):
        """"""
        self.maxsize = kwargs.get('maxsize', self.MSIZE)
