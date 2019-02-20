#!/bin/bash

curdir=`dirname $0`

cd `dirname $curdir` && python -m cpe.daemon -a stop