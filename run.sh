#!/bin/sh

echo 'sh: mount ./tmp'
sudo mount -t tmpfs -o size=256m /dev/shm ./tmp

echo 'sh: start'
cd bin
./AeroMixer.py
cd ..

echo 'sh: umount ./tmp'
sudo umount ./tmp
