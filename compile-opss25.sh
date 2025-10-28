#!/bin/bash

mkdir build

cmake -B build ./ -DPYTHON=true -DCMAKE_BUILD_TYPE=Release
make -C build -j


