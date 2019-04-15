'''
Created on Feb 23, 2019

@author: Daniel
'''

import os
import sys
import signal
import logging

from multiprocessing import Lock

lock = Lock()

class Daemon(object):
    """"""
    @classmethod
    def daemonize(cls, pidpath, **kws):
        """"""
        if cls.isrun(pidpath):
            raise RuntimeError('process already running.')

        stdin   = kws.get('stdin',  '/dev/null')
        stdout  = kws.get('stdout', '/var/log/stdout')
        stderr  = kws.get('stderr', '/var/log/stderr')
        
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #1: {0} {1}'.format(e.errno, e.strerror))

        os.chdir('/')
        os.setsid()
        os.umask(0o22)

        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #2: {0} {1}'.format(e.errno, e.strerror))

        sys.stdout.flush()
        sys.stderr.flush()

        with open(stdin, 'rb', 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(stdout, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(stderr, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        cls.savePid(pidpath)

        signal.signal(signal.SIGTERM, cls.sigtermHandler)

    @classmethod
    def removePid(cls, pidpath):
        """"""
        pidfile = '{0}/{1}'.format(pidpath, os.getpid())
        with lock:
            if os.path.exists(pidfile):
                os.remove(pidfile)

    @classmethod
    def removeAllPid(cls, pidpath):
        """"""
        with lock:
            if os.path.exists(pidpath):
                for pid in os.listdir(pidpath):
                    os.remove('{0}/{1}'.format(pidpath, pid))
    
                try:
                    os.rmdir(pidpath)
                except OSError as e:
                    logging.warn(e)

    @classmethod
    def savePid(cls, pidpath):
        """"""
        with lock:
            if not os.path.exists(pidpath):
                os.mkdir(pidpath)

            pid = os.getpid()
            with open('{0}/{1}'.format(pidpath, pid), 'w') as f:
                f.write(str(pid))

    @classmethod
    def sigtermHandler(cls, signo, frame):
        """"""
        raise SystemExit(253)

    @classmethod
    def start(cls, pidpath, **kws):
        """"""
        try:
            cls.daemonize(pidpath, **kws)
        except RuntimeError as e:
            logging.error('RuntimeError {0}'.format(e))
            raise SystemExit(254)

        cls.run(pidpath, **kws)

    @classmethod
    def stop(cls, pidpath):
        """"""
        if os.path.exists(pidpath):
            for pid in os.listdir(pidpath):
                if not pid.isdigit():
                    continue

                try:
                    os.kill(int(pid), signal.SIGTERM)
                except OSError as e:
                    logging.warn(e)
                    continue

        cls.removeAllPid(pidpath)

    @classmethod
    def restart(cls, pidpath, **kws):
        """"""
        cls.stop(pidpath)
        cls.start(pidpath, **kws)

    @classmethod
    def run(cls, **kws):
        """"""
        raise NotImplementedError

    @classmethod
    def isrun(cls, pidpath):
        """"""
        if os.path.exists(pidpath):
            for pid in os.listdir(pidpath):
                if not pid.isdigit():
                    continue
                if os.path.exists('/proc/{0}'.format(pid)):
                    return True

        return False

    @classmethod
    def status(cls, pidpath):
        """"""
        stats = []

        if os.path.exists(pidpath):
            for pid in os.listdir(pidpath):
                if not pid.isdigit():
                    continue

                if os.path.exists('/proc/{0}'.format(pid)):
                    stats.append('{0} running'.format(pid))
                else:
                    stats.append('{0} stopped'.format(pid))

            return '\n'.join(stats)

        return 'stopped'
