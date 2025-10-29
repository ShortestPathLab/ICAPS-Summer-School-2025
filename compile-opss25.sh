#!/bin/bash

mkdir build

bash ./python/set_track.bash planner

cmake -B build ./ -DPYTHON=true -DCMAKE_BUILD_TYPE=Release
make -C build -j


