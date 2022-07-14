#!/bin/bash

set -e

dir="dist"

rm -rf $dir

mkdir -p $dir

cp -r libexec $dir/libexec
cp -r bin $dir/bin

tar -czf "$dir.tar.gz" $dir/
