'''
Created on Mar 22, 2019

@author: info
'''

import subprocess

def call(args, input=None):
    """"""
    p=subprocess.Popen(' '.join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdoutput, erroutput) = p.communicate(input)
    
    return p.returncode, stdoutput, erroutput

if __name__ == '__main__':
    ret, out, err = call(['ls', '-l'])
    print ret
    print out
    print err
    print call(['brctl', 'show'])
