#!/bin/bash

"""
NetworkManager on $ETH MUST disable and clear default gw. 
"""

ETH="ens192"
OPE="openlan.net"
curdir=`dirname $0`

cd curdir

brctl addbr br-olan || :
brctl delif br-olan $ETH || :
brctl addif br-olan $ETH

ifconfig $ETH 0

dhclient br-olan

python -m cpe.daemon -a start
