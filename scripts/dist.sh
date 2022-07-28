#!/bin/bash

set -e

dir="dist"

rm -rf $dir

mkdir -p $dir

cp -r bin $dir/bin
cp -r libexec $dir/libexec
cp -r shims $dir/shims
mkdir $dir/var

tar -czf "$dir.tar.gz" $dir/
