#!/bin/bash

set -e 

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
brctl addif br-olan $ETH

kill `pidof dhclient` || :
ifconfig $ETH 0

dhclient br-olan

cd openlan-py
python -m cpe.bridge $OPE &
