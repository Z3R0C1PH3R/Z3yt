#!/bin/bash
progdir=$(cd $(dirname $0); pwd)
exec >YouTube-Z3-logfile.txt 2>&1
cd $progdir/Z3yt
python3 yt.py
