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

curdir=`dirname $0`
cpedir=`dirname $curdir`

cd `dirname $cpedir` && python -m cpe.daemon -a start
