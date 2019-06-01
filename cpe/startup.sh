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
OPE="localhost"
ZONE="office" # home/office

curdir=`dirname $0`

brctl addbr br-olan || :

if ip link show dev $ETH; then
  ifconfig $ETH 0
  brctl delif br-olan $ETH || :
  brctl addif br-olan $ETH
fi

if [ "$ZONE" == "office" ]; then
  kill `pidof dhclient` || :
  dhclient br-olan
fi

cd `dirname $curdir` && python -m cpe.daemon -a start
