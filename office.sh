#!/bin/bash

set -e 

ETH="ens192"
OPE="144.48.6.219"

brctl addbr br-olan || exit
brctl addif br-olan $ETH

ifconfig $ETH 0

kill `pidof dhclient` || exit
dhclient br-olan

cd openlan-py
python -m cpe.bridge $OPE &
