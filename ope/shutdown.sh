#!/bin/bash

curdir=`dirname $0`

cd `dirname $curdir` && python -m ope.daemon -a stop

