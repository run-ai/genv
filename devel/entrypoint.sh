#!/bin/bash

set -e

GENV_ROOT=${GENV_ROOT:-$HOME/genv}

if ! [ -d "$GENV_ROOT" ]; then
  echo "ERROR: Genv directory not mounted properly"
  exit 1
fi

devel_shims_path="$GENV_ROOT/devel/shims"

shopt -s nullglob

for shim_path in "$devel_shims_path/"*; do
  shim="${shim_path##$devel_shims_path/}"

  if ! command -v $shim &> /dev/null
  then
    ln -s "$shim_path" "/usr/bin/$shim"
  fi
done

pip install -e $GENV_ROOT > /dev/null

cat << EOT >> "$HOME/.bashrc"
eval "\$(genv shell --init)"
EOT

( exec "$@" )
