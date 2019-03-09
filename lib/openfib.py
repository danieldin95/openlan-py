
import time
import logging

from threading import thread
from threading import Event

from lib.rwlock import RWLock
from lib.ethernet import Ethernet

class OpenFibConn(object):
    """"""
    def __init__(self):
        """"""

    def fd(self):
        """"""
        raise NotImplemented

    def uptime(self):
        """"""
        raise NotImplemented

    @property
    def addrs(self):
        """"""
        raise NotImplemented

class OpenFibEnt(object):
    """"""
    def __init__(self, conn, ethdst, **kws):
        """"""
        self.conn = conn
        self.ethdst  = ethdst
        self.createTime = time.time()
        self.updateTime = time.time()
        self.aging = kws.get('aging', 300)

    def update(self, conn=None):
        """"""
        if conn is not None and self.conn is not conn:
            self.conn = conn

        self.updateTime = time.time()

    def upTime(self):
        """"""
        if self.isExpire():
            return 0

        return round(time.time() - self.createTime, 2)

    def isExpire(self):
        """"""
        if (time.time() - self.updateTime > self.aging or
            not self.conn.isok()):
            return True

        return False

    def __str__(self):
        """"""
        return '{0} {1} {2}'.format(Ethernet.addr2Str(self.ethdst), 
                                    self.conn.fd(), self.upTime())

class OpenFibMgr(object):
    """"""
    def __init__(self, maxsize=65535):
        """"""
        self.maxsize = maxsize
        self.fib = {}
        self.fibrwl = RWLock()

    def learn(self, conn, eth):
        """
        @param conn: a OpenFibConn object 
        """
        entry = self.getEntry(eth.src)
        if entry is None:
            if len(self.fib) > self.maxsize:
                logging.error('source learning reached max size {0}'
                              .format(self.maxsize))
                # TODO archive fib aging 
                return
            
            entry = OpenFibEnt(conn, eth.src)
            logging.info('source learning {0}'.format(entry))

            with self.fibrwl.writer_lock:
                self.fib[eth.src] = entry
        else:
            entry.update(conn)

    def getEntry(self, ethaddr):
        """"""
        with self.fibrwl.reader_lock:
            fib = self.fib.get(ethaddr)

        return fib

    def delEntry(self, ethaddr):
        """"""
        with self.fibrwl.writer_lock:
            if ethaddr in self.fib:
                self.fib.pop(ethaddr)

    def listEntry(self):
        """"""
        with self.fibrwl.reader_lock:
            for fib in self.fib.values():
                yield fib
                
class OpenFibJob(thread):
    """"""
    def __init__(self, interval=30):
        """"""
        super(OpenFibJob, self).__init__()
        self.fibs = OpenFibMgr()
        self._interval = interval
        self._lasttime = time.time()
        self._running = True
        self._event = Event() 

    def run(self):
        """"""
        while self._running:
            self._event.wait(self.interval)
            self._event.clear()
            expired = []
            for fib in self.fibs.listEntry():
                if fib.isExpire():
                    expired.append(fib.ethdst)

            for ex in expired:
                self.fibs.delEntry(ex)

    def stop(self):
        """"""
        self._running = False
        self._event.set()
