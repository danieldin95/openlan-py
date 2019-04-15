'''
Created on Feb 23, 2019

@author: info
'''

import os
import sys
import atexit
import signal
import logging

class Daemon(object):
    """"""
    @classmethod
    def daemonize(cls, pidfile, **kws):
        """"""
        if cls.isrun(pidfile):
            raise RuntimeError('process already running.')

        stdin   = kws.get('stdin',  '/dev/null')
        stdout  = kws.get('stdout', '/var/log/stdout')
        stderr  = kws.get('stderr', '/var/log/stderr')

        # First fork.
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError('fork #1: {0} {1}'.format(e.errno, e.strerror))

        os.chdir('/')
        os.setsid()
        os.umask(0o22)

        # Second fork.
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

        with open(pidfile, 'w') as f:
            f.write(str(os.getpid()))

        atexit.register(lambda: os.remove(pidfile))

        signal.signal(signal.SIGTERM, cls.sigtermHandler)

    @classmethod
    def sigtermHandler(cls, signo, frame):
        """"""
        raise SystemExit(253)

    @classmethod
    def start(cls, pidfile, **kws):
        """"""
        try:
            cls.daemonize(pidfile, **kws)
        except RuntimeError as e:
            logging.error('RuntimeError {0}'.format(e))
            raise SystemExit(254)

        cls.run(**kws)

    @classmethod
    def stop(cls, pidfile):
        """"""
        try:
            if os.path.exists(pidfile):
                with open(pidfile) as f:
                    pid = int(f.read())
                    os.kill(pid, signal.SIGTERM)
                    if cls.isrun(pidfile):
                        os.kill(pid, signal.SIGKILL)
        except OSError as e:
            if 'No such process' in str(e) and os.path.exists(pidfile): 
                os.remove(pidfile)

    @classmethod
    def restart(cls, pidfile, **kws):
        """"""
        cls.stop(pidfile)
        cls.start(pidfile, **kws)

    @classmethod
    def run(cls, **kws):
        """"""
        raise NotImplementedError
    
    @classmethod
    def isrun(cls, pidfile):
        """"""
        if os.path.exists(pidfile):
            with open(pidfile, 'r') as f:
                pid = f.read().strip()
                if pid.isdigit() and os.path.exists('/proc/{0}'.format(pid)):
                    return True

        return False

    @classmethod
    def status(cls, pidfile):
        """"""
        if cls.isrun(pidfile):
            return 'running.'

        return 'stopped'
