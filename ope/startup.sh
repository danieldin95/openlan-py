#!/bin/bash

#
# 
# cp ./openlan-py/cpe/cpe.service /usr/lib/systemd/system
# 
# systemctl enable ope
# systemctl start  ope
#
curdir=`dirname $0`

cd `dirname $curdir` && { 
  python -m sky.daemon -a start
  python -m ope.daemon -a start
}
