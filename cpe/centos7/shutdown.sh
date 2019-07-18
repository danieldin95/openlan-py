#!/bin/bash

curdir=`dirname $0`
cpedir=`dirname $curdir`

cd `dirname $cpedir` && python -m cpe.daemon -a stop
