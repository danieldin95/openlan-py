#!/bin/bash

#
# NetworkManager on $ETH MUST disable and clear default gw. 
#

curdir=`dirname $0`

cd `dirname $curdir` && python -m cpe.daemon -a stop