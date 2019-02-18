#!/bin/bash

set -e 

"""
NetworkManager on $ETH MUST disable and clear default gw. 
"""

ETH=$1
if [ "$ETH" == "" ]; then
  echo "$0 <office-nic> <ope-address>"
  exit 0
fi

OPE=$2
if [ "$OPE" == "" ]; then
  OPE="openlan.net"
fi

brctl addbr br-olan || :
brctl delif br-olan $ETH || :
brctl addif br-olan $ETH

ifconfig $ETH 0

dhclient br-olan

python -m cpe.bridge $OPE &
