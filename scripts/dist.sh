#!/bin/bash

set -e

dir="dist"

rm -rf $dir

mkdir -p $dir

cp -r bin $dir/bin
cp -r exe $dir/exe
cp -r libexec $dir/libexec
cp -r py $dir/py
cp -r shims $dir/shims

tar -czf "$dir.tar.gz" $dir/
