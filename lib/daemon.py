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
    def __init__(self, pidfile, **kws):
        """"""
        self.pidfile = pidfile

        self.stdin  = kws.get('stdin', '/dev/null')
        self.stdout = kws.get('stdout', '/dev/null')
        self.stderr = kws.get('stderr', '/dev/null')

    def daemonize(self):
        """"""
        if self.isrun():
            raise RuntimeError('process already running.')

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

#         with open(self.stdin, 'rb', 0) as f:
#             os.dup2(f.fileno(), sys.stdin.fileno())
#         with open(self.stdout, 'ab', 0) as f:
#             os.dup2(f.fileno(), sys.stdout.fileno())
#         with open(self.stderr, 'ab', 0) as f:
#             os.dup2(f.fileno(), sys.stderr.fileno())

        with open(self.pidfile, 'w') as f:
            f.write(str(os.getpid()))

        atexit.register(lambda: os.remove(self.pidfile))

        signal.signal(signal.SIGTERM, self.sigtermHandler)

    @staticmethod
    def sigtermHandler(signo, frame):
        """"""
        raise SystemExit(253)

    def start(self):
        """"""
        try:
            self.daemonize()
        except RuntimeError as e:
            logging.error('RuntimeError {0}'.format(e))
            raise SystemExit(254)

        self.run()

    def stop(self):
        """"""
        try:
            if os.path.exists(self.pidfile):
                with open(self.pidfile) as f:
                    os.kill(int(f.read()), signal.SIGTERM)
        except OSError as e:
            if 'No such process' in str(e) and os.path.exists(self.pidfile): 
                os.remove(self.pidfile)

    def restart(self):
        """"""
        self.stop()
        self.start()

    def run(self):
        """"""
        raise NotImplementedError
    
    def isrun(self):
        """"""
        if os.path.exists(self.pidfile):
            with open(self.pidfile, 'r') as f:
                pid = f.read().strip()
                if pid.isdigit() and os.path.exists('/proc/{0}'.format(pid)):
                    return True

        return False

    def status(self):
        """"""
        if self.isrun():
            return 'running.'

        return 'stopped'