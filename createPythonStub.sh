#!/usr/bin/env bash

bash compile.sh

DIR=$(pwd)

export PYTHONPATH=$DIR/build:$PYTHONPATH

stubgen -m MAPF -o ./python