#!/bin/bash

#
# NetworkManager on $ETH MUST disable and clear default gw. 
#
# 
# cp ./openlan-py/cpe/cpe.service /usr/lib/systemd/system
# 
# systemctl enable cpe
# systemctl start  cpe
#

ETH="ens192"
OPE="openlan.net"
curdir=`dirname $0`

brctl addbr br-olan || :
brctl delif br-olan $ETH || :
brctl addif br-olan $ETH

ifconfig $ETH 0

kill `pidof dhclient` || :
dhclient br-olan

cd `dirname $curdir` && python -m cpe.daemon -a start
